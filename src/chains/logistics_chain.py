"""
Logistics Chain - Responsável por informações de transporte e acomodação.
"""
from typing import Dict, Any, List
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from ..config import Config


class LogisticsChain:
    """Chain especializada em logística de viagens."""
    
    def __init__(self, rag_system):
        """
        Inicializa a chain de logística.
        
        Args:
            rag_system: Sistema RAG para busca de informações
        """
        self.config = Config()
        self.rag_system = rag_system
        
        # Inicializa LLM
        self.llm = ChatGroq(
            groq_api_key=self.config.GROQ_API_KEY,
            model_name=self.config.GROQ_MODEL,
            temperature=0.2  # Baixa temperatura para informações precisas
        )
        
        # Template para informações logísticas
        self.logistics_template = PromptTemplate(
            input_variables=["query", "transport_info", "city_info"],
            template="""
Você é um especialista em logística de viagens e transporte.

PERGUNTA DO USUÁRIO: {query}

INFORMAÇÕES DE TRANSPORTE DISPONÍVEIS:
{transport_info}

INFORMAÇÕES GERAIS DA CIDADE:
{city_info}

INSTRUÇÕES:
1. Responda de forma clara e direta à pergunta sobre logística
2. Inclua informações práticas sobre transporte, horários e preços
3. Forneça alternativas quando possível
4. Adicione dicas de segurança e eficiência
5. Mencione apps úteis ou cartões de transporte
6. Se for sobre acomodação, sugira áreas recomendadas

TIPOS DE INFORMAÇÃO A INCLUIR:
- Como chegar ao destino específico
- Opções de transporte (preços, horários, duração)
- Dicas para evitar multidões ou economizar
- Informações sobre acessibilidade
- Alternativas em caso de problemas

RESPOSTA DETALHADA:"""
        )
        
        # Cria a chain
        self.chain = (
            self.logistics_template 
            | self.llm 
            | StrOutputParser()
        )
    
    def get_logistics_info(self, route_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fornece informações logísticas baseadas na consulta.
        
        Args:
            route_info: Informações do router sobre a consulta
            
        Returns:
            Dicionário com informações logísticas
        """
        query = route_info["original_query"]
        extracted_info = route_info["extracted_info"]
        
        # Detecta cidade da consulta
        cities = extracted_info.get("cities", [])
        main_city = cities[0] if cities else self._detect_city_from_query(query)
        
        # Busca informações de transporte relevantes
        transport_info = self._get_transport_info(query, main_city)
        city_info = self._get_city_logistics_info(main_city)
        
        try:
            # Gera resposta logística
            response = self.chain.invoke({
                "query": query,
                "transport_info": transport_info,
                "city_info": city_info
            })
            
            return {
                "success": True,
                "response": response,
                "city": main_city,
                "type": self._classify_logistics_type(query)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter informações logísticas: {str(e)}"
            }
    
    def _detect_city_from_query(self, query: str) -> str:
        """Detecta cidade a partir da consulta."""
        query_lower = query.lower()
        for city in self.config.SUPPORTED_CITIES:
            if city.lower() in query_lower:
                return city
        return ""
    
    def _get_transport_info(self, query: str, city: str) -> str:
        """Busca informações específicas de transporte."""
        # Palavras-chave para diferentes tipos de transporte
        transport_keywords = {
            "metro": ["metrô", "metro", "subway", "underground"],
            "bus": ["ônibus", "bus", "autobus"],
            "taxi": ["táxi", "taxi", "uber", "lyft", "99"],
            "bike": ["bicicleta", "bike", "ciclovia", "velib"],
            "walk": ["andar", "caminhada", "pé", "walking"],
            "airport": ["aeroporto", "airport", "voo", "chegada"]
        }
        
        query_lower = query.lower()
        relevant_transports = []
        
        # Identifica tipos de transporte mencionados
        for transport_type, keywords in transport_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                relevant_transports.append(transport_type)
        
        # Se nenhum tipo específico, busca geral
        if not relevant_transports:
            relevant_transports = ["metro", "bus", "taxi"]
        
        # Busca informações no RAG
        transport_results = []
        if city:
            for transport_type in relevant_transports:
                search_query = f"transporte {transport_type} {city}"
                results = self.rag_system.search_by_city(search_query, city, top_k=3)
                transport_results.extend(results)
        
        # Formata informações encontradas
        if transport_results:
            return self._format_transport_info(transport_results)
        else:
            return self._get_general_transport_info(city)
    
    def _get_city_logistics_info(self, city: str) -> str:
        """Obtém informações logísticas gerais da cidade."""
        if not city:
            return "Cidade não especificada."
        
        # Busca informações gerais de transporte da cidade
        search_query = f"transporte sistema {city}"
        results = self.rag_system.search_by_city(search_query, city, top_k=5)
        
        if results:
            return self._format_city_info(results, city)
        else:
            return self._get_default_city_info(city)
    
    def _format_transport_info(self, transport_results: List[Dict]) -> str:
        """Formata informações de transporte para o prompt."""
        if not transport_results:
            return "Informações de transporte não encontradas."
        
        formatted_info = []
        for result in transport_results:
            info_parts = [
                f"TIPO: {result.get('nome', 'N/A')}",
                f"CATEGORIA: {result.get('categoria', 'N/A')}"
            ]
            
            if result.get('descricao'):
                info_parts.append(f"DESCRIÇÃO: {result['descricao']}")
            if result.get('horario'):
                info_parts.append(f"HORÁRIOS: {result['horario']}")
            if result.get('preco'):
                info_parts.append(f"PREÇOS: {result['preco']}")
            if result.get('dicas'):
                info_parts.append(f"DICAS: {result['dicas']}")
            if result.get('como_chegar'):
                info_parts.append(f"COMO USAR: {result['como_chegar']}")
            
            formatted_info.append("\n".join(info_parts))
        
        return "\n\n---\n\n".join(formatted_info)
    
    def _format_city_info(self, results: List[Dict], city: str) -> str:
        """Formata informações gerais da cidade."""
        info_parts = [f"INFORMAÇÕES GERAIS - {city}"]
        
        for result in results:
            if result.get('categoria') == 'Transporte':
                info_parts.append(f"- {result.get('nome', 'N/A')}: {result.get('descricao', 'N/A')}")
        
        return "\n".join(info_parts)
    
    def _get_general_transport_info(self, city: str) -> str:
        """Informações gerais de transporte quando não há dados específicos."""
        general_info = {
            "Rio de Janeiro": """
TRANSPORTE NO RIO DE JANEIRO:
- Metrô: Sistema limpo e seguro, conecta principais pontos turísticos
- Ônibus: Rede extensa mas pode ser confusa para turistas
- Táxi/Uber: Disponível em toda cidade, use apps para segurança
- BRT: Sistema de ônibus rápido em corredores exclusivos
- Dicas: Compre RioCard para facilitar, evite horários de pico
            """,
            "Paris": """
TRANSPORTE EM PARIS:
- Metrô: Extenso sistema com 16 linhas, muito eficiente
- Ônibus: Complementa metrô, boa opção para ver a cidade
- Vélib': Sistema de bikes compartilhadas, ecológico e barato
- Táxi/Uber: Disponível mas caro, use apenas quando necessário
- Dicas: Compre Navigo Easy, apps Citymapper e RATP são úteis
            """
        }
        
        return general_info.get(city, f"Informações específicas de {city} não disponíveis.")
    
    def _get_default_city_info(self, city: str) -> str:
        """Informações padrão quando não há dados específicos."""
        return f"Informações logísticas gerais para {city} não disponíveis no banco de dados."
    
    def _classify_logistics_type(self, query: str) -> str:
        """Classifica o tipo de consulta logística."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["como chegar", "transporte", "metrô", "ônibus"]):
            return "transport"
        elif any(word in query_lower for word in ["hotel", "hospedagem", "acomodação", "onde ficar"]):
            return "accommodation"
        elif any(word in query_lower for word in ["aeroporto", "voo", "chegada", "transfer"]):
            return "airport_transfer"
        else:
            return "general_logistics"