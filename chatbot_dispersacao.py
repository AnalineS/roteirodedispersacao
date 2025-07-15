import os
import numpy as np
import torch
import hashlib
import logging
import pickle

from datetime import datetime
from transformers.pipelines import pipeline
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DispensacaoChatbot:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.qa_pipeline = None
        self.embedding_model = None
        self.chunks = []
        self.cache = {}
        self.load_models()
        self.load_pdf_content()

    def load_models(self):
        try:
            logger.info("Carregando modelos de IA...")
            self.qa_pipeline = pipeline(
                "question-answering",
                model="deepset/roberta-base-squad2",
                device=0 if torch.cuda.is_available() else -1
            )
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Modelos carregados com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {e}")
            raise

    def load_pdf_content(self):
        try:
            if not os.path.exists(self.pdf_path):
                logger.warning(f"PDF não encontrado: {self.pdf_path}")
                return

            text = self.extract_text_from_pdf(self.pdf_path)
            self.chunks = self.chunk_text(text)
            logger.info(f"PDF processado em {len(self.chunks)} trechos.")
        except Exception as e:
            logger.error(f"Erro ao processar PDF: {e}")

    def extract_text_from_pdf(self, path):
        try:
            reader = PdfReader(path)
            return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF: {e}")
            return ""

    def chunk_text(self, text, chunk_size=1500, overlap=300):
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            best_break = max(
                text.rfind(sep, start, end) for sep in ['\n\n', '. ', '\n', ' '] if text.rfind(sep, start, end) != -1
            )
            if best_break < start + chunk_size * 0.7:
                best_break = end
            chunks.append(text[start:best_break].strip())
            start = best_break - overlap

        return chunks

    def get_relevant_chunks(self, question, top_k=3):
        if not self.chunks:
            return []

        question_embedding = self.embedding_model.encode(question)
        chunk_embeddings = self.embedding_model.encode(self.chunks)

        similarities = np.dot(chunk_embeddings, question_embedding) / (
            np.linalg.norm(chunk_embeddings, axis=1) * np.linalg.norm(question_embedding)
        )

        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [self.chunks[i] for i in top_indices if similarities[i] > 0.1]

    def answer_question(self, question):
        cache_key = hashlib.md5(question.encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]

        relevant_chunks = self.get_relevant_chunks(question)
        context = " ".join(relevant_chunks)

        try:
            result = self.qa_pipeline(question=question, context=context, handle_impossible_answer=True)
            confidence = result.get("score", 0.0)
            answer = result.get("answer", "") if confidence > 0.2 else "Informação não encontrada com confiança suficiente."
        except Exception as e:
            logger.error(f"Erro na geração de resposta: {e}")
            answer = "Erro ao tentar responder."
            confidence = 0.0

        response = {
            "question": question,
            "answer": answer,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }

        self.cache[cache_key] = response
        return response
