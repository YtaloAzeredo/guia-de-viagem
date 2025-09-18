"""
Arquivo de teste para verificar funcionalidades básicas do sistema.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import Mock, patch
from src.config import Config
from src.router import IntentionRouter, RouterChain


class TestConfig:
    """Testes para a classe Config."""
    
    def test_config_initialization(self):
        """Testa inicialização da configuração."""
        config = Config()
        
        # Verifica constantes básicas
        assert config.GROQ_MODEL == "llama3-8b-8192"
        assert config.EMBEDDING_DIMENSION == 384
        assert config.TOP_K_RESULTS == 5
        assert len(config.SUPPORTED_CITIES) >= 2
        assert len(config.INTENTIONS) == 4
    
    def test_intentions_mapping(self):
        """Testa mapeamento de intenções."""
        config = Config()
        
        expected_intentions = [
            "roteiro-viagem",
            "logistica-transporte", 
            "info-local",
            "traducao-idiomas"
        ]
        
        for intention in expected_intentions:
            assert intention in config.INTENTIONS
            assert len(config.INTENTIONS[intention]) > 0


class TestIntentionRouter:
    """Testes para classificação de intenções."""
    
    def setup_method(self):
        """Configura testes com mock do LLM."""
        with patch('src.router.ChatGroq') as mock_groq:
            mock_groq.return_value = Mock()
            self.router = IntentionRouter()
    
    def test_fallback_classification_roteiro(self):
        """Testa classificação fallback para roteiros."""
        queries = [
            "Quero um roteiro para Paris",
            "Plano de viagem para o Rio",
            "Itinerário de 3 dias",
            "O que visitar em Paris"
        ]
        
        for query in queries:
            result = self.router._fallback_classification(query)
            assert result == "roteiro-viagem"
    
    def test_fallback_classification_transporte(self):
        """Testa classificação fallback para transporte."""
        queries = [
            "Como chegar ao Cristo Redentor",
            "Onde fica o metrô",
            "Preço do táxi",
            "Como ir ao aeroporto"
        ]
        
        for query in queries:
            result = self.router._fallback_classification(query)
            assert result == "logistica-transporte"
    
    def test_fallback_classification_info_local(self):
        """Testa classificação fallback para informações locais."""
        queries = [
            "Horário do museu",
            "Preço do ingresso",
            "Melhores restaurantes",
            "Onde comer"
        ]
        
        for query in queries:
            result = self.router._fallback_classification(query)
            assert result == "info-local"
    
    def test_fallback_classification_traducao(self):
        """Testa classificação fallback para tradução."""
        queries = [
            "Como dizer obrigado em francês",
            "Frases úteis em inglês",
            "Traduzir cardápio",
            "Falar português"
        ]
        
        for query in queries:
            result = self.router._fallback_classification(query)
            assert result == "traducao-idiomas"


class TestRouterChain:
    """Testes para o RouterChain."""
    
    def setup_method(self):
        """Configura testes."""
        with patch('src.router.ChatGroq') as mock_groq:
            mock_groq.return_value = Mock()
            self.router_chain = RouterChain()
    
    def test_extract_query_info_cities(self):
        """Testa extração de cidades."""
        queries_cities = [
            ("Roteiro em Paris", ["Paris"]),
            ("Viagem ao Rio de Janeiro", ["Rio de Janeiro"]),
            ("Paris e Rio", ["Paris", "Rio de Janeiro"])
        ]
        
        for query, expected_cities in queries_cities:
            info = self.router_chain._extract_query_info(query, "roteiro-viagem")
            for city in expected_cities:
                assert city in info["cities"]
    
    def test_extract_query_info_duration(self):
        """Testa extração de duração."""
        queries_duration = [
            ("Roteiro de 3 dias", 3),
            ("Viagem por 5 dias", 5), 
            ("Plano para 1 dia", 1)
        ]
        
        for query, expected_duration in queries_duration:
            info = self.router_chain._extract_query_info(query, "roteiro-viagem")
            assert info.get("duration_days") == expected_duration
    
    def test_extract_query_info_interests(self):
        """Testa extração de interesses."""
        queries_interests = [
            ("Roteiro cultural", ["cultural"]),
            ("Viagem gastronômica", ["gastronomico"]),
            ("Aventura em família", ["aventura", "familiar"])
        ]
        
        for query, expected_interests in queries_interests:
            info = self.router_chain._extract_query_info(query, "roteiro-viagem")
            for interest in expected_interests:
                assert interest in info["interests"]


# Testes de integração simplificados
def test_system_imports():
    """Testa se todas as importações funcionam corretamente."""
    try:
        from src.config import Config
        from src.router import RouterChain, IntentionRouter
        from src.chains.itinerary_chain import ItineraryChain
        from src.chains.logistics_chain import LogisticsChain
        from src.chains.local_info_chain import LocalInfoChain
        from src.chains.translation_chain import TranslationChain
        
        # Testa inicialização básica
        config = Config()
        assert config is not None
        
        print("✅ Todas as importações funcionaram corretamente")
        
    except ImportError as e:
        pytest.fail(f"Falha na importação: {e}")


def test_config_validation():
    """Testa validação de configuração."""
    config = Config()
    
    # Mock das variáveis necessárias para teste
    original_groq = config.GROQ_API_KEY
    original_pinecone = config.PINECONE_API_KEY
    
    try:
        config.GROQ_API_KEY = None
        config.PINECONE_API_KEY = None
        
        with pytest.raises(ValueError):
            config.validate()
            
    finally:
        config.GROQ_API_KEY = original_groq
        config.PINECONE_API_KEY = original_pinecone


if __name__ == "__main__":
    """Executa testes básicos sem pytest."""
    
    print("🧪 EXECUTANDO TESTES BÁSICOS")
    print("="*50)
    
    try:
        # Teste de importações
        print("1. Testando importações...")
        test_system_imports()
        
        # Teste de configuração  
        print("2. Testando configurações...")
        config = Config()
        print(f"   ✅ Modelo configurado: {config.GROQ_MODEL}")
        print(f"   ✅ Cidades suportadas: {len(config.SUPPORTED_CITIES)}")
        print(f"   ✅ Intenções configuradas: {len(config.INTENTIONS)}")
        
        # Teste de router básico
        print("3. Testando router básico...")
        with patch('src.router.ChatGroq') as mock_groq:
            mock_groq.return_value = Mock()
            router = IntentionRouter()
            
            # Testa classificação fallback
            test_queries = [
                ("Roteiro para Paris", "roteiro-viagem"),
                ("Como chegar lá", "logistica-transporte"),
                ("Restaurantes bons", "info-local"),
                ("Frases em francês", "traducao-idiomas")
            ]
            
            for query, expected in test_queries:
                result = router._fallback_classification(query)
                assert result == expected, f"Falha para '{query}': esperado {expected}, obtido {result}"
            
        print("   ✅ Router funcionando corretamente")
        
        print(f"\n{'='*50}")
        print("🎉 TODOS OS TESTES BÁSICOS PASSARAM!")
        print("\n📝 Para executar testes completos:")
        print("   pip install pytest")
        print("   pytest test_basic.py -v")
        
    except Exception as e:
        print(f"❌ Erro nos testes: {str(e)}")
        import traceback
        traceback.print_exc()