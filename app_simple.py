from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import json
import re
import hashlib
import pickle
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class HanseniaseChatbot:
    def __init__(self):
        self.pdf_path = "PDFs/Roteiro de Dsispensação - Hanseníase F.docx.pdf"
        self.cache = {}
        self.load_pdf_content()
        
        # Dicionário de sinônimos e termos relacionados
        self.synonyms = {
            'hanseníase': ['lepra', 'doença de hansen', 'mycobacterium leprae'],
            'medicamento': ['fármaco', 'droga', 'remédio', 'medicação'],
            'dispensação': ['dispensar', 'entrega', 'fornecimento', 'distribuição'],
            'tratamento': ['terapia', 'cura', 'medicação', 'tratar'],
            'sintomas': ['sinais', 'manifestações', 'sintomatologia'],
            'diagnóstico': ['identificação', 'detecção', 'diagnosticar'],
            'prevenção': ['prevenir', 'evitar', 'profilaxia'],
            'contágio': ['transmissão', 'infecção', 'contaminação'],
            'cura': ['tratamento', 'recuperação', 'melhora'],
            'antibiótico': ['antimicrobiano', 'medicamento antibacteriano'],
            'dapsona': ['dds', 'diaminodifenilsulfona'],
            'rifampicina': ['rifampin'],
            'clofazimina': ['lamprene'],
            'poliquimioterapia': ['pqt', 'tratamento múltiplo'],
            'paucibacilar': ['pb', 'poucos bacilos'],
            'multibacilar': ['mb', 'muitos bacilos'],
            'bacilo': ['bactéria', 'mycobacterium', 'micobactéria'],
            'lesão': ['ferida', 'mancha', 'alteração cutânea'],
            'pele': ['cutâneo', 'dermatológico', 'epiderme'],
            'nervo': ['neural', 'nervoso', 'neurológico'],
            'deformidade': ['deformação', 'sequela', 'alteração física'],
            'isolamento': ['separação', 'quarentena', 'isolamento social'],
            'notificação': ['comunicação', 'registro', 'declaração'],
            'vigilância': ['monitoramento', 'acompanhamento', 'supervisão'],
            'reação': ['resposta imunológica', 'inflamação', 'alergia'],
            'recidiva': ['recaída', 'retorno da doença', 'reaparecimento'],
            'resistência': ['resistente', 'refratário', 'não responsivo'],
            'adverso': ['efeito colateral', 'reação adversa', 'complicação'],
            'compliance': ['aderência', 'cumprimento', 'seguimento do tratamento'],
            'monitoramento': ['acompanhamento', 'vigilância', 'supervisão']
        }
    
    def load_pdf_content(self):
        """Carrega e processa o conteúdo do PDF"""
        try:
            if os.path.exists(self.pdf_path):
                self.pdf_text = self.extract_text_from_pdf(self.pdf_path)
                self.chunks = self.chunk_text(self.pdf_text)
                logger.info(f"PDF carregado: {len(self.chunks)} chunks")
            else:
                logger.warning(f"PDF não encontrado: {self.pdf_path}")
                self.pdf_text = ""
                self.chunks = []
        except Exception as e:
            logger.error(f"Erro ao carregar PDF: {e}")
            self.pdf_text = ""
            self.chunks = []
    
    def chunk_text(self, text, chunk_size=1500, overlap=300):
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
            
            # Tenta quebrar em parágrafos primeiro
            last_paragraph = text.rfind('\n\n', start, end)
            last_newline = text.rfind('\n', start, end)
            last_sentence = text.rfind('. ', start, end)
            last_space = text.rfind(' ', start, end)
            
            # Prioridade: parágrafo > frase > quebra de linha > espaço
            if last_paragraph > start + chunk_size * 0.7:
                end = last_paragraph + 2
            elif last_sentence > start + chunk_size * 0.7:
                end = last_sentence + 2
            elif last_newline > start + chunk_size * 0.7:
                end = last_newline + 1
            elif last_space > start + chunk_size * 0.7:
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
    
    def expand_query_with_synonyms(self, question):
        """Expande a pergunta com sinônimos e termos relacionados"""
        expanded_terms = [question.lower()]
        
        for term, synonyms in self.synonyms.items():
            if term in question.lower():
                for synonym in synonyms:
                    expanded_question = question.lower().replace(term, synonym)
                    if expanded_question not in expanded_terms:
                        expanded_terms.append(expanded_question)
        
        return expanded_terms
    
    def get_relevant_chunks(self, question, top_k=3):
        """Encontra os chunks mais relevantes para a pergunta usando busca por palavras-chave"""
        if not self.chunks:
            return []
        
        try:
            # Busca por palavras-chave
            keyword_scores = []
            question_words = set(question.lower().split())
            
            for chunk in self.chunks:
                chunk_words = set(chunk.lower().split())
                common_words = question_words.intersection(chunk_words)
                if common_words:
                    score = len(common_words) / len(question_words)
                    keyword_scores.append((score, chunk))
                else:
                    keyword_scores.append((0, chunk))
            
            # Ordenar por score e pegar os melhores
            keyword_scores.sort(reverse=True)
            relevant_chunks = [chunk for score, chunk in keyword_scores[:top_k] if score > 0.1]
            
            return relevant_chunks
            
        except Exception as e:
            logger.error(f"Erro ao calcular similaridade: {e}")
            return []
    
    def answer_question(self, question, personality_id):
        """Responde uma pergunta sobre hanseníase com busca por palavras-chave"""
        # Verificar cache
        cache_key = f"{personality_id}_{hashlib.md5(question.encode()).hexdigest()}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Obter chunks relevantes
        relevant_chunks = self.get_relevant_chunks(question, top_k=5)
        
        if not relevant_chunks:
            # Sem resposta encontrada no PDF
            if personality_id == "dr_gasnelio":
                response = {
                    "answer": "Não encontrei essa informação específica na tese. Por favor, reformule sua pergunta ou seja mais específico sobre o aspecto da hanseníase que gostaria de saber.",
                    "confidence": 0.0,
                    "source": "no_answer",
                    "personality": "Dr. Gasnelio",
                    "disease": "Hanseníase"
                }
            else:
                response = {
                    "answer": "Olha, sobre isso específico eu não tenho certeza no material que tenho aqui. Mas posso te ajudar com outras perguntas sobre hanseníase! Que tal perguntar sobre sintomas, tratamento ou como funciona a dispensação dos medicamentos? 😊",
                    "confidence": 0.0,
                    "source": "fallback",
                    "personality": "Gá",
                    "disease": "Hanseníase"
                }
            self.cache[cache_key] = response
            return response
        
        # Combinar chunks relevantes
        context = " ".join(relevant_chunks)
        
        # Resposta baseada no contexto encontrado
        if personality_id == "dr_gasnelio":
            response = {
                "answer": f"Com base na documentação, posso informar que: {context[:500]}...",
                "confidence": 0.8,
                "source": "pdf_content",
                "personality": "Dr. Gasnelio",
                "disease": "Hanseníase"
            }
        else:
            response = {
                "answer": f"Olha, encontrei isso na documentação: {context[:500]}...",
                "confidence": 0.8,
                "source": "pdf_content",
                "personality": "Gá",
                "disease": "Hanseníase"
            }
        
        self.cache[cache_key] = response
        return response

# Inicializar o chatbot
chatbot = HanseniaseChatbot()

@app.route('/')
def index():
    """Página principal"""
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Roteiro de Dispensação - Hanseníase</title>
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
                max-height: 90vh;
                display: flex;
                flex-direction: column;
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
                font-weight: 300;
            }
            
            .header p {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .chat-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                max-height: 60vh;
            }
            
            .chat-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background: #f8f9fa;
            }
            
            .message {
                margin-bottom: 15px;
                padding: 15px;
                border-radius: 15px;
                max-width: 80%;
                word-wrap: break-word;
            }
            
            .user-message {
                background: #667eea;
                color: white;
                margin-left: auto;
                border-bottom-right-radius: 5px;
            }
            
            .bot-message {
                background: white;
                color: #333;
                border: 1px solid #e0e0e0;
                border-bottom-left-radius: 5px;
            }
            
            .chat-input {
                padding: 20px;
                background: white;
                border-top: 1px solid #e0e0e0;
                display: flex;
                gap: 10px;
            }
            
            .chat-input input {
                flex: 1;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            
            .chat-input input:focus {
                border-color: #667eea;
            }
            
            .chat-input button {
                padding: 15px 25px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                transition: transform 0.2s;
            }
            
            .chat-input button:hover {
                transform: translateY(-2px);
            }
            
            .personality-selector {
                padding: 20px;
                background: #f8f9fa;
                border-bottom: 1px solid #e0e0e0;
                text-align: center;
            }
            
            .personality-selector label {
                margin-right: 20px;
                cursor: pointer;
            }
            
            .personality-selector input[type="radio"] {
                margin-right: 5px;
            }
            
            .loading {
                text-align: center;
                padding: 20px;
                color: #666;
            }
            
            .typing-indicator {
                display: flex;
                align-items: center;
                gap: 5px;
                padding: 15px;
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 15px;
                border-bottom-left-radius: 5px;
                max-width: 80%;
            }
            
            .typing-dot {
                width: 8px;
                height: 8px;
                background: #667eea;
                border-radius: 50%;
                animation: typing 1.4s infinite ease-in-out;
            }
            
            .typing-dot:nth-child(1) { animation-delay: -0.32s; }
            .typing-dot:nth-child(2) { animation-delay: -0.16s; }
            
            @keyframes typing {
                0%, 80%, 100% { transform: scale(0); }
                40% { transform: scale(1); }
            }
            
            @media (max-width: 768px) {
                .container {
                    margin: 10px;
                    max-height: 95vh;
                }
                
                .header h1 {
                    font-size: 2em;
                }
                
                .message {
                    max-width: 90%;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Chat Hanseníase</h1>
                <p>Assistente virtual para dúvidas sobre dispensação de medicamentos</p>
            </div>
            
            <div class="personality-selector">
                <label>
                    <input type="radio" name="personality" value="gá" checked>
                    Gá (Amigável)
                </label>
                <label>
                    <input type="radio" name="personality" value="dr_gasnelio">
                    Dr. Gasnelio (Técnico)
                </label>
            </div>
            
            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="message bot-message">
                        Olá! Sou o assistente virtual sobre hanseníase. Como posso te ajudar hoje? 😊
                    </div>
                </div>
                
                <div class="chat-input">
                    <input type="text" id="userInput" placeholder="Digite sua pergunta sobre hanseníase..." onkeypress="handleKeyPress(event)">
                    <button onclick="sendMessage()">Enviar</button>
                </div>
            </div>
        </div>
        
        <script>
            let isTyping = false;
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
            
            function addMessage(message, isUser = false) {
                const chatMessages = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
                messageDiv.textContent = message;
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function showTypingIndicator() {
                const chatMessages = document.getElementById('chatMessages');
                const typingDiv = document.createElement('div');
                typingDiv.className = 'typing-indicator';
                typingDiv.id = 'typingIndicator';
                typingDiv.innerHTML = `
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                `;
                chatMessages.appendChild(typingDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function hideTypingIndicator() {
                const typingIndicator = document.getElementById('typingIndicator');
                if (typingIndicator) {
                    typingIndicator.remove();
                }
            }
            
            async function sendMessage() {
                const userInput = document.getElementById('userInput');
                const message = userInput.value.trim();
                
                if (!message || isTyping) return;
                
                // Adicionar mensagem do usuário
                addMessage(message, true);
                userInput.value = '';
                
                // Mostrar indicador de digitação
                isTyping = true;
                showTypingIndicator();
                
                // Obter personalidade selecionada
                const personality = document.querySelector('input[name="personality"]:checked').value;
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            personality: personality
                        })
                    });
                    
                    const data = await response.json();
                    
                    // Remover indicador de digitação
                    hideTypingIndicator();
                    
                    // Adicionar resposta do bot
                    addMessage(data.answer);
                    
                } catch (error) {
                    console.error('Erro:', error);
                    hideTypingIndicator();
                    addMessage('Desculpe, ocorreu um erro. Tente novamente.');
                }
                
                isTyping = false;
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.route('/chat')
def chat():
    """Página de chat simples"""
    return index()

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API para chat"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        personality = data.get('personality', 'gá')
        
        if not message:
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        # Processar a pergunta
        response = chatbot.answer_question(message, personality)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Erro no chat API: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificação de saúde da API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Hanseníase Chatbot API'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 