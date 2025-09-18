"""
Router Chain para classificação de intenções de consultas turísticas.
"""
from typing import Dict, Any, Optional

try:
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_groq import ChatGroq
except ImportError:
    # Mock classes para quando as dependências não estão instaladas
    class PromptTemplate:
        def __init__(self, **kwargs):
            pass
    class StrOutputParser:
        pass
    class ChatGroq:
        def __init__(self, **kwargs):
            pass

try:
    from .config import Config
except ImportError:
    # Importação absoluta como fallback
    from config import Config


class IntentionRouter:
    """Router responsável por classificar intenções de consultas."""
    
    def __init__(self):
        """Inicializa o router de intenções."""
        self.config = Config()
        
        # Só valida se as dependências estão disponíveis
        try:
            self.config.validate()
            
            # Inicializa LLM Groq
            self.llm = ChatGroq(
                groq_api_key=self.config.GROQ_API_KEY,
                model_name=self.config.GROQ_MODEL,
                temperature=0.1  # Baixa temperatura para classificação consistente
            )
        except (ValueError, Exception):
            # Modo fallback sem LLM
            self.llm = None
        
        # Template e chain só se LLM disponível
        if self.llm is not None:
            # Template para classificação de intenções
            self.classification_template = PromptTemplate(
                input_variables=["query", "intentions"],
                template="""
Você é um especialista em classificação de intenções para consultas de turismo.

Analise a consulta do usuário e classifique-a em uma das seguintes categorias:

{intentions}

CONSULTA DO USUÁRIO: "{query}"

INSTRUÇÕES:
1. Analise cuidadosamente a consulta
2. Identifique a intenção principal
3. Responda APENAS com uma das categorias listadas acima
4. Seja preciso e consistente

CATEGORIA:"""
            )
            
            # Cria a chain de classificação
            self.classification_chain = (
                self.classification_template 
                | self.llm 
                | StrOutputParser()
            )
        else:
            self.classification_template = None
            self.classification_chain = None
    
    def classify_intention(self, query: str) -> str:
        """
        Classifica a intenção da consulta do usuário.
        
        Args:
            query: Consulta do usuário
            
        Returns:
            Categoria da intenção classificada
        """
        # Se LLM disponível, usa classificação com IA
        if self.classification_chain is not None:
            # Prepara descrições das intenções
            intentions_text = self._format_intentions()
            
            try:
                # Executa classificação
                result = self.classification_chain.invoke({
                    "query": query,
                    "intentions": intentions_text
                })
                
                # Limpa e valida resultado
                classified_intention = result.strip().lower()
                
                # Verifica se a classificação é válida
                valid_intentions = list(self.config.INTENTIONS.keys())
                
                # Tenta match exato primeiro
                if classified_intention in valid_intentions:
                    return classified_intention
                
                # Tenta match parcial
                for intention in valid_intentions:
                    if intention in classified_intention or classified_intention in intention:
                        return intention
                
                # Fallback: usa heurísticas baseadas em palavras-chave
                return self._fallback_classification(query)
                
            except Exception as e:
                print(f"Erro na classificação: {e}")
                return self._fallback_classification(query)
        else:
            # Usa apenas classificação fallback
            return self._fallback_classification(query)
    
    def _format_intentions(self) -> str:
        """Formata as intenções para o prompt."""
        intentions_list = []
        for intention, description in self.config.INTENTIONS.items():
            intentions_list.append(f"- {intention}: {description}")
        
        return "\n".join(intentions_list)
    
    def _fallback_classification(self, query: str) -> str:
        """
        Sistema de fallback para classificação baseado em palavras-chave.
        
        Args:
            query: Consulta do usuário
            
        Returns:
            Categoria mais provável
        """
        query_lower = query.lower()
        
        # Palavras-chave para cada categoria
        keywords = {
            "roteiro-viagem": [
                "roteiro", "itinerário", "viagem", "dias", "plano", "programação",
                "cronograma", "agenda", "visitar", "conhecer", "turismo", "passeio",
                "tour", "rota", "percurso"
            ],
            "logistica-transporte": [
                "como chegar", "transporte", "ônibus", "metrô", "táxi", "uber",
                "avião", "voo", "hotel", "hospedagem", "acomodação", "reserva",
                "estadia", "onde ficar", "transfer", "aeroporto", "estação"
            ],
            "info-local": [
                "restaurante", "comida", "comer", "onde", "horário", "preço",
                "ingresso", "entrada", "custo", "museu", "atração", "ponto turístico",
                "informações", "detalhes", "funcionamento", "aberto", "fechado",
                "localização", "endereço"
            ],
            "traducao-idiomas": [
                "tradução", "traduzir", "idioma", "língua", "falar", "dizer",
                "frases", "palavras", "comunicação", "linguagem", "expressões",
                "como falar", "como dizer", "francês", "inglês", "espanhol",
                "português"
            ]
        }
        
        # Conta matches por categoria
        scores = {}
        for category, category_keywords in keywords.items():
            score = sum(1 for keyword in category_keywords if keyword in query_lower)
            scores[category] = score
        
        # Retorna categoria com maior score, ou default
        if scores:
            best_category = max(scores, key=scores.get)
            if scores[best_category] > 0:
                return best_category
        
        # Default fallback
        return "info-local"
    
    def get_intention_description(self, intention: str) -> str:
        """Retorna descrição da intenção."""
        return self.config.INTENTIONS.get(intention, "Intenção desconhecida")
    
    def get_available_intentions(self) -> Dict[str, str]:
        """Retorna todas as intenções disponíveis."""
        return self.config.INTENTIONS.copy()


class RouterChain:
    """Chain principal para roteamento de consultas."""
    
    def __init__(self):
        """Inicializa o router chain."""
        self.intention_router = IntentionRouter()
    
    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Roteia consulta para cadeia apropriada.
        
        Args:
            query: Consulta do usuário
            
        Returns:
            Dicionário com informações de roteamento
        """
        # Classifica intenção
        intention = self.intention_router.classify_intention(query)
        
        # Extrai informações adicionais da consulta
        extracted_info = self._extract_query_info(query, intention)
        
        return {
            "intention": intention,
            "original_query": query,
            "chain_target": self._get_chain_name(intention),
            "extracted_info": extracted_info,
            "description": self.intention_router.get_intention_description(intention)
        }
    
    def _extract_query_info(self, query: str, intention: str) -> Dict[str, Any]:
        """Extrai informações específicas da consulta."""
        query_lower = query.lower()
        info = {}
        
        # Extrai cidades mencionadas
        cities = []
        for city in self.intention_router.config.SUPPORTED_CITIES:
            if city.lower() in query_lower:
                cities.append(city)
        info["cities"] = cities
        
        # Extrai duração (para roteiros)
        if intention == "roteiro-viagem":
            import re
            duration_patterns = [
                r'(\d+)\s*dias?',
                r'(\d+)\s*dia',
                r'por\s*(\d+)\s*dias?'
            ]
            for pattern in duration_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    info["duration_days"] = int(match.group(1))
                    break
        
        # Extrai tipo de interesse
        interest_keywords = {
            "cultural": ["cultural", "cultura", "museu", "história", "arte"],
            "gastronomico": ["gastronomico", "comida", "restaurante", "culinária"],
            "aventura": ["aventura", "esporte", "ativo", "natureza"],
            "romantico": ["romântico", "casal", "romance", "lua de mel"],
            "familiar": ["família", "criança", "familiar", "kids"]
        }
        
        interests = []
        for interest, keywords in interest_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                interests.append(interest)
        info["interests"] = interests
        
        return info
    
    def _get_chain_name(self, intention: str) -> str:
        """Mapeia intenção para nome da chain."""
        chain_mapping = {
            "roteiro-viagem": "itinerary_chain",
            "logistica-transporte": "logistics_chain",
            "info-local": "local_info_chain",
            "traducao-idiomas": "translation_chain"
        }
        return chain_mapping.get(intention, "local_info_chain")