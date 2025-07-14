# Guia para Atualizar o render.yaml no GitHub

## Problema Atual
O Render está tentando executar `gunicorn app_production:app` em vez de `gunicorn app_simple:app`, porque o arquivo `render.yaml` no GitHub não está atualizado.

## Solução

### 1. Instalar o Git (se necessário)
- Baixe o Git de: https://git-scm.com/download/win
- Instale seguindo as instruções padrão
- Reinicie o PowerShell após a instalação

### 2. Abrir o PowerShell no diretório do projeto
```powershell
cd "C:\Users\Ana\Meu Drive\Imagens site Junin\gemini v2"
```

### 3. Inicializar o repositório Git (se necessário)
```powershell
git init
git remote add origin https://github.com/AnalineS/siteroteirodedispersacao.git
```

### 4. Verificar se o render.yaml está correto
O arquivo `render.yaml` deve conter:
```yaml
services:
  - type: web
    name: roteiro-dispersacao
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app_simple:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.13.4
      - key: FLASK_ENV
        value: production
```

### 5. Adicionar arquivos ao Git
```powershell
git add .
```

### 6. Fazer commit
```powershell
git commit -m "Atualizar render.yaml para usar app_simple:app"
```

### 7. Enviar para o GitHub
```powershell
git push -u origin main
```

### 8. Fazer novo deploy no Render
1. Acesse: https://dashboard.render.com
2. Vá para o serviço "roteiro-dispersacao"
3. Clique em "Manual Deploy"
4. Aguarde o build e deploy

### 9. Verificar o site
O site deve ficar disponível em: https://roteiro-dispersacao.onrender.com

## Arquivos Importantes
- ✅ `render.yaml` - Configuração do Render
- ✅ `app_simple.py` - Aplicação Flask simplificada
- ✅ `requirements.txt` - Dependências Python
- ✅ `runtime.txt` - Versão do Python

## Comandos Alternativos (se houver problemas)
Se o push falhar, tente:
```powershell
git pull origin main --allow-unrelated-histories
git push -u origin main
```

Ou force o push (use com cuidado):
```powershell
git push -u origin main --force
``` 