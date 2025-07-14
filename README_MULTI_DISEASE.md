# 🏥 Chatbot Multi-Doenças

Sistema de chatbot inteligente que responde perguntas sobre múltiplas doenças baseado em PDFs de teses e roteiros médicos.

## ✨ Características

- **Múltiplas Doenças**: Suporte para várias doenças simultaneamente
- **Duas Personalidades**: Dr. Gasnelio (técnico) e Gá (descontraído)
- **IA Avançada**: Modelo de linguagem para respostas precisas
- **Interface Moderna**: Design responsivo e intuitivo
- **Cache Inteligente**: Otimização de performance
- **Fácil Expansão**: Adicione novas doenças facilmente

## 🚀 Instalação Rápida

### Windows
```bash
# 1. Instalar dependências
setup_multi_disease.bat

# 2. Iniciar servidor
start_multi_disease.bat
```

### Linux/Mac
```bash
# 1. Instalar dependências
pip install flask flask-cors transformers torch sentence-transformers PyPDF2 numpy

# 2. Criar pasta para PDFs
mkdir pdfs

# 3. Iniciar servidor
python app_multi_disease.py
```

## 📁 Estrutura do Projeto

```
gemini v2/
├── app_multi_disease.py          # Backend principal
├── setup_multi_disease.bat       # Instalador Windows
├── start_multi_disease.bat       # Inicializador Windows
├── add_disease.py               # Gerenciador de doenças
├── pdfs/                        # Pasta para PDFs
│   ├── hanseniase.pdf
│   ├── diabetes.pdf
│   └── hipertensao.pdf
└── README_MULTI_DISEASE.md      # Esta documentação
```

## 🏥 Doenças Configuradas

### 1. Hanseníase
- **PDF**: `pdfs/hanseniase.pdf`
- **Descrição**: Doença infecciosa crônica causada pela bactéria Mycobacterium leprae
- **Palavras-chave**: hanseníase, lepra, mycobacterium, bacilo de hansen

### 2. Diabetes
- **PDF**: `pdfs/diabetes.pdf`
- **Descrição**: Doença metabólica caracterizada por níveis elevados de glicose no sangue
- **Palavras-chave**: diabetes, glicemia, insulina, hiperglicemia

### 3. Hipertensão
- **PDF**: `pdfs/hipertensao.pdf`
- **Descrição**: Pressão arterial elevada de forma persistente
- **Palavras-chave**: hipertensão, pressão alta, hipertensão arterial, hta

## 👨‍⚕️ Personalidades

### Dr. Gasnelio
- **Estilo**: Sério e técnico
- **Linguagem**: Médica e formal
- **Ideal para**: Profissionais de saúde e estudantes

### Gá
- **Estilo**: Descontraído e simples
- **Linguagem**: Informal e acessível
- **Ideal para**: Público geral e pacientes

## 🔧 Como Adicionar Novas Doenças

### Método 1: Script Automático
```bash
python add_disease.py
```

### Método 2: Manual
1. **Adicionar PDF**: Coloque o PDF na pasta `pdfs/`
2. **Editar código**: Adicione a doença em `app_multi_disease.py`
3. **Reiniciar**: Execute `start_multi_disease.bat`

### Exemplo de Configuração
```python
"cancer": {
    "name": "Câncer",
    "pdf_path": "pdfs/cancer.pdf",
    "description": "Doença caracterizada pelo crescimento descontrolado de células",
    "keywords": ["câncer", "tumor", "neoplasia", "oncologia"],
    "personalities": {
        "dr_gasnelio": {
            "name": "Dr. Gasnelio",
            "style": "sério e técnico",
            "greeting": "Olá! Sou o Dr. Gasnelio, especialista em câncer. Como posso ajudá-lo hoje?",
            "fallback": "Baseado na literatura médica sobre câncer..."
        },
        "ga": {
            "name": "Gá",
            "style": "descontraído e simples",
            "greeting": "Oi! Sou o Gá! 😊 Vou te ajudar a entender sobre câncer...",
            "fallback": "Olha, sobre isso eu não tenho certeza..."
        }
    }
}
```

## 🌐 Uso

### 1. Acessar o Sistema
- Abra: `http://localhost:5000`
- Selecione uma doença
- Escolha uma personalidade
- Clique em "Iniciar Chat"

### 2. Fazer Perguntas
- Digite perguntas sobre a doença selecionada
- O chatbot responderá baseado no PDF específico
- Respostas incluem nível de confiança e fonte

### 3. APIs Disponíveis
```bash
# Listar doenças
GET /api/diseases

# Listar personalidades de uma doença
GET /api/diseases/{disease_id}/personalities

# Fazer pergunta
POST /api/chat
{
    "question": "Qual é o tratamento para hanseníase?",
    "disease_id": "hanseniase",
    "personality_id": "dr_gasnelio"
}

# Verificar saúde do sistema
GET /api/health
```

## ⚙️ Configurações

### Parâmetros de IA
- **Modelo**: `deepset/roberta-base-squad2`
- **Chunk Size**: 2000 caracteres
- **Overlap**: 200 caracteres
- **Confiança Mínima**: 35%
- **Cache**: Habilitado

### Otimizações
- **Embeddings**: `all-MiniLM-L6-v2`
- **Similaridade**: Cosseno
- **Top-k**: 3 chunks mais relevantes
- **Fallback**: Respostas padrão por personalidade

## 📊 Monitoramento

### Logs
- Erros de carregamento de PDFs
- Performance de respostas
- Uso de cache
- Tempo de resposta

### Métricas
- Número de doenças ativas
- PDFs carregados
- Modelos funcionando
- Status do servidor

## 🔍 Troubleshooting

### Problema: PDF não encontrado
```
Solução: Verifique se o PDF está na pasta 'pdfs' com o nome correto
```

### Problema: Erro de modelo
```
Solução: Execute setup_multi_disease.bat para reinstalar dependências
```

### Problema: Servidor não inicia
```
Solução: Verifique se Python 3.8+ está instalado
```

### Problema: Respostas genéricas
```
Solução: Verifique se o PDF contém informações relevantes
```

## 🚀 Deploy

### Local
```bash
python app_multi_disease.py
```

### Produção
```bash
# Usando Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_multi_disease:app

# Usando Docker
docker build -t chatbot-multi-disease .
docker run -p 5000:5000 chatbot-multi-disease
```

## 📈 Roadmap

- [ ] Interface administrativa
- [ ] Upload de PDFs via web
- [ ] Análise de sentimentos
- [ ] Integração com APIs médicas
- [ ] Suporte a múltiplos idiomas
- [ ] Relatórios de uso
- [ ] Backup automático de dados

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 📞 Suporte

- **Email**: suporte@chatbot-multi-disease.com
- **Issues**: GitHub Issues
- **Documentação**: Este README

---

**Desenvolvido com ❤️ para melhorar o acesso à informação médica** 