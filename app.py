from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pdfplumber
import os
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
import torch
import re
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variáveis globais
PDF_PATH = 'Roteiro-de-Dsispensacao-Hanseniase-F.docx.pdf'
pdf_text = ""
qa_pipeline = None
tokenizer = None
model = None

def extract_pdf_text(pdf_path):
    """Extrai texto do PDF"""
    global pdf_text
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Página {page_num + 1} ---\n{page_text}\n"
        logger.info(f"PDF extraído com sucesso. Total de caracteres: {len(text)}")
        return text
    except Exception as e:
        logger.error(f"Erro ao extrair PDF: {e}")
        return ""

def load_ai_model():
    """Carrega o modelo de IA gratuito do Hugging Face"""
    global qa_pipeline, tokenizer, model
    try:
        # Usando modelo gratuito e leve
        model_name = "deepset/roberta-base-squad2"
        logger.info(f"Carregando modelo: {model_name}")
        
        qa_pipeline = pipeline(
            "question-answering",
            model=model_name,
            tokenizer=model_name,
            device=-1 if not torch.cuda.is_available() else 0
        )
        logger.info("Modelo carregado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao carregar modelo: {e}")
        qa_pipeline = None

def find_relevant_context(question, full_text, max_length=4000):
    """Encontra o contexto mais relevante para a pergunta"""
    # Divide o texto em chunks menores
    chunks = []
    chunk_size = 2000
    overlap = 200
    
    for i in range(0, len(full_text), chunk_size - overlap):
        chunk = full_text[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    
    # Se temos poucos chunks, retorna o texto completo
    if len(chunks) <= 2:
        return full_text[:max_length]
    
    # Para perguntas simples, usa o primeiro chunk
    if len(question.split()) <= 5:
        return chunks[0][:max_length]
    
    # Busca por palavras-chave na pergunta
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
    
    return best_chunk[:max_length]

def answer_question(question, persona):
    """Responde à pergunta usando o modelo de IA"""
    global qa_pipeline, pdf_text
    
    if not qa_pipeline or not pdf_text:
        return fallback_response(persona, "Modelo não disponível")
    
    try:
        # Encontra contexto relevante
        context = find_relevant_context(question, pdf_text)
        
        # Faz a pergunta ao modelo
        result = qa_pipeline(
            question=question,
            context=context,
            max_answer_len=200,
            handle_impossible_answer=True
        )
        
        answer = result['answer'].strip()
        confidence = result['score']
        
        # Se a confiança for baixa ou resposta vazia, usa fallback
        if not answer or confidence < 0.3:
            return fallback_response(persona, "Informação não encontrada na tese")
        
        return format_persona_answer(answer, persona, confidence)
        
    except Exception as e:
        logger.error(f"Erro ao processar pergunta: {e}")
        return fallback_response(persona, "Erro técnico")

def format_persona_answer(answer, persona, confidence):
    """Formata a resposta de acordo com a personalidade"""
    if persona == "dr_gasnelio":
        return {
            "answer": f"Dr. Gasnelio responde:\n\n{answer}\n\n*Baseado na tese sobre roteiro de dispensação para hanseníase. Confiança: {confidence:.1%}*",
            "persona": "dr_gasnelio",
            "confidence": confidence
        }
    elif persona == "ga":
        # Simplifica a resposta para o Gá
        simple_answer = simplify_text(answer)
        return {
            "answer": f"Gá explica:\n\n{simple_answer}\n\n*Tá na tese, pode confiar! 😊*",
            "persona": "ga",
            "confidence": confidence
        }
    else:
        return {
            "answer": answer,
            "persona": "default",
            "confidence": confidence
        }

def simplify_text(text):
    """Simplifica o texto para o Gá"""
    # Remove termos muito técnicos e substitui por versões mais simples
    replacements = {
        "dispensação": "entrega de remédios",
        "farmacêutico": "farmacêutico",
        "medicamentos": "remédios",
        "tratamento": "tratamento",
        "hanseníase": "hanseníase",
        "protocolo": "guia",
        "orientação": "explicação",
        "paciente": "pessoa",
        "adesão": "seguir o tratamento",
        "posologia": "como tomar",
        "posologia": "como usar",
        "administração": "como tomar",
        "via de administração": "como tomar",
        "reação adversa": "efeito colateral",
        "interação medicamentosa": "mistura de remédios"
    }
    
    simplified = text
    for technical, simple in replacements.items():
        simplified = simplified.replace(technical, simple)
    
    return simplified

def fallback_response(persona, reason=""):
    """Resposta de fallback quando não encontra informação"""
    if persona == "dr_gasnelio":
        return {
            "answer": f"Dr. Gasnelio responde:\n\nDesculpe, não encontrei essa informação específica na minha tese sobre roteiro de dispensação para hanseníase. {reason}\n\nPosso ajudá-lo com outras questões relacionadas ao tema da pesquisa.",
            "persona": "dr_gasnelio",
            "confidence": 0.0
        }
    elif persona == "ga":
        return {
            "answer": f"Gá responde:\n\nIh, essa eu não sei! 😅 {reason}\n\nSó posso explicar coisas que estão na tese sobre hanseníase e dispensação de remédios. Pergunta outra coisa sobre o tema?",
            "persona": "ga",
            "confidence": 0.0
        }
    else:
        return {
            "answer": f"Desculpe, não encontrei essa informação na tese. {reason}",
            "persona": "default",
            "confidence": 0.0
        }

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        # Garante que o corpo é JSON válido
        if not request.is_json:
            return jsonify({"error": "Requisição deve ser JSON"}), 400

        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "JSON inválido ou vazio"}), 400

        question = data.get('question', '').strip()
        personality_id = data.get('personality_id')

        if not question:
            return jsonify({"error": "Pergunta não fornecida"}), 400

        if not personality_id or personality_id not in ['dr_gasnelio', 'ga']:
            return jsonify({"error": "Personalidade inválida"}), 400

        # Responder pergunta
        response = answer_question(question, personality_id)
        return jsonify(response)

    except Exception as e:
        logger.error(f"Erro na API de chat: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificação de saúde da API"""
    return jsonify({
        "status": "healthy",
        "model_loaded": qa_pipeline is not None,
        "pdf_loaded": len(pdf_text) > 0,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/info', methods=['GET'])
def api_info():
    """Informações sobre a API"""
    return jsonify({
        "name": "Chatbot Tese Hanseníase API",
        "version": "1.0.0",
        "description": "API para chatbot baseado na tese sobre roteiro de dispensação para hanseníase",
        "personas": {
            "dr_gasnelio": "Professor sério e técnico",
            "ga": "Amigo descontraído que explica de forma simples"
        },
        "model": "deepset/roberta-base-squad2",
        "pdf_source": "Roteiro de Dispensação para Hanseníase"
    })

if __name__ == '__main__':
    # Inicialização
    logger.info("Iniciando aplicação...")
    
    # Carrega o PDF
    if os.path.exists(PDF_PATH):
        pdf_text = extract_pdf_text(PDF_PATH)
    else:
        logger.warning(f"PDF não encontrado: {PDF_PATH}")
        pdf_text = "PDF não disponível"
    
    # Carrega o modelo de IA
    load_ai_model()
    
    # Inicia o servidor
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Servidor iniciado na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=debug) 