"""
Translation Chain - Responsável por guias de tradução e frases úteis.
"""
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from ..config import Config


class TranslationChain:
    """Chain especializada em tradução e guias de idiomas."""
    
    def __init__(self, rag_system=None):
        """
        Inicializa a chain de tradução.
        
        Args:
            rag_system: Sistema RAG (opcional para esta chain)
        """
        self.config = Config()
        self.rag_system = rag_system
        
        # Inicializa LLM
        self.llm = ChatGroq(
            groq_api_key=self.config.GROQ_API_KEY,
            model_name=self.config.GROQ_MODEL,
            temperature=0.1  # Muito baixa para traduções precisas
        )
        
        # Template para guias de tradução
        self.translation_template = PromptTemplate(
            input_variables=["query", "target_language", "context", "travel_scenario"],
            template="""
Você é um especialista em idiomas e tradução para viajantes.

SOLICITAÇÃO: {query}
IDIOMA ALVO: {target_language}
CONTEXTO DA VIAGEM: {context}
CENÁRIO: {travel_scenario}

INSTRUÇÕES:
1. Forneça traduções precisas e contextualmente apropriadas
2. Inclua pronúncia aproximada em português quando útil
3. Organize por categorias relevantes para turistas
4. Adicione dicas culturais importantes
5. Inclua variações regionais quando relevante
6. Forneça exemplos de uso prático

CATEGORIAS SUGERIDAS:
- Cumprimentos básicos
- Pedindo informações
- No restaurante
- No hotel
- Transporte
- Emergências
- Compras
- Números e horários
- Frases de cortesia

FORMATO DE RESPOSTA:
- Use formatação clara com categorias
- Inclua a frase em português, tradução e pronúncia
- Adicione contexto cultural quando importante
- Sugira gestos ou expressões não-verbais úteis

GUIA DE TRADUÇÃO PRÁTICO:"""
        )
        
        # Cria a chain
        self.chain = (
            self.translation_template 
            | self.llm 
            | StrOutputParser()
        )
    
    def get_translation_guide(self, route_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera guia de tradução baseado na consulta.
        
        Args:
            route_info: Informações do router sobre a consulta
            
        Returns:
            Dicionário com guia de tradução
        """
        query = route_info["original_query"]
        extracted_info = route_info["extracted_info"]
        
        # Detecta idioma alvo e contexto
        target_language = self._detect_target_language(query, extracted_info)
        context = self._extract_travel_context(query, extracted_info)
        travel_scenario = self._identify_travel_scenario(query)
        
        try:
            # Gera guia de tradução
            translation_guide = self.chain.invoke({
                "query": query,
                "target_language": target_language,
                "context": context,
                "travel_scenario": travel_scenario
            })
            
            return {
                "success": True,
                "translation_guide": translation_guide,
                "target_language": target_language,
                "travel_context": context,
                "scenario": travel_scenario
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao gerar guia de tradução: {str(e)}"
            }
    
    def _detect_target_language(self, query: str, extracted_info: Dict) -> str:
        """Detecta o idioma alvo da tradução."""
        query_lower = query.lower()
        
        # Mapeamento de idiomas comuns para turistas
        language_keywords = {
            "francês": "Francês",
            "frances": "Francês", 
            "french": "Francês",
            "inglês": "Inglês",
            "ingles": "Inglês",
            "english": "Inglês",
            "espanhol": "Espanhol",
            "spanish": "Espanhol",
            "italiano": "Italiano",
            "italian": "Italiano",
            "alemão": "Alemão",
            "alemao": "Alemão",
            "german": "Alemão",
            "japonês": "Japonês",
            "japones": "Japonês",
            "japanese": "Japonês"
        }
        
        # Procura por menções diretas do idioma
        for keyword, language in language_keywords.items():
            if keyword in query_lower:
                return language
        
        # Tenta detectar pela cidade mencionada
        cities = extracted_info.get("cities", [])
        city_languages = {
            "Paris": "Francês",
            "Rio de Janeiro": "Português (para estrangeiros)"
        }
        
        if cities:
            main_city = cities[0]
            if main_city in city_languages:
                return city_languages[main_city]
        
        # Detecta pela menção de país
        country_keywords = {
            "frança": "Francês",
            "france": "Francês", 
            "brasil": "Português",
            "brazil": "Português",
            "estados unidos": "Inglês",
            "eua": "Inglês",
            "usa": "Inglês"
        }
        
        for country, language in country_keywords.items():
            if country in query_lower:
                return language
        
        # Default: se não detectou, pergunta sobre idiomas gerais para turistas
        return "Idiomas úteis para turistas (Inglês, Francês, Espanhol)"
    
    def _extract_travel_context(self, query: str, extracted_info: Dict) -> str:
        """Extrai contexto da viagem da consulta."""
        context_parts = []
        
        # Contexto da cidade/país
        cities = extracted_info.get("cities", [])
        if cities:
            context_parts.append(f"Viagem para {cities[0]}")
        
        # Contexto de duração
        duration = extracted_info.get("duration_days")
        if duration:
            context_parts.append(f"Estadia de {duration} dias")
        
        # Contexto de interesses
        interests = extracted_info.get("interests", [])
        if interests:
            context_parts.append(f"Interesses: {', '.join(interests)}")
        
        # Contexto específico da consulta
        query_lower = query.lower()
        specific_contexts = []
        
        if "negócios" in query_lower or "trabalho" in query_lower:
            specific_contexts.append("viagem de negócios")
        elif "família" in query_lower or "criança" in query_lower:
            specific_contexts.append("viagem em família")
        elif "romântico" in query_lower or "lua de mel" in query_lower:
            specific_contexts.append("viagem romântica")
        elif "estudante" in query_lower or "mochileiro" in query_lower:
            specific_contexts.append("viagem econômica")
        
        if specific_contexts:
            context_parts.extend(specific_contexts)
        
        return "; ".join(context_parts) if context_parts else "Viagem turística geral"
    
    def _identify_travel_scenario(self, query: str) -> str:
        """Identifica o cenário específico de uso das traduções."""
        query_lower = query.lower()
        
        # Cenários específicos
        scenarios = {
            "restaurante": ["restaurante", "comer", "comida", "cardápio", "garçom"],
            "hotel": ["hotel", "hospedagem", "check-in", "quarto", "recepção"],
            "transporte": ["transporte", "metrô", "ônibus", "táxi", "aeroporto"],
            "compras": ["compras", "loja", "preço", "pagar", "shopping"],
            "emergência": ["emergência", "ajuda", "médico", "polícia", "hospital"],
            "turismo": ["turismo", "atração", "museu", "ingresso", "informação"],
            "direções": ["direção", "como chegar", "onde fica", "localização", "endereço"]
        }
        
        for scenario, keywords in scenarios.items():
            if any(keyword in query_lower for keyword in keywords):
                return scenario.title()
        
        # Cenário geral se não identificou específico
        return "Situações gerais de turismo"
    
    def get_emergency_phrases(self, target_language: str) -> Dict[str, str]:
        """Retorna frases essenciais de emergência em qualquer idioma."""
        # Esta função pode ser chamada diretamente para situações de emergência
        emergency_template = PromptTemplate(
            input_variables=["language"],
            template="""
Forneça as 10 frases mais importantes de emergência em {language} para turistas:

1. "Socorro/Ajuda"
2. "Preciso de um médico"
3. "Chame a polícia"
4. "Onde fica o hospital?"
5. "Não falo [idioma local]"
6. "Estou perdido"
7. "Posso usar seu telefone?"
8. "Onde fica a embaixada do Brasil?"
9. "Preciso de ajuda urgente"
10. "Obrigado pela ajuda"

Para cada frase, inclua:
- Tradução exata
- Pronúncia aproximada em português
- Contexto de uso

FRASES DE EMERGÊNCIA:"""
        )
        
        emergency_chain = emergency_template | self.llm | StrOutputParser()
        
        try:
            result = emergency_chain.invoke({"language": target_language})
            return {
                "success": True,
                "emergency_phrases": result,
                "language": target_language
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao gerar frases de emergência: {str(e)}"
            }