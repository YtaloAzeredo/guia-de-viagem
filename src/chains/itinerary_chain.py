"""
Itinerary Chain - Responsável por gerar roteiros de viagem personalizados.
"""
from typing import Dict, List, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from ..config import Config


class ItineraryChain:
    """Chain especializada em criar roteiros de viagem."""
    
    def __init__(self, rag_system):
        """
        Inicializa a chain de roteiros.
        
        Args:
            rag_system: Sistema RAG para busca de informações
        """
        self.config = Config()
        self.rag_system = rag_system
        
        # Inicializa LLM
        self.llm = ChatGroq(
            groq_api_key=self.config.GROQ_API_KEY,
            model_name=self.config.GROQ_MODEL,
            temperature=0.3
        )
        
        # Template para geração de roteiros
        self.itinerary_template = PromptTemplate(
            input_variables=["query", "duration", "city", "interests", "locations", "user_preferences"],
            template="""
Você é um especialista em turismo e criação de roteiros personalizados.

SOLICITAÇÃO DO USUÁRIO: {query}

INFORMAÇÕES COLETADAS:
- Cidade: {city}
- Duração: {duration}
- Interesses: {interests}
- Preferências específicas: {user_preferences}

LOCAIS E ATRAÇÕES DISPONÍVEIS:
{locations}

INSTRUÇÕES:
1. Crie um roteiro detalhado e personalizado
2. Organize por dias e horários
3. Considere proximidade geográfica para otimizar deslocamentos
4. Inclua tempo estimado para cada atividade
5. Adicione dicas práticas e recomendações
6. Sugira opções alternativas quando possível
7. Considere horários de funcionamento e preços quando disponíveis

FORMATO DE RESPOSTA:
- Use formatação clara com cabeçalhos
- Organize por dias (Dia 1, Dia 2, etc.)
- Para cada local inclua: nome, tempo estimado, dicas importantes
- Adicione seção de dicas gerais ao final

ROTEIRO PERSONALIZADO:"""
        )
        
        # Cria a chain
        self.chain = (
            self.itinerary_template 
            | self.llm 
            | StrOutputParser()
        )
    
    def generate_itinerary(self, route_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera roteiro baseado nas informações de roteamento.
        
        Args:
            route_info: Informações do router sobre a consulta
            
        Returns:
            Dicionário com o roteiro gerado
        """
        query = route_info["original_query"]
        extracted_info = route_info["extracted_info"]
        
        # Extrai informações específicas
        cities = extracted_info.get("cities", [])
        duration = extracted_info.get("duration_days", 3)  # Default 3 dias
        interests = extracted_info.get("interests", [])
        
        # Define cidade principal
        main_city = cities[0] if cities else self._detect_city_from_query(query)
        
        if not main_city:
            return {
                "success": False,
                "error": "Cidade não especificada ou não suportada. Cidades disponíveis: " + 
                        ", ".join(self.config.SUPPORTED_CITIES)
            }
        
        # Busca locais relevantes usando RAG
        locations_data = self._get_relevant_locations(main_city, interests, duration)
        
        # Prepara informações para o template
        locations_text = self._format_locations_for_prompt(locations_data)
        interests_text = ", ".join(interests) if interests else "Geral"
        user_preferences = self._extract_user_preferences(query)
        
        try:
            # Gera roteiro
            itinerary_text = self.chain.invoke({
                "query": query,
                "duration": f"{duration} dias",
                "city": main_city,
                "interests": interests_text,
                "locations": locations_text,
                "user_preferences": user_preferences
            })
            
            return {
                "success": True,
                "itinerary": itinerary_text,
                "city": main_city,
                "duration_days": duration,
                "interests": interests,
                "locations_used": len(locations_data)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao gerar roteiro: {str(e)}"
            }
    
    def _detect_city_from_query(self, query: str) -> str:
        """Detecta cidade a partir da consulta."""
        query_lower = query.lower()
        for city in self.config.SUPPORTED_CITIES:
            if city.lower() in query_lower:
                return city
        return ""
    
    def _get_relevant_locations(self, city: str, interests: List[str], duration: int) -> List[Dict]:
        """Busca locais relevantes para o roteiro."""
        # Quantidade de locais baseada na duração
        num_locations = min(duration * 4, 15)  # Máximo 4 por dia, limite 15
        
        # Se há interesses específicos, busca por eles
        if interests:
            locations = []
            for interest in interests:
                search_query = f"{interest} {city}"
                results = self.rag_system.search_by_city(search_query, city, top_k=5)
                locations.extend(results)
            
            # Remove duplicatas
            seen_ids = set()
            unique_locations = []
            for loc in locations:
                if loc["id"] not in seen_ids:
                    unique_locations.append(loc)
                    seen_ids.add(loc["id"])
            
            locations = unique_locations[:num_locations]
        else:
            # Busca geral para a cidade
            search_query = f"pontos turísticos atrações {city}"
            locations = self.rag_system.search_by_city(search_query, city, top_k=num_locations)
        
        return locations
    
    def _format_locations_for_prompt(self, locations: List[Dict]) -> str:
        """Formata locais para o prompt."""
        if not locations:
            return "Nenhum local específico encontrado."
        
        formatted_locations = []
        for loc in locations:
            location_info = [
                f"NOME: {loc.get('nome', 'N/A')}",
                f"CATEGORIA: {loc.get('categoria', 'N/A')}",
                f"DESCRIÇÃO: {loc.get('descricao', 'N/A')}"
            ]
            
            if loc.get('horario'):
                location_info.append(f"HORÁRIO: {loc['horario']}")
            if loc.get('preco'):
                location_info.append(f"PREÇO: {loc['preco']}")
            if loc.get('tempo_visita'):
                location_info.append(f"TEMPO VISITA: {loc['tempo_visita']}")
            if loc.get('dicas'):
                location_info.append(f"DICAS: {loc['dicas']}")
            if loc.get('como_chegar'):
                location_info.append(f"COMO CHEGAR: {loc['como_chegar']}")
            
            formatted_locations.append("\n".join(location_info))
        
        return "\n\n---\n\n".join(formatted_locations)
    
    def _extract_user_preferences(self, query: str) -> str:
        """Extrai preferências específicas do usuário."""
        query_lower = query.lower()
        preferences = []
        
        # Detecta preferências comuns
        if "barato" in query_lower or "econômico" in query_lower:
            preferences.append("orçamento limitado")
        if "luxo" in query_lower or "premium" in query_lower:
            preferences.append("experiências premium")
        if "família" in query_lower or "criança" in query_lower:
            preferences.append("adequado para famílias")
        if "acessível" in query_lower or "mobilidade" in query_lower:
            preferences.append("acessibilidade")
        if "fotografia" in query_lower or "fotos" in query_lower:
            preferences.append("locais instagramáveis")
        
        return "; ".join(preferences) if preferences else "Preferências gerais"