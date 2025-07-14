from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import json
import re
from transformers import pipeline
import torch
from sentence_transformers import SentenceTransformer
import numpy as np
import hashlib
import pickle
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class MultiDiseaseChatbot:
    def __init__(self):
        self.diseases = {}
        self.qa_pipeline = None
        self.embedding_model = None
        self.cache = {}
        self.load_models()
        self.load_diseases()
    
    def load_models(self):
        """Carrega os modelos de IA"""
        try:
            logger.info("Carregando modelos de IA...")
            self.qa_pipeline = pipeline(
                "question-answering",
                model="deepset/roberta-base-squad2",
                device=-1 if not torch.cuda.is_available() else 0
            )
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Modelos carregados com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {e}")
            raise
    
    def load_diseases(self):
        """Carrega todas as doenças configuradas"""
        try:
            # Estrutura de doenças
            self.diseases = {
                "hanseniase": {
                    "name": "Hanseníase",
                    "pdf_path": "PDFs/hanseniase.pdf",
                    "description": "Doença infecciosa crônica causada pela bactéria Mycobacterium leprae",
                    "keywords": ["hanseníase", "lepra", "mycobacterium", "bacilo de hansen"],
                    "personalities": {
                        "dr_gasnelio": {
                            "name": "Dr. Gasnelio",
                            "style": "sério e técnico",
                            "greeting": "Olá! Sou o Dr. Gasnelio, especialista em hanseníase. Como posso ajudá-lo hoje?",
                            "fallback": "Baseado na literatura médica sobre hanseníase, posso orientar que esta condição requer avaliação médica especializada. Recomendo consultar um dermatologista ou infectologista para diagnóstico adequado."
                        },
                        "ga": {
                            "name": "Gá",
                            "style": "descontraído e simples",
                            "greeting": "Oi! Sou o Gá! 😊 Vou te ajudar a entender sobre hanseníase de um jeito bem simples!",
                            "fallback": "Olha, sobre isso eu não tenho certeza no material que tenho aqui. Mas posso te dizer que é sempre bom procurar um médico quando temos dúvidas sobre saúde, certo? 😊"
                        }
                    }
                },
                "diabetes": {
                    "name": "Diabetes",
                    "pdf_path": "PDFs/diabetes.pdf",
                    "description": "Doença metabólica caracterizada por níveis elevados de glicose no sangue",
                    "keywords": ["diabetes", "glicemia", "insulina", "hiperglicemia"],
                    "personalities": {
                        "dr_gasnelio": {
                            "name": "Dr. Gasnelio",
                            "style": "sério e técnico",
                            "greeting": "Olá! Sou o Dr. Gasnelio, especialista em diabetes. Como posso ajudá-lo hoje?",
                            "fallback": "Baseado na literatura médica sobre diabetes, posso orientar que esta condição requer monitoramento contínuo e acompanhamento médico. Recomendo consultar um endocrinologista para avaliação adequada."
                        },
                        "ga": {
                            "name": "Gá",
                            "style": "descontraído e simples",
                            "greeting": "Oi! Sou o Gá! 😊 Vou te ajudar a entender sobre diabetes de um jeito bem simples!",
                            "fallback": "Olha, sobre isso eu não tenho certeza no material que tenho aqui. Mas posso te dizer que diabetes é coisa séria e sempre precisa de acompanhamento médico, ok? 😊"
                        }
                    }
                },
                "hipertensao": {
                    "name": "Hipertensão",
                    "pdf_path": "PDFs/hipertensao.pdf",
                    "description": "Pressão arterial elevada de forma persistente",
                    "keywords": ["hipertensão", "pressão alta", "hipertensão arterial", "hta"],
                    "personalities": {
                        "dr_gasnelio": {
                            "name": "Dr. Gasnelio",
                            "style": "sério e técnico",
                            "greeting": "Olá! Sou o Dr. Gasnelio, especialista em hipertensão. Como posso ajudá-lo hoje?",
                            "fallback": "Baseado na literatura médica sobre hipertensão, posso orientar que esta condição requer monitoramento regular e controle adequado. Recomendo consultar um cardiologista para avaliação completa."
                        },
                        "ga": {
                            "name": "Gá",
                            "style": "descontraído e simples",
                            "greeting": "Oi! Sou o Gá! 😊 Vou te ajudar a entender sobre pressão alta de um jeito bem simples!",
                            "fallback": "Olha, sobre isso eu não tenho certeza no material que tenho aqui. Mas posso te dizer que pressão alta é coisa séria e precisa de muito cuidado, ok? 😊"
                        }
                    }
                }
            }
            
            # Criar diretório PDFs se não existir
            os.makedirs("PDFs", exist_ok=True)
            
            logger.info(f"Carregadas {len(self.diseases)} doenças configuradas")
        except Exception as e:
            logger.error(f"Erro ao carregar doenças: {e}")
            raise
    
    def get_available_diseases(self):
        """Retorna lista de doenças disponíveis"""
        return [
            {
                "id": disease_id,
                "name": disease["name"],
                "description": disease["description"],
                "pdf_exists": os.path.exists(disease["pdf_path"])
            }
            for disease_id, disease in self.diseases.items()
        ]
    
    def get_disease_personalities(self, disease_id):
        """Retorna as personalidades disponíveis para uma doença"""
        if disease_id not in self.diseases:
            return []
        
        return [
            {
                "id": personality_id,
                "name": personality["name"],
                "style": personality["style"],
                "greeting": personality["greeting"]
            }
            for personality_id, personality in self.diseases[disease_id]["personalities"].items()
        ]
    
    def chunk_text(self, text, chunk_size=2000, overlap=200):
        """Divide o texto em chunks menores"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Tenta quebrar em uma quebra de linha ou espaço
            last_newline = text.rfind('\n', start, end)
            last_space = text.rfind(' ', start, end)
            
            if last_newline > start + chunk_size * 0.8:
                end = last_newline + 1
            elif last_space > start + chunk_size * 0.8:
                end = last_space + 1
            
            chunks.append(text[start:end])
            start = end - overlap
        
        return chunks
    
    def extract_text_from_pdf(self, pdf_path):
        """Extrai texto do PDF"""
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return text.strip()
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF {pdf_path}: {e}")
            return ""
    
    def get_relevant_chunks(self, question, disease_id, top_k=3):
        """Encontra os chunks mais relevantes para a pergunta"""
        if disease_id not in self.diseases:
            return []
        
        pdf_path = self.diseases[disease_id]["pdf_path"]
        
        if not os.path.exists(pdf_path):
            logger.warning(f"PDF não encontrado: {pdf_path}")
            return []
        
        # Extrair texto do PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return []
        
        # Dividir em chunks
        chunks = self.chunk_text(text)
        
        # Calcular embeddings
        question_embedding = self.embedding_model.encode(question)
        chunk_embeddings = self.embedding_model.encode(chunks)
        
        # Calcular similaridade
        similarities = np.dot(chunk_embeddings, question_embedding) / (
            np.linalg.norm(chunk_embeddings, axis=1) * np.linalg.norm(question_embedding)
        )
        
        # Pegar os top_k chunks mais relevantes
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [chunks[i] for i in top_indices if similarities[i] > 0.1]
    
    def answer_question(self, question, disease_id, personality_id):
        """Responde uma pergunta sobre uma doença específica"""
        if disease_id not in self.diseases:
            return {
                "error": "Doença não encontrada",
                "available_diseases": self.get_available_diseases()
            }
        
        if personality_id not in self.diseases[disease_id]["personalities"]:
            return {
                "error": "Personalidade não encontrada",
                "available_personalities": self.get_disease_personalities(disease_id)
            }
        
        # Verificar cache
        cache_key = f"{disease_id}_{personality_id}_{hashlib.md5(question.encode()).hexdigest()}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Obter chunks relevantes
        relevant_chunks = self.get_relevant_chunks(question, disease_id)
        
        if not relevant_chunks:
            # Fallback baseado na personalidade
            personality = self.diseases[disease_id]["personalities"][personality_id]
            if personality_id == "dr_gasnelio":
                response = {
                    "answer": "",
                    "confidence": 0.0,
                    "source": "no_answer",
                    "personality": personality["name"],
                    "disease": self.diseases[disease_id]["name"]
                }
            else:
                response = {
                    "answer": personality["fallback"],
                    "confidence": 0.0,
                    "source": "fallback",
                    "personality": personality["name"],
                    "disease": self.diseases[disease_id]["name"]
                }
            self.cache[cache_key] = response
            return response
        
        # Combinar chunks relevantes
        context = " ".join(relevant_chunks)
        
        try:
            # Fazer pergunta ao modelo
            result = self.qa_pipeline(
                question=question,
                context=context,
                max_answer_len=200,
                handle_impossible_answer=True
            )
            
            # Verificar confiança
            confidence = result.get('score', 0.0)
            
            if confidence < 0.35:  # Limite de confiança
                personality = self.diseases[disease_id]["personalities"][personality_id]
                answer = personality["fallback"]
                confidence = 0.0
                source = "fallback"
            else:
                answer = result['answer']
                source = "pdf"
            
            response = {
                "answer": answer,
                "confidence": confidence,
                "source": source,
                "personality": self.diseases[disease_id]["personalities"][personality_id]["name"],
                "disease": self.diseases[disease_id]["name"]
            }
            
            self.cache[cache_key] = response
            return response
            
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {e}")
            personality = self.diseases[disease_id]["personalities"][personality_id]
            response = {
                "answer": personality["fallback"],
                "confidence": 0.0,
                "source": "error_fallback",
                "personality": personality["name"],
                "disease": self.diseases[disease_id]["name"]
            }
            self.cache[cache_key] = response
            return response

# Inicializar chatbot
chatbot = MultiDiseaseChatbot()

@app.route('/')
def index():
    """Página inicial com seleção de doença"""
    html_template = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chatbot Multi-Doenças</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
                max-width: 800px;
                width: 100%;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .content {
                padding: 40px;
            }
            
            .disease-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .disease-card {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                cursor: pointer;
                border: 2px solid transparent;
            }
            
            .disease-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                border-color: #667eea;
            }
            
            .disease-card.selected {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .disease-card h3 {
                font-size: 1.3em;
                margin-bottom: 10px;
            }
            
            .disease-card p {
                font-size: 0.9em;
                opacity: 0.8;
                margin-bottom: 15px;
            }
            
            .status {
                font-size: 0.8em;
                padding: 5px 10px;
                border-radius: 20px;
                display: inline-block;
            }
            
            .status.available {
                background: #28a745;
                color: white;
            }
            
            .status.unavailable {
                background: #dc3545;
                color: white;
            }
            
            .personality-section {
                margin-top: 30px;
                text-align: center;
            }
            
            .personality-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            
            .personality-card {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                cursor: pointer;
                border: 2px solid transparent;
            }
            
            .personality-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.1);
                border-color: #667eea;
            }
            
            .personality-card.selected {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .personality-card h4 {
                font-size: 1.1em;
                margin-bottom: 8px;
            }
            
            .personality-card p {
                font-size: 0.9em;
                opacity: 0.8;
            }
            
            .start-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 40px;
                border-radius: 25px;
                font-size: 1.1em;
                cursor: pointer;
                transition: transform 0.3s ease;
                margin-top: 20px;
            }
            
            .start-btn:hover {
                transform: translateY(-2px);
            }
            
            .start-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }
            
            .instructions {
                background: #e9ecef;
                border-radius: 15px;
                padding: 20px;
                margin-top: 30px;
            }
            
            .instructions h3 {
                color: #495057;
                margin-bottom: 15px;
            }
            
            .instructions ul {
                list-style: none;
                padding: 0;
            }
            
            .instructions li {
                padding: 8px 0;
                border-bottom: 1px solid #dee2e6;
            }
            
            .instructions li:last-child {
                border-bottom: none;
            }
            
            .instructions li:before {
                content: "✓";
                color: #28a745;
                font-weight: bold;
                margin-right: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 Chatbot Multi-Doenças</h1>
                <p>Selecione uma doença e uma personalidade para começar</p>
            </div>
            
            <div class="content">
                <h2 style="text-align: center; margin-bottom: 30px; color: #495057;">Escolha uma Doença:</h2>
                
                <div class="disease-grid" id="diseaseGrid">
                    <!-- Doenças serão carregadas aqui -->
                </div>
                
                <div class="personality-section" id="personalitySection" style="display: none;">
                    <h2 style="color: #495057; margin-bottom: 20px;">Escolha uma Personalidade:</h2>
                    
                    <div class="personality-grid" id="personalityGrid">
                        <!-- Personalidades serão carregadas aqui -->
                    </div>
                    
                    <button class="start-btn" id="startBtn" disabled>Iniciar Chat</button>
                </div>
                
                <div class="instructions">
                    <h3>📋 Como usar:</h3>
                    <ul>
                        <li>Selecione uma doença da lista acima</li>
                        <li>Escolha entre Dr. Gasnelio (técnico) ou Gá (descontraído)</li>
                        <li>Clique em "Iniciar Chat" para começar a conversa</li>
                        <li>Faça perguntas sobre a doença selecionada</li>
                        <li>O chatbot responderá baseado no conteúdo do PDF específico</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <script>
            let selectedDisease = null;
            let selectedPersonality = null;
            
            // Carregar doenças disponíveis
            async function loadDiseases() {
                try {
                    const response = await fetch('/api/diseases');
                    const diseases = await response.json();
                    
                    const diseaseGrid = document.getElementById('diseaseGrid');
                    diseaseGrid.innerHTML = '';
                    
                    diseases.forEach(disease => {
                        const card = document.createElement('div');
                        card.className = 'disease-card';
                        card.onclick = () => selectDisease(disease.id);
                        
                        const statusClass = disease.pdf_exists ? 'available' : 'unavailable';
                        const statusText = disease.pdf_exists ? 'Disponível' : 'PDF não encontrado';
                        
                        card.innerHTML = `
                            <h3>${disease.name}</h3>
                            <p>${disease.description}</p>
                            <span class="status ${statusClass}">${statusText}</span>
                        `;
                        
                        diseaseGrid.appendChild(card);
                    });
                } catch (error) {
                    console.error('Erro ao carregar doenças:', error);
                }
            }
            
            // Selecionar doença
            function selectDisease(diseaseId) {
                selectedDisease = diseaseId;
                
                // Atualizar seleção visual
                document.querySelectorAll('.disease-card').forEach(card => {
                    card.classList.remove('selected');
                });
                event.target.closest('.disease-card').classList.add('selected');
                
                // Carregar personalidades
                loadPersonalities(diseaseId);
                
                // Mostrar seção de personalidades
                document.getElementById('personalitySection').style.display = 'block';
            }
            
            // Carregar personalidades
            async function loadPersonalities(diseaseId) {
                try {
                    const response = await fetch(`/api/diseases/${diseaseId}/personalities`);
                    const personalities = await response.json();
                    
                    const personalityGrid = document.getElementById('personalityGrid');
                    personalityGrid.innerHTML = '';
                    
                    personalities.forEach(personality => {
                        const card = document.createElement('div');
                        card.className = 'personality-card';
                        card.onclick = () => selectPersonality(personality.id);
                        
                        card.innerHTML = `
                            <h4>${personality.name}</h4>
                            <p>${personality.style}</p>
                        `;
                        
                        personalityGrid.appendChild(card);
                    });
                } catch (error) {
                    console.error('Erro ao carregar personalidades:', error);
                }
            }
            
            // Selecionar personalidade
            function selectPersonality(personalityId) {
                selectedPersonality = personalityId;
                
                // Atualizar seleção visual
                document.querySelectorAll('.personality-card').forEach(card => {
                    card.classList.remove('selected');
                });
                event.target.closest('.personality-card').classList.add('selected');
                
                // Habilitar botão de início
                document.getElementById('startBtn').disabled = false;
            }
            
            // Iniciar chat
            function startChat() {
                if (selectedDisease && selectedPersonality) {
                    // Redirecionar para o chat com parâmetros
                    window.location.href = `/chat?disease=${selectedDisease}&personality=${selectedPersonality}`;
                }
            }
            
            // Event listeners
            document.getElementById('startBtn').addEventListener('click', startChat);
            
            // Carregar doenças ao iniciar
            loadDiseases();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/chat')
def chat():
    """Página do chat com doença e personalidade específicas"""
    disease_id = request.args.get('disease')
    personality_id = request.args.get('personality')
    
    if not disease_id or not personality_id:
        return "Parâmetros inválidos", 400
    
    if disease_id not in chatbot.diseases:
        return "Doença não encontrada", 404
    
    if personality_id not in chatbot.diseases[disease_id]["personalities"]:
        return "Personalidade não encontrada", 404
    
    disease = chatbot.diseases[disease_id]
    personality = disease["personalities"][personality_id]
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chat - {disease['name']} - {personality['name']}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }}
            
            .header {{
                background: rgba(255,255,255,0.95);
                backdrop-filter: blur(10px);
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .header-info {{
                display: flex;
                align-items: center;
                gap: 20px;
            }}
            
            .disease-badge {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
            }}
            
            .personality-badge {{
                background: #28a745;
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
            }}
            
            .back-btn {{
                background: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 20px;
                cursor: pointer;
                text-decoration: none;
                transition: background 0.3s ease;
            }}
            
            .back-btn:hover {{
                background: #5a6268;
            }}
            
            .chat-container {{
                flex: 1;
                display: flex;
                flex-direction: column;
                max-width: 800px;
                margin: 20px auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            
            .chat-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            
            .chat-header h1 {{
                font-size: 2em;
                margin-bottom: 10px;
            }}
            
            .chat-header p {{
                font-size: 1.1em;
                opacity: 0.9;
            }}
            
            .chat-messages {{
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                max-height: 500px;
            }}
            
            .message {{
                margin-bottom: 20px;
                display: flex;
                align-items: flex-start;
                gap: 15px;
            }}
            
            .message.user {{
                flex-direction: row-reverse;
            }}
            
            .message-avatar {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                color: white;
                flex-shrink: 0;
            }}
            
            .message.user .message-avatar {{
                background: #667eea;
            }}
            
            .message.bot .message-avatar {{
                background: #28a745;
            }}
            
            .message-content {{
                background: #f8f9fa;
                padding: 15px 20px;
                border-radius: 20px;
                max-width: 70%;
                word-wrap: break-word;
            }}
            
            .message.user .message-content {{
                background: #667eea;
                color: white;
            }}
            
            .message.bot .message-content {{
                background: #e9ecef;
                color: #495057;
            }}
            
            .message-time {{
                font-size: 0.8em;
                opacity: 0.7;
                margin-top: 5px;
            }}
            
            .chat-input {{
                padding: 20px;
                border-top: 1px solid #dee2e6;
                background: #f8f9fa;
            }}
            
            .input-group {{
                display: flex;
                gap: 10px;
            }}
            
            .chat-input input {{
                flex: 1;
                padding: 15px 20px;
                border: 2px solid #dee2e6;
                border-radius: 25px;
                font-size: 1em;
                outline: none;
                transition: border-color 0.3s ease;
            }}
            
            .chat-input input:focus {{
                border-color: #667eea;
            }}
            
            .send-btn {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 1em;
                transition: transform 0.3s ease;
            }}
            
            .send-btn:hover {{
                transform: translateY(-2px);
            }}
            
            .send-btn:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }}
            
            .typing-indicator {{
                display: none;
                padding: 15px 20px;
                background: #e9ecef;
                border-radius: 20px;
                margin-bottom: 20px;
                color: #6c757d;
                font-style: italic;
            }}
            
            .confidence-indicator {{
                font-size: 0.8em;
                opacity: 0.7;
                margin-top: 5px;
            }}
            
            .source-indicator {{
                font-size: 0.8em;
                opacity: 0.7;
                margin-top: 5px;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-info">
                <span class="disease-badge">{disease['name']}</span>
                <span class="personality-badge">{personality['name']}</span>
            </div>
            <a href="/" class="back-btn">← Voltar</a>
        </div>
        
        <div class="chat-container">
            <div class="chat-header">
                <h1>{personality['name']}</h1>
                <p>Especialista em {disease['name']} - {personality['style']}</p>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="message bot">
                    <div class="message-avatar">{personality['name'][0]}</div>
                    <div class="message-content">
                        {personality['greeting']}
                        <div class="message-time">{datetime.now().strftime('%H:%M')}</div>
                    </div>
                </div>
            </div>
            
            <div class="typing-indicator" id="typingIndicator">
                {personality['name']} está digitando...
            </div>
            
            <div class="chat-input">
                <div class="input-group">
                    <input type="text" id="messageInput" placeholder="Digite sua pergunta sobre {disease['name']}..." onkeypress="handleKeyPress(event)">
                    <button class="send-btn" id="sendBtn" onclick="sendMessage()">Enviar</button>
                </div>
            </div>
        </div>
        
        <script>
            const diseaseId = '{disease_id}';
            const personalityId = '{personality_id}';
            const personalityName = '{personality['name']}';
            
            function addMessage(content, isUser = false, confidence = null, source = null) {{
                const messagesContainer = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${{isUser ? 'user' : 'bot'}}`;
                
                const avatar = document.createElement('div');
                avatar.className = 'message-avatar';
                avatar.textContent = isUser ? 'U' : personalityName[0];
                
                const messageContent = document.createElement('div');
                messageContent.className = 'message-content';
                messageContent.innerHTML = content;
                
                const time = document.createElement('div');
                time.className = 'message-time';
                time.textContent = new Date().toLocaleTimeString('pt-BR', {{hour: '2-digit', minute: '2-digit'}});
                messageContent.appendChild(time);
                
                if (confidence !== null && source !== null) {{
                    const confidenceDiv = document.createElement('div');
                    confidenceDiv.className = 'confidence-indicator';
                    confidenceDiv.textContent = `Confiança: ${{(confidence * 100).toFixed(1)}}%`;
                    messageContent.appendChild(confidenceDiv);
                    
                    const sourceDiv = document.createElement('div');
                    sourceDiv.className = 'source-indicator';
                    sourceDiv.textContent = `Fonte: ${{source === 'pdf' ? 'PDF da tese' : 'Resposta padrão'}}`;
                    messageContent.appendChild(sourceDiv);
                }}
                
                messageDiv.appendChild(avatar);
                messageDiv.appendChild(messageContent);
                messagesContainer.appendChild(messageDiv);
                
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }}
            
            function showTyping() {{
                document.getElementById('typingIndicator').style.display = 'block';
                document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight;
            }}
            
            function hideTyping() {{
                document.getElementById('typingIndicator').style.display = 'none';
            }}
            
            async function sendMessage() {{
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Adicionar mensagem do usuário
                addMessage(message, true);
                input.value = '';
                
                // Mostrar indicador de digitação
                showTyping();
                
                try {{
                    const response = await fetch('/api/chat', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{
                            question: message,
                            disease_id: diseaseId,
                            personality_id: personalityId
                        }})
                    }});
                    
                    const data = await response.json();
                    
                    hideTyping();
                    
                    if (data.error) {{
                        addMessage(`Erro: ${{data.error}}`);
                    }} else {{
                        addMessage(data.answer, false, data.confidence, data.source);
                    }}
                }} catch (error) {{
                    hideTyping();
                    addMessage('Erro ao enviar mensagem. Tente novamente.');
                    console.error('Erro:', error);
                }}
            }}
            
            function handleKeyPress(event) {{
                if (event.key === 'Enter') {{
                    sendMessage();
                }}
            }}
            
            // Focar no input ao carregar
            document.getElementById('messageInput').focus();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    """API para listar doenças disponíveis"""
    return jsonify(chatbot.get_available_diseases())

@app.route('/api/diseases/<disease_id>/personalities', methods=['GET'])
def get_personalities(disease_id):
    """API para listar personalidades de uma doença"""
    return jsonify(chatbot.get_disease_personalities(disease_id))

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API para chat"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        disease_id = data.get('disease_id')
        personality_id = data.get('personality_id')
        
        if not question:
            return jsonify({"error": "Pergunta não fornecida"}), 400
        
        if not disease_id or not personality_id:
            return jsonify({"error": "Doença ou personalidade não fornecida"}), 400
        
        # Responder pergunta
        response = chatbot.answer_question(question, disease_id, personality_id)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Erro na API de chat: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificação de saúde da API"""
    return jsonify({
        "status": "healthy",
        "diseases_loaded": len(chatbot.diseases),
        "models_loaded": chatbot.qa_pipeline is not None and chatbot.embedding_model is not None,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🏥 Chatbot Multi-Doenças iniciando...")
    print(f"📚 Doenças carregadas: {len(chatbot.diseases)}")
    print("🌐 Servidor rodando em http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 