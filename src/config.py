"""
Configurações centrais do sistema de guia de viagem.
"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()


class Config:
    # APIs
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "guia-viagem")

    # Modelos
    GROQ_MODEL = "llama-3.1-8b-instant"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

    # Configurações RAG
    EMBEDDING_DIMENSION = 384
    TOP_K_RESULTS = 5
    SIMILARITY_THRESHOLD = 0.7

    # Intenções suportadas
    INTENTIONS = {
        "roteiro-viagem": "Gerar roteiros de viagem personalizados",
        "logistica-transporte": "Informações sobre transporte e acomodação",
        "info-local": "Informações específicas sobre locais e atrações",
        "traducao-idiomas": "Guias de tradução e frases úteis",
    }

    # Cidades suportadas
    SUPPORTED_CITIES = ["Rio de Janeiro", "Paris"]

    @classmethod
    def validate(cls):
        """Valida se as configurações essenciais estão presentes."""
        required_vars = ["GROQ_API_KEY", "PINECONE_API_KEY"]
        missing = []

        for var in required_vars:
            if not getattr(cls, var):
                missing.append(var)

        if missing:
            raise ValueError(
                f"Variáveis de ambiente obrigatórias não encontradas: {missing}"
            )

        return True
