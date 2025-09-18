"""
Configurações centrais do sistema de guia de viagem.
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    """Configurações centralizadas do sistema."""
    
    # APIs
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "guia-viagem")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Para embeddings (alternativa)
    
    # Modelos
    GROQ_MODEL = "llama-3.1-8b-instant"  # Modelo Groq padrão
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Modelo para embeddings
    
    # Dimensões do vetor (para o modelo all-MiniLM-L6-v2)
    EMBEDDING_DIMENSION = 384
    
    # Configurações RAG
    TOP_K_RESULTS = 5  # Número de resultados similares a recuperar
    SIMILARITY_THRESHOLD = 0.7  # Threshold mínimo de similaridade
    
    # Categorias de intenções
    INTENTIONS = {
        "roteiro-viagem": "Gerar roteiros de viagem personalizados",
        "logistica-transporte": "Informações sobre transporte e acomodação",
        "info-local": "Informações específicas sobre locais e atrações",
        "traducao-idiomas": "Guias de tradução e frases úteis"
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
            raise ValueError(f"Variáveis de ambiente obrigatórias não encontradas: {missing}")
        
        return True