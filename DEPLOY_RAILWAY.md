# 🚂 Deploy no Railway - Alternativa Gratuita

## ✅ Por que Railway?

- **Gratuito:** $5 de crédito mensal (suficiente para projetos pequenos)
- **Python nativo:** Suporte completo a Flask
- **Deploy automático:** Integração com GitHub
- **SSL gratuito:** HTTPS automático
- **Sem configuração complexa:** Deploy em 5 minutos

---

## 🚀 Passo a Passo - Railway

### 1️⃣ Preparar o Projeto

#### Criar `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python app_production.py",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

#### Criar `Procfile`:
```
web: python app_production.py
```

#### Atualizar `requirements.txt`:
```
flask==2.3.3
flask-cors==4.0.0
transformers==4.35.0
torch==2.1.0
sentence-transformers==2.2.2
PyPDF2==3.0.1
numpy==1.24.3
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
```

### 2️⃣ Criar Conta no Railway
- Acesse: [https://railway.app/](https://railway.app/)
- Faça login com GitHub
- Clique em "New Project"

### 3️⃣ Deploy
- Selecione "Deploy from GitHub repo"
- Escolha seu repositório
- Railway detectará automaticamente que é Python
- Clique em "Deploy"

### 4️⃣ Configurar Variáveis de Ambiente
No painel do Railway, adicione:
```
FLASK_ENV=production
PORT=8000
```

---

## 🎯 Vantagens do Railway

✅ **Deploy automático** do GitHub  
✅ **SSL gratuito** automático  
✅ **Domínio personalizado** gratuito  
✅ **Logs em tempo real**  
✅ **Escalabilidade** fácil  
✅ **Backup automático**  

---

## 📊 Comparação de Custos

| Plataforma | Plano Gratuito | Limitações |
|------------|----------------|------------|
| **Railway** | $5/mês crédito | 500 horas/mês |
| **Render** | Gratuito | 750 horas/mês |
| **Heroku** | Pago | $7/mês mínimo |
| **Vercel** | Gratuito | Sem Python |
| **Netlify** | Gratuito | Sem Python |

---

## 🔧 Configuração Adicional

### Para melhor performance:
```python
# No app_production.py
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### Health Check:
```python
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
```

---

## 🎉 Resultado

Após o deploy, você terá:
- **URL:** `https://seu-projeto.railway.app`
- **Deploy automático** a cada push no GitHub
- **Logs** em tempo real
- **Monitoramento** de performance

---

## 🆘 Troubleshooting

### Erro: "Build failed"
- Verifique se `requirements.txt` está correto
- Confirme se `Procfile` existe
- Verifique os logs no Railway

### Erro: "Port not found"
- Adicione `PORT=8000` nas variáveis de ambiente
- Confirme se o app está rodando na porta correta

### Erro: "Memory limit"
- Railway tem limite de 512MB no plano gratuito
- Otimize o modelo de IA se necessário 