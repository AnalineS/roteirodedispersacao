# Chatbot Inteligente para Roteiro de Dispensação

Chatbot modular e inteligente baseado em tese de roteiro de dispensação, com personalidades técnicas e amigáveis, integração com IA, busca semântica e interface moderna.

---

## 🚩 Estrutura do Projeto

```
├── app/                # Backend principal (Flask, lógica RAG, integração LangFlow)
│   ├── services/       # Utilitários centralizados (chunking, PDF, respostas)
│   ├── ...
├── backend/            # Alternativa de backend, integrações e endpoints
├── frontend/           # Interface Streamlit (chatbot web)
├── scripts/            # Scripts utilitários e manutenção
├── tests/              # Testes automatizados
├── relatorio-disp/     # Documentação, históricos, arquivos legados
├── static/, templates/ # Recursos estáticos e templates HTML
├── requirements.txt    # Dependências principais
└── README.md           # Este arquivo
```

---

## 👤 Para Usuários Finais

### Instalação Rápida
1. **Pré-requisitos:** Python 3.9+, internet, PDF da tese
2. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd gemini-v2
   ```
3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Coloque o PDF da tese** na raiz do projeto:
   - `Roteiro-de-Dsispensacao-Hanseniase-F.docx.pdf`
5. **Inicie a interface web:**
   ```bash
   python -m app.streamlit_app
   # ou
   streamlit run app/streamlit_app.py
   ```
6. **Acesse:** [http://localhost:8501](http://localhost:8501)

### Principais Funcionalidades
- Chat com duas personalidades: Dr. Gasnelio (técnico) e Gá (amigável)
- Respostas baseadas em IA e informações da tese
- Interface web moderna e responsiva
- Upload de documentos e busca semântica

---

## 👨‍💻 Para Desenvolvedores

### Estrutura Modular
- **app/**: Backend principal (Flask), lógica RAG, integração LangFlow
- **app/services/**: Funções utilitárias centralizadas (chunk_text, extract_text_from_pdf, etc)
- **backend/**: Alternativa de backend, endpoints REST, integrações
- **frontend/**: Interface Streamlit (web)
- **scripts/**: Scripts de build, manutenção e utilidades
- **tests/**: Testes automatizados

### Executando o Backend (API Flask)
```bash
python -m app.flask_api
# ou
python app/main.py --mode flask
```
Acesse: [http://localhost:5000](http://localhost:5000)

### Executando o Frontend (Streamlit)
```bash
python -m app.streamlit_app
# ou
streamlit run app/streamlit_app.py
```
Acesse: [http://localhost:8501](http://localhost:8501)

### Testes
```bash
pytest tests/
```

### Variáveis de Ambiente Importantes
- `ASTRA_DB_TOKEN`, `ASTRA_DB_API_ENDPOINT`: Integração com Astra DB
- `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`: Integração com LLMs externos
- `LANGFLOW_API_KEY`, `LANGFLOW_BASE_URL`: Integração com LangFlow
- `FLASK_HOST`, `FLASK_PORT`, `STREAMLIT_HOST`, `STREAMLIT_PORT`: Configuração de servidores

Configure variáveis em `.env` ou diretamente no ambiente.

### Utilização dos Utilitários Centralizados
Exemplo de uso do chunking:
```python
from app.services.text_utils import chunk_text
chunks = chunk_text(texto, chunk_size=1500, overlap=300)
```

---

## 🔗 Endpoints Principais (API Flask)
- `GET /api/health` — Health check
- `POST /api/chat` — Envia mensagem ao chatbot
- `GET /api/flows` — Lista fluxos LangFlow
- `POST /api/flows` — Cria novo fluxo
- `POST /api/calculate` — Calcula parâmetros de dispersão
- `POST /api/upload` — Upload de documentos

Veja exemplos de payloads e respostas na documentação dos endpoints.

---

## 🧩 Decisões de Design e Modularização
- **Centralização de utilitários:** Todas as funções de chunking, PDF, expansão de sinônimos e resposta estão em `app/services/`
- **Remoção de duplicidade:** Funções duplicadas e scripts antigos foram removidos ou arquivados
- **Documentação:** Todos os módulos, funções e lógicas complexas estão documentados com docstrings e comentários explicativos
- **Testes:** Estrutura pronta para testes automatizados
- **Fácil manutenção:** Separação clara entre backend, frontend, utilitários e scripts

---

## 📝 Manutenção e Contribuição
- Siga o padrão de modularização e centralização de utilitários
- Documente funções e lógicas complexas
- Prefira abrir issues ou pull requests para contribuições
- Consulte a pasta `relatorio-disp/` para histórico e documentação legada

---

## 👥 Autores e Contato
- **Nélio Gomes** — Pesquisador Principal
- **Universidade de Brasília (UnB)** — Programa de Pós-Graduação em Ciências Farmacêuticas

Contribuições são bem-vindas! Abra uma issue ou pull request. 