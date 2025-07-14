from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pdfplumber
import os
import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
import pickle
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variáveis globais
PDF_PATH = 'Roteiro-de-Dsispensacao-Hanseniase-F.docx.pdf'
pdf_text = ""
pdf_chunks = []
qa_pipeline = None
response_cache = {}
config = {}

def load_config():
    """Carrega configuração otimizada"""
    global config
    
    # Configuração padrão
    default_config = {
        "chunk_size": 2000,
        "overlap": 200,
        "max_answer_length": 200,
        "confidence_threshold": 0.3,
        "use_semantic_search": False,
        "use_caching": True,
        "model_name": "deepset/roberta-base-squad2",
        "cache_file": "response_cache.pkl"
    }
    
    # Tentar carregar configuração otimizada
    if os.path.exists("optimized_config.json"):
        try:
            with open("optimized_config.json", "r", encoding="utf-8") as f:
                optimized_config = json.load(f)
                config = {**default_config, **optimized_config}
                logger.info("Configuração otimizada carregada")
        except Exception as e:
            logger.warning(f"Erro ao carregar configuração otimizada: {e}")
            config = default_config
    else:
        config = default_config
    
    logger.info(f"Configuração: {config}")

def analyze_pdf_complexity(text: str) -> Dict:
    """Analisa a complexidade do PDF e ajusta configuração"""
    total_chars = len(text)
    total_words = len(text.split())
    sentences = re.split(r'[.!?]+', text)
    avg_words_per_sentence = total_words / len(sentences) if sentences else 0
    
    # Ajustar configuração baseado no tamanho
    if total_chars > 100000:  # PDF muito grande
        config.update({
            "chunk_size": 1500,
            "overlap": 300,
            "use_semantic_search": True,
            "max_answer_length": 150,
            "confidence_threshold": 0.4
        })
        complexity_level = "HIGH"
    elif total_chars > 50000:  # PDF médio
        config.update({
            "chunk_size": 2000,
            "overlap": 200,
            "use_caching": True,
            "confidence_threshold": 0.35
        })
        complexity_level = "MEDIUM"
    else:  # PDF pequeno
        complexity_level = "LOW"
    
    return {
        "total_chars": total_chars,
        "total_words": total_words,
        "avg_words_per_sentence": round(avg_words_per_sentence, 2),
        "complexity_level": complexity_level,
        "estimated_chunks": (total_chars // config["chunk_size"]) + 1
    }

def extract_pdf_text(pdf_path: str) -> str:
    """Extrai texto do PDF com tratamento de erros"""
    global pdf_text
    
    try:
        if not os.path.exists(pdf_path):
            logger.error(f"PDF não encontrado: {pdf_path}")
            return ""
        
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Página {page_num + 1} ---\n{page_text}\n"
        
        logger.info(f"PDF extraído: {len(text)} caracteres")
        return text
        
    except Exception as e:
        logger.error(f"Erro ao extrair PDF: {e}")
        return ""

def create_chunks(text: str) -> List[str]:
    """Cria chunks do texto baseado na configuração"""
    global pdf_chunks
    
    chunk_size = config["chunk_size"]
    overlap = config["overlap"]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Se não é o último chunk, tenta quebrar em uma palavra
        if end < len(text):
            # Procura o último espaço antes do fim
            last_space = text.rfind(' ', start, end)
            if last_space > start:
                end = last_space
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    logger.info(f"Criados {len(chunks)} chunks")
    return chunks

def load_ai_model():
    """Carrega o modelo de IA com tratamento de erros"""
    global qa_pipeline
    
    try:
        from transformers import pipeline
        
        logger.info(f"Carregando modelo: {config['model_name']}")
        
        qa_pipeline = pipeline(
            "question-answering",
            model=config["model_name"],
            device=-1  # CPU
        )
        
        logger.info("Modelo carregado com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao carregar modelo: {e}")
        return False

def load_cache():
    """Carrega cache de respostas"""
    global response_cache
    
    cache_file = config.get("cache_file", "response_cache.pkl")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "rb") as f:
                response_cache = pickle.load(f)
            logger.info(f"Cache carregado: {len(response_cache)} entradas")
        except Exception as e:
            logger.warning(f"Erro ao carregar cache: {e}")
            response_cache = {}

def save_cache():
    """Salva cache de respostas"""
    cache_file = config.get("cache_file", "response_cache.pkl")
    try:
        with open(cache_file, "wb") as f:
            pickle.dump(response_cache, f)
        logger.info("Cache salvo")
    except Exception as e:
        logger.warning(f"Erro ao salvar cache: {e}")

def find_best_chunk(question: str, chunks: List[str]) -> str:
    """Encontra o chunk mais relevante para a pergunta"""
    if not chunks:
        return ""
    
    # Se temos poucos chunks, retorna o primeiro
    if len(chunks) <= 2:
        return chunks[0]
    
    # Busca por palavras-chave
    question_words = set(re.findall(r'\w+', question.lower()))
    
    best_chunk = chunks[0]
    best_score = 0
    
    for chunk in chunks:
        chunk_words = set(re.findall(r'\w+', chunk.lower()))
        common_words = question_words.intersection(chunk_words)
        score = len(common_words) / len(question_words) if question_words else 0
        
        if score > best_score:
            best_score = score
            best_chunk = chunk
    
    return best_chunk

def get_cached_response(question: str, persona: str) -> Optional[str]:
    """Obtém resposta do cache"""
    if not config.get("use_caching", False):
        return None
    
    cache_key = hashlib.md5(f"{question.lower()}:{persona}".encode()).hexdigest()
    return response_cache.get(cache_key)

def cache_response(question: str, persona: str, answer: str):
    """Armazena resposta no cache"""
    if not config.get("use_caching", False):
        return
    
    cache_key = hashlib.md5(f"{question.lower()}:{persona}".encode()).hexdigest()
    response_cache[cache_key] = answer

def answer_question(question: str, persona: str) -> Dict:
    """Responde à pergunta usando estratégia otimizada"""
    global qa_pipeline, pdf_chunks
    
    # Verificar cache primeiro
    cached_answer = get_cached_response(question, persona)
    if cached_answer:
        logger.info("Resposta encontrada no cache")
        return {
            "answer": cached_answer,
            "persona": persona,
            "confidence": 1.0,
            "source": "cache"
        }
    
    if not qa_pipeline:
        return fallback_response(persona, "Modelo não disponível")
    
    try:
        # Encontrar chunk mais relevante
        context = find_best_chunk(question, pdf_chunks)
        
        if not context:
            return fallback_response(persona, "Contexto não encontrado")
        
        # Fazer pergunta ao modelo
        result = qa_pipeline(
            question=question,
            context=context,
            max_answer_len=config["max_answer_length"],
            handle_impossible_answer=True
        )
        
        answer = result['answer'].strip()
        confidence = result['score']
        
        # Verificar confiança mínima
        if not answer or confidence < config["confidence_threshold"]:
            return fallback_response(persona, "Confiança muito baixa")
        
        # Formatar resposta
        formatted_answer = format_persona_answer(answer, persona, confidence)
        
        # Armazenar no cache
        cache_response(question, persona, formatted_answer["answer"])
        
        return formatted_answer
        
    except Exception as e:
        logger.error(f"Erro ao processar pergunta: {e}")
        return fallback_response(persona, "Erro técnico")

def format_persona_answer(answer: str, persona: str, confidence: float) -> Dict:
    """Formata resposta de acordo com a personalidade"""
    if persona == "dr_gasnelio":
        return {
            "answer": f"Dr. Gasnelio responde:\n\n{answer}\n\n*Baseado na tese sobre roteiro de dispensação para hanseníase. Confiança: {confidence:.1%}*",
            "persona": "dr_gasnelio",
            "confidence": confidence,
            "source": "model"
        }
    elif persona == "ga":
        simple_answer = simplify_text(answer)
        return {
            "answer": f"Gá explica:\n\n{simple_answer}\n\n*Tá na tese, pode confiar! 😊*",
            "persona": "ga",
            "confidence": confidence,
            "source": "model"
        }
    else:
        return {
            "answer": answer,
            "persona": "default",
            "confidence": confidence,
            "source": "model"
        }

def simplify_text(text: str) -> str:
    """Simplifica texto para o Gá"""
    replacements = {
        "dispensação": "entrega de remédios",
        "medicamentos": "remédios",
        "posologia": "como tomar",
        "administração": "como tomar",
        "via de administração": "como tomar",
        "reação adversa": "efeito colateral",
        "interação medicamentosa": "mistura de remédios",
        "protocolo": "guia",
        "orientação": "explicação",
        "adesão": "seguir o tratamento"
    }
    
    simplified = text
    for technical, simple in replacements.items():
        simplified = simplified.replace(technical, simple)
    
    return simplified

def fallback_response(persona: str, reason: str = "") -> Dict:
    """Resposta de fallback"""
    if persona == "dr_gasnelio":
        return {
            "answer": f"Dr. Gasnelio responde:\n\nDesculpe, não encontrei essa informação específica na minha tese sobre roteiro de dispensação para hanseníase. {reason}\n\nPosso ajudá-lo com outras questões relacionadas ao tema da pesquisa.",
            "persona": "dr_gasnelio",
            "confidence": 0.0,
            "source": "fallback"
        }
    elif persona == "ga":
        return {
            "answer": f"Gá responde:\n\nIh, essa eu não sei! 😅 {reason}\n\nSó posso explicar coisas que estão na tese sobre hanseníase e dispensação de remédios. Pergunta outra coisa sobre o tema?",
            "persona": "ga",
            "confidence": 0.0,
            "source": "fallback"
        }
    else:
        return {
            "answer": f"Desculpe, não encontrei essa informação na tese. {reason}",
            "persona": "default",
            "confidence": 0.0,
            "source": "fallback"
        }

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint do chat otimizado"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
        
        question = data.get('question', '').strip()
        persona = data.get('persona', 'ga')
        
        if not question:
            return jsonify({"error": "Pergunta não fornecida"}), 400
        
        if persona not in ['dr_gasnelio', 'ga']:
            persona = 'ga'
        
        logger.info(f"Pergunta: {question} (persona: {persona})")
        response = answer_question(question, persona)
        
        response['timestamp'] = datetime.now().isoformat()
        response['question'] = question
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Erro no chat: {e}")
        return jsonify({
            "error": "Erro interno",
            "answer": "Desculpe, ocorreu um erro técnico.",
            "persona": persona if 'persona' in locals() else 'ga',
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificação de saúde com informações detalhadas"""
    return jsonify({
        "status": "healthy",
        "model_loaded": qa_pipeline is not None,
        "pdf_loaded": len(pdf_text) > 0,
        "chunks_created": len(pdf_chunks),
        "cache_size": len(response_cache),
        "config": config,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/info', methods=['GET'])
def api_info():
    """Informações da API"""
    return jsonify({
        "name": "Chatbot Tese Hanseníase API (Otimizada)",
        "version": "2.0.0",
        "description": "API otimizada para chatbot baseado na tese sobre roteiro de dispensação para hanseníase",
        "personas": {
            "dr_gasnelio": "Professor sério e técnico",
            "ga": "Amigo descontraído que explica de forma simples"
        },
        "model": config.get("model_name", "deepset/roberta-base-squad2"),
        "pdf_source": "Roteiro de Dispensação para Hanseníase",
        "optimizations": {
            "chunking": len(pdf_chunks) > 0,
            "caching": config.get("use_caching", False),
            "semantic_search": config.get("use_semantic_search", False)
        }
    })

if __name__ == '__main__':
    # Inicialização otimizada
    logger.info("🚀 Iniciando aplicação otimizada...")
    
    # Carregar configuração
    load_config()
    
    # Carregar PDF
    pdf_text = extract_pdf_text(PDF_PATH)
    if pdf_text:
        # Analisar complexidade
        complexity = analyze_pdf_complexity(pdf_text)
        logger.info(f"Complexidade: {complexity}")
        
        # Criar chunks
        pdf_chunks = create_chunks(pdf_text)
        
        # Carregar modelo
        if load_ai_model():
            # Carregar cache
            load_cache()
            
            # Iniciar servidor
            port = int(os.environ.get('PORT', 5000))
            debug = os.environ.get('FLASK_ENV') == 'development'
            
            logger.info(f"✅ Servidor iniciado na porta {port}")
            logger.info(f"📊 Estatísticas:")
            logger.info(f"   - PDF: {len(pdf_text)} caracteres")
            logger.info(f"   - Chunks: {len(pdf_chunks)}")
            logger.info(f"   - Cache: {len(response_cache)} entradas")
            
            app.run(host='0.0.0.0', port=port, debug=debug)
        else:
            logger.error("❌ Falha ao carregar modelo de IA")
    else:
        logger.error("❌ Falha ao carregar PDF") 