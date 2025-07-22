# Chatbot Tese Hanseníase

Chatbot inteligente baseado na tese sobre roteiro de dispensação para hanseníase, com duas personalidades: Dr. Gasnelio (professor sério) e Gá (amigo descontraído).

## 🚀 Funcionalidades

- **Duas Personalidades**: 
  - **Dr. Gasnelio**: Respostas técnicas e formais
  - **Gá**: Explicações simples e descontraídas
- **IA Gratuita**: Usa modelo Hugging Face (deepset/roberta-base-squad2)
- **Baseado em PDF**: Responde exclusivamente com informações da tese
- **Interface Moderna**: Design responsivo e intuitivo

## 📋 Pré-requisitos

- Python 3.9+
- PDF da tese: `Roteiro-de-Dsispensacao-Hanseniase-F.docx.pdf`

## 🛠️ Instalação

### Windows (Recomendado)
1. **Baixe o PDF da tese** do link fornecido:
   - Link: https://drive.google.com/drive/folders/1435FhEIp_yOwtretv-G-ZQpNFY-f6tzr?usp=drive_link
   - Salve como: `Roteiro-de-Dsispensacao-Hanseniase-F.docx.pdf` na raiz do projeto

2. **Execute o instalador**:
   ```cmd
   setup.bat
   ```

3. **Inicie o chatbot**:
   ```cmd
   start.bat
   ```

### Linux/Mac
```bash
# Clone o repositório
git clone <url-do-repositorio>
cd gemini-v2

# Baixe o PDF da tese do link fornecido
# Salve como: Roteiro-de-Dsispensacao-Hanseniase-F.docx.pdf

# Execute o instalador automático
python3 install_and_check.py
```

### Instalação Manual
1. **Clone o repositório**:
```bash
git clone <url-do-repositorio>
cd gemini-v2
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Coloque o PDF da tese** na raiz do projeto:
```
gemini-v2/
├── Roteiro-de-Dsispensacao-Hanseniase-F.docx.pdf
├── app_optimized.py
├── requirements.txt
└── ...
```

4. **Analise a compatibilidade**:
```bash
python3 pdf_analyzer.py
```

## 🚀 Execução

### Desenvolvimento
```bash
python app_optimized.py
```

### Produção
```bash
gunicorn app_optimized:app
```

### Script de Inicialização
```bash
./start.sh
```

O servidor estará disponível em `http://localhost:5000`

## 📡 Endpoints da API

### POST `/api/chat`
Envia uma pergunta para o chatbot.

**Request:**
```json
{
  "question": "Qual a dose de rifampicina?",
  "personality_id": "dr_gasnelio"
}
```

**Response:**
```json
{
  "answer": "Dr. Gasnelio responde:\n\nA dose de rifampicina...",
  "persona": "dr_gasnelio",
  "confidence": 0.85,
  "timestamp": "2025-01-13T10:30:00",
  "question": "Qual a dose de rifampicina?"
}
```

### GET `/api/health`
Verifica o status da API.

### GET `/api/info`
Informações sobre a API.

## 🎭 Personalidades

### Dr. Gasnelio
- Tom sério e técnico
- Linguagem formal
- Foco em precisão científica
- Inclui nível de confiança

### Gá
- Tom descontraído e amigável
- Linguagem simples
- Explicações acessíveis
- Usa emojis e expressões informais

## 🔧 Configuração

### Variáveis de Ambiente
- `PORT`: Porta do servidor (padrão: 5000)
- `FLASK_ENV`: Ambiente (development/production)

### Configuração Automática
O sistema analisa automaticamente o PDF e gera configurações otimizadas:
- **PDFs Pequenos** (< 50k chars): Processamento direto
- **PDFs Médios** (50k-100k chars): Chunking básico + cache
- **PDFs Grandes** (> 100k chars): Chunking avançado + cache + busca semântica

### Personalização
Edite `app_optimized.py` ou `optimized_config.json` para:
- Alterar o modelo de IA
- Modificar as personalidades
- Ajustar parâmetros de confiança
- Configurar chunking e cache

## 📦 Deploy

### Heroku
```bash
heroku create
git push heroku main
```

### Railway
```bash
railway login
railway init
railway up
```

### Render
1. Conecte o repositório
2. Configure o build command: `pip install -r requirements.txt`
3. Configure o start command: `gunicorn app:app`

## 🐛 Troubleshooting

### Erro: "PDF não encontrado"
- Verifique se o arquivo PDF está na raiz do projeto
- Confirme o nome do arquivo: `Roteiro-de-Dsispensacao-Hanseniase-F.docx.pdf`
- Execute: `python3 install_and_check.py` para verificação automática

### Erro: "Modelo não carregado"
- Verifique a conexão com internet (para baixar o modelo)
- Confirme se as dependências foram instaladas corretamente
- Execute: `pip install -r requirements.txt`

### Erro: "Memória insuficiente"
- O modelo pode consumir muita RAM
- Considere usar um servidor com mais memória
- Para PDFs grandes, use configurações otimizadas

### Erro: "Resposta muito lenta"
- Execute: `python3 pdf_analyzer.py` para análise
- Ajuste configurações em `optimized_config.json`
- Considere reduzir `chunk_size` ou aumentar `overlap`

### Erro: "Baixa precisão"
- Aumente `confidence_threshold` na configuração
- Habilite `use_semantic_search` para PDFs complexos
- Verifique se o PDF tem texto extraível

## 📝 Licença

Este projeto é parte da tese de doutorado sobre roteiro de dispensação para hanseníase.

## 🗂️ Histórico de Versões e Documentação

Este projeto passou por diversas fases de desenvolvimento e modularização. Abaixo estão os principais marcos e referências de documentação:

- **2023-2024:** Estrutura inicial do chatbot, integração com PDF e personalidades.
- **2024-05:** Refatoração para modularização, centralização de utilitários e remoção de duplicidades.
- **2024-06:** Limpeza de scripts antigos, consolidação de documentação e atualização do README principal.
- **Guias e tutoriais antigos:**
  - Diversos arquivos `.md` de deploy, troubleshooting e migração foram consolidados neste README.
  - Para histórico detalhado, consulte o repositório ou os arquivos arquivados na pasta `relatorio-disp/`.

Caso precise de informações sobre versões anteriores, consulte o histórico do repositório ou entre em contato com os autores.

## 👥 Autores

- **Nélio Gomes** - Pesquisador Principal
- **Universidade de Brasília (UnB)** - Programa de Pós-Graduação em Ciências Farmacêuticas

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request. 