import streamlit as st
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import logging

# Função para health check
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port+1), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

# Inicia o health server em uma thread separada
if os.getenv("RENDER"):
    start_health_server()
    logging.getLogger("streamlit").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)

ASTRA_DB_ENDPOINT = os.environ.get("ASTRA_DB_ENDPOINT")
ASTRA_DB_TOKEN = os.environ.get("ASTRA_DB_TOKEN")
OPENROUTER_API_KEYROTEIRO_DISP_KIMIE_K2FREE = os.environ.get("OPENROUTER_API_KEYROTEIRO_DISP_KIMIE_K2FREE")

logging.info(f"ASTRA_DB_ENDPOINT set: {bool(ASTRA_DB_ENDPOINT)}")
logging.info(f"ASTRA_DB_TOKEN set: {bool(ASTRA_DB_TOKEN)}")
logging.info(f"OPENROUTER_API_KEYROTEIRO_DISP_KIMIE_K2FREE set: {bool(OPENROUTER_API_KEYROTEIRO_DISP_KIMIE_K2FREE)}")

# Seu app Streamlit normal
st.title("Streamlit App Friendly")
st.write("Bem-vindo ao app!") 