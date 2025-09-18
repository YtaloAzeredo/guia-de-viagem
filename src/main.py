"""
Sistema principal do Guia de Viagem Inteligente.
Orquestra todas as cadeias especializadas através do router.
"""
from typing import Dict, Any, Optional
from .config import Config
from .rag import setup_rag_system
from .router import RouterChain
from .chains.itinerary_chain import ItineraryChain
from .chains.logistics_chain import LogisticsChain
from .chains.local_info_chain import LocalInfoChain
from .chains.translation_chain import TranslationChain


class TravelGuideSystem:
    """Sistema principal do guia de viagem inteligente."""
    
    def __init__(self):
        """Inicializa o sistema completo."""
        print("Inicializando Sistema de Guia de Viagem...")
        
        # Configurações
        self.config = Config()
        self.config.validate()
        
        # Sistema RAG
        print("Configurando sistema RAG...")
        self.rag_system = setup_rag_system()
        
        # Router principal
        print("Inicializando router...")
        self.router = RouterChain()
        
        # Cadeias especializadas
        print("Configurando cadeias especializadas...")
        self.chains = {
            "itinerary_chain": ItineraryChain(self.rag_system),
            "logistics_chain": LogisticsChain(self.rag_system),
            "local_info_chain": LocalInfoChain(self.rag_system),
            "translation_chain": TranslationChain(self.rag_system)
        }
        
        print("Sistema inicializado com sucesso!")
    
    def process_query(self, query: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Processa uma consulta do usuário através do sistema completo.
        
        Args:
            query: Consulta do usuário
            verbose: Se deve incluir informações detalhadas de debug
            
        Returns:
            Dicionário com a resposta processada
        """
        try:
            # 1. Roteamento da consulta
            if verbose:
                print(f"\n🔍 Analisando consulta: '{query}'")
            
            route_info = self.router.route_query(query)
            
            if verbose:
                print(f"📋 Intenção detectada: {route_info['intention']}")
                print(f"🎯 Chain alvo: {route_info['chain_target']}")
                if route_info['extracted_info']:
                    print(f"📊 Informações extraídas: {route_info['extracted_info']}")
            
            # 2. Processamento pela chain apropriada
            chain_name = route_info['chain_target']
            chain = self.chains.get(chain_name)
            
            if not chain:
                return {
                    "success": False,
                    "error": f"Chain '{chain_name}' não encontrada",
                    "route_info": route_info
                }
            
            if verbose:
                print(f"⚙️ Processando com {chain_name}...")
            
            # Executa processamento específico
            result = self._execute_chain(chain_name, chain, route_info)
            
            # 3. Prepara resposta final
            response = {
                "success": result.get("success", False),
                "intention": route_info["intention"],
                "chain_used": chain_name,
                "route_info": route_info if verbose else None
            }
            
            if result.get("success"):
                # Adiciona resultado específico da chain
                if chain_name == "itinerary_chain":
                    response.update({
                        "type": "itinerary",
                        "itinerary": result.get("itinerary"),
                        "city": result.get("city"),
                        "duration_days": result.get("duration_days"),
                        "interests": result.get("interests", [])
                    })
                
                elif chain_name == "logistics_chain":
                    response.update({
                        "type": "logistics",
                        "logistics_info": result.get("response"),
                        "city": result.get("city"),
                        "logistics_type": result.get("type")
                    })
                
                elif chain_name == "local_info_chain":
                    response.update({
                        "type": "local_info",
                        "local_info": result.get("response"),
                        "city": result.get("city"),
                        "places_found": result.get("places_found", 0)
                    })
                
                elif chain_name == "translation_chain":
                    response.update({
                        "type": "translation",
                        "translation_guide": result.get("translation_guide"),
                        "target_language": result.get("target_language"),
                        "travel_context": result.get("travel_context")
                    })
            else:
                response["error"] = result.get("error", "Erro desconhecido")
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro no processamento: {str(e)}",
                "intention": "unknown"
            }
    
    def _execute_chain(self, chain_name: str, chain: Any, route_info: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a chain apropriada baseada no tipo."""
        try:
            if chain_name == "itinerary_chain":
                return chain.generate_itinerary(route_info)
            elif chain_name == "logistics_chain":
                return chain.get_logistics_info(route_info)
            elif chain_name == "local_info_chain":
                return chain.get_local_info(route_info)
            elif chain_name == "translation_chain":
                return chain.get_translation_guide(route_info)
            else:
                return {
                    "success": False,
                    "error": f"Tipo de chain desconhecido: {chain_name}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na execução da chain {chain_name}: {str(e)}"
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o sistema."""
        return {
            "system_name": "Guia de Viagem Inteligente",
            "supported_cities": self.config.SUPPORTED_CITIES,
            "available_intentions": self.config.INTENTIONS,
            "chains_available": list(self.chains.keys()),
            "rag_system_active": bool(self.rag_system),
            "model": self.config.GROQ_MODEL
        }
    
    def reload_rag_data(self) -> Dict[str, Any]:
        """Recarrega dados no sistema RAG."""
        try:
            self.rag_system.load_and_index_data(force_reload=True)
            return {
                "success": True,
                "message": "Dados RAG recarregados com sucesso"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao recarregar dados RAG: {str(e)}"
            }


class TravelGuideInterface:
    """Interface simplificada para interação com o sistema."""
    
    def __init__(self):
        """Inicializa a interface."""
        self.system = TravelGuideSystem()
        print("\n✅ Sistema de Guia de Viagem pronto para uso!")
        self._print_welcome_message()
    
    def _print_welcome_message(self):
        """Exibe mensagem de boas-vindas."""
        print("\n" + "="*60)
        print("🌍 BEM-VINDO AO GUIA DE VIAGEM INTELIGENTE 🌍")
        print("="*60)
        print("\n🎯 O que posso ajudar você hoje?")
        print("\n📍 Exemplos de consultas:")
        print("  • 'Quero um roteiro cultural em Paris por 3 dias'")
        print("  • 'Como chegar ao Cristo Redentor?'")
        print("  • 'Melhores restaurantes no Rio de Janeiro'")
        print("  • 'Frases úteis em francês para turistas'")
        print(f"\n🏙️ Cidades disponíveis: {', '.join(self.system.config.SUPPORTED_CITIES)}")
        print("\n💡 Digite 'sair' para encerrar ou 'info' para informações do sistema")
        print("-"*60)
    
    def start_interactive_mode(self):
        """Inicia modo interativo de conversa."""
        while True:
            try:
                # Recebe consulta do usuário
                user_input = input("\n🗣️ Sua pergunta: ").strip()
                
                # Comandos especiais
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    print("\n👋 Obrigado por usar o Guia de Viagem! Boa viagem!")
                    break
                
                if user_input.lower() in ['info', 'informacoes']:
                    self._show_system_info()
                    continue
                
                if user_input.lower() in ['reload', 'recarregar']:
                    print("\n🔄 Recarregando dados...")
                    result = self.system.reload_rag_data()
                    if result["success"]:
                        print("✅ Dados recarregados com sucesso!")
                    else:
                        print(f"❌ Erro: {result['error']}")
                    continue
                
                if not user_input:
                    print("Por favor, digite uma pergunta válida.")
                    continue
                
                # Processa consulta
                print("\n🤔 Analisando sua pergunta...")
                response = self.system.process_query(user_input, verbose=True)
                
                # Exibe resposta
                self._display_response(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Sistema encerrado pelo usuário. Até logo!")
                break
            except Exception as e:
                print(f"\n❌ Erro inesperado: {str(e)}")
                print("Por favor, tente novamente.")
    
    def _show_system_info(self):
        """Exibe informações do sistema."""
        info = self.system.get_system_info()
        print("\n" + "="*50)
        print("ℹ️ INFORMAÇÕES DO SISTEMA")
        print("="*50)
        print(f"📊 Sistema: {info['system_name']}")
        print(f"🤖 Modelo: {info['model']}")
        print(f"🏙️ Cidades: {', '.join(info['supported_cities'])}")
        print(f"🎯 Intenções disponíveis:")
        for intention, description in info['available_intentions'].items():
            print(f"   • {intention}: {description}")
        print("-"*50)
    
    def _display_response(self, response: Dict[str, Any]):
        """Exibe resposta formatada do sistema."""
        print("\n" + "="*60)
        
        if not response.get("success", False):
            print("❌ ERRO")
            print("="*60)
            print(f"🚨 {response.get('error', 'Erro desconhecido')}")
            return
        
        # Cabeçalho baseado no tipo
        response_type = response.get("type", "unknown")
        icons = {
            "itinerary": "🗺️ ROTEIRO PERSONALIZADO",
            "logistics": "🚗 INFORMAÇÕES LOGÍSTICAS", 
            "local_info": "📍 INFORMAÇÕES LOCAIS",
            "translation": "🗣️ GUIA DE TRADUÇÃO"
        }
        
        print(icons.get(response_type, "📋 RESPOSTA"))
        print("="*60)
        
        # Conteúdo específico por tipo
        if response_type == "itinerary":
            if response.get("city"):
                print(f"🏙️ Cidade: {response['city']}")
            if response.get("duration_days"):
                print(f"⏱️ Duração: {response['duration_days']} dias")
            if response.get("interests"):
                print(f"🎯 Interesses: {', '.join(response['interests'])}")
            print("\n" + response.get("itinerary", ""))
            
        elif response_type == "logistics":
            if response.get("city"):
                print(f"🏙️ Cidade: {response['city']}")
            print("\n" + response.get("logistics_info", ""))
            
        elif response_type == "local_info":
            if response.get("city"):
                print(f"🏙️ Cidade: {response['city']}")
            if response.get("places_found"):
                print(f"📊 Locais encontrados: {response['places_found']}")
            print("\n" + response.get("local_info", ""))
            
        elif response_type == "translation":
            if response.get("target_language"):
                print(f"🗣️ Idioma: {response['target_language']}")
            if response.get("travel_context"):
                print(f"🎯 Contexto: {response['travel_context']}")
            print("\n" + response.get("translation_guide", ""))
        
        print("\n" + "-"*60)
    
    def process_single_query(self, query: str, verbose: bool = False) -> Dict[str, Any]:
        """Processa uma única consulta (para uso programático)."""
        return self.system.process_query(query, verbose)


# Função principal para execução do sistema
def main():
    """Função principal para executar o sistema."""
    try:
        interface = TravelGuideInterface()
        interface.start_interactive_mode()
    except Exception as e:
        print(f"\n❌ Erro fatal na inicialização: {str(e)}")
        print("Verifique se todas as configurações estão corretas no arquivo .env")


if __name__ == "__main__":
    main()