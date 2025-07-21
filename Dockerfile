FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# As variáveis ASTRA_DB_ENDPOINT, ASTRA_DB_TOKEN e OPENROUTER_API_KEYROTEIRO_DISP_KIMIE_K2FREE devem ser passadas como env no deploy
COPY . .
EXPOSE 10000
CMD ["streamlit", "run", "streamlit_app_friendly.py", "--server.port=10000", "--server.address=0.0.0.0"] 