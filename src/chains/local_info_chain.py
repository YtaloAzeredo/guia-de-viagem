"""
Local Info Chain - Responsável por informações específicas sobre locais.
"""
from typing import Dict, Any, List
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from ..config import Config


class LocalInfoChain:
    """Chain especializada em informações locais específicas."""
    
    def __init__(self, rag_system):
        """
        Inicializa a chain de informações locais.
        
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
        
        # Template para informações locais
        self.local_info_template = PromptTemplate(
            input_variables=["query", "relevant_places", "additional_context"],
            template="""
Você é um especialista local e guia turístico experiente.

PERGUNTA DO USUÁRIO: {query}

LOCAIS E INFORMAÇÕES RELEVANTES ENCONTRADAS:
{relevant_places}

CONTEXTO ADICIONAL:
{additional_context}

INSTRUÇÕES:
1. Responda de forma precisa e detalhada à pergunta específica
2. Use as informações encontradas como base principal
3. Inclua detalhes práticos: horários, preços, localização
4. Adicione dicas úteis e recomendações pessoais
5. Mencione alternativas próximas quando relevante
6. Seja específico sobre como chegar e o que esperar
7. Inclua avisos importantes (segurança, reservas necessárias, etc.)

FORMATO DA RESPOSTA:
- Resposta direta à pergunta
- Informações detalhadas sobre cada local mencionado
- Dicas práticas e recomendações
- Informações complementares relevantes

RESPOSTA ESPECIALIZADA:"""
        )
        
        # Cria a chain
        self.chain = (
            self.local_info_template 
            | self.llm 
            | StrOutputParser()
        )
    
    def get_local_info(self, route_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fornece informações locais específicas baseadas na consulta.
        
        Args:
            route_info: Informações do router sobre a consulta
            
        Returns:
            Dicionário com informações locais
        """
        query = route_info["original_query"]
        extracted_info = route_info["extracted_info"]
        
        # Detecta cidade e categoria da consulta
        cities = extracted_info.get("cities", [])
        main_city = cities[0] if cities else self._detect_city_from_query(query)
        
        # Busca locais relevantes
        relevant_places = self._search_relevant_places(query, main_city)
        additional_context = self._get_additional_context(query, main_city)
        
        try:
            # Gera resposta com informações locais
            response = self.chain.invoke({
                "query": query,
                "relevant_places": relevant_places,
                "additional_context": additional_context
            })
            
            return {
                "success": True,
                "response": response,
                "city": main_city,
                "places_found": len(relevant_places.split("---")) if relevant_places else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter informações locais: {str(e)}"
            }
    
    def _detect_city_from_query(self, query: str) -> str:
        """Detecta cidade a partir da consulta."""
        query_lower = query.lower()
        for city in self.config.SUPPORTED_CITIES:
            if city.lower() in query_lower:
                return city
        return ""
    
    def _search_relevant_places(self, query: str, city: str) -> str:
        """Busca locais relevantes para a consulta."""
        # Se cidade específica for mencionada
        if city:
            results = self.rag_system.search_by_city(query, city, top_k=5)
        else:
            # Busca geral em todas as cidades
            results = self.rag_system.search_similar(query, top_k=8)
        
        if results:
            return self._format_places_info(results)
        else:
            # Tenta busca mais ampla se não encontrou resultados
            broader_query = self._create_broader_query(query)
            results = self.rag_system.search_similar(broader_query, top_k=5)
            return self._format_places_info(results) if results else "Nenhuma informação específica encontrada."
    
    def _create_broader_query(self, query: str) -> str:
        """Cria consulta mais ampla se a busca específica não retornar resultados."""
        query_lower = query.lower()
        
        # Mapeia termos específicos para termos mais amplos
        broader_terms = {
            "vegano": "restaurante comida",
            "japonês": "restaurante comida",
            "italiano": "restaurante comida",
            "barato": "restaurante preço",
            "luxo": "restaurante fino",
            "noturno": "bar restaurante noite",
            "criança": "família atividade",
            "arte": "museu galeria cultura",
            "história": "museu cultural",
            "natureza": "parque área verde",
            "shopping": "compras loja",
        }
        
        for specific, broader in broader_terms.items():
            if specific in query_lower:
                return broader
        
        # Se não encontrou mapeamento, usa palavras-chave gerais
        return "ponto turístico atração"
    
    def _format_places_info(self, places: List[Dict]) -> str:
        """Formata informações dos locais para o prompt."""
        if not places:
            return "Nenhum local encontrado."
        
        formatted_places = []
        for place in places:
            place_info = [
                f"NOME: {place.get('nome', 'N/A')}",
                f"CIDADE: {place.get('cidade', 'N/A')}",
                f"CATEGORIA: {place.get('categoria', 'N/A')}",
                f"DESCRIÇÃO: {place.get('descricao', 'N/A')}"
            ]
            
            # Adiciona informações específicas se disponíveis
            optional_fields = [
                ('endereco', 'ENDEREÇO'),
                ('horario', 'HORÁRIO'),
                ('preco', 'PREÇO'),
                ('tempo_visita', 'TEMPO DE VISITA'),
                ('dicas', 'DICAS'),
                ('como_chegar', 'COMO CHEGAR')
            ]
            
            for field, label in optional_fields:
                if place.get(field):
                    place_info.append(f"{label}: {place[field]}")
            
            # Adiciona score de similaridade se disponível
            if place.get('similarity_score'):
                score_percent = round(place['similarity_score'] * 100, 1)
                place_info.append(f"RELEVÂNCIA: {score_percent}%")
            
            formatted_places.append("\n".join(place_info))
        
        return "\n\n---\n\n".join(formatted_places)
    
    def _get_additional_context(self, query: str, city: str) -> str:
        """Obtém contexto adicional relevante para a consulta."""
        context_parts = []
        
        # Contexto sobre a cidade
        if city:
            context_parts.append(f"Consulta sobre {city}")
            
            # Informações gerais sobre a cidade baseadas na query
            city_overview = self.rag_system.get_city_overview(city)
            if city_overview:
                categories = set(place.get('categoria', '') for place in city_overview[:5])
                context_parts.append(f"Categorias disponíveis em {city}: {', '.join(filter(None, categories))}")
        
        # Contexto sobre tipo de consulta
        query_lower = query.lower()
        query_context = []
        
        if any(word in query_lower for word in ["restaurante", "comer", "comida"]):
            query_context.append("Consulta sobre gastronomia")
        if any(word in query_lower for word in ["museu", "cultura", "arte", "história"]):
            query_context.append("Consulta sobre cultura e arte")
        if any(word in query_lower for word in ["praia", "parque", "natureza"]):
            query_context.append("Consulta sobre atividades ao ar livre")
        if any(word in query_lower for word in ["noite", "bar", "festa"]):
            query_context.append("Consulta sobre vida noturna")
        
        if query_context:
            context_parts.append("Tipo de interesse: " + ", ".join(query_context))
        
        # Contexto sobre preferências específicas
        preferences = []
        if "barato" in query_lower or "econômico" in query_lower:
            preferences.append("Opções econômicas")
        if "luxo" in query_lower or "premium" in query_lower:
            preferences.append("Opções premium")
        if "família" in query_lower or "criança" in query_lower:
            preferences.append("Adequado para famílias")
        
        if preferences:
            context_parts.append("Preferências: " + ", ".join(preferences))
        
        return "\n".join(context_parts) if context_parts else "Consulta geral sobre informações locais."