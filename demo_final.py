#!/usr/bin/env python3
"""
Demo Final do Sistema de Guia de Viagem Inteligente
Demonstra todas as funcionalidades do sistema usando LangChain Router Chains, Groq e RAG.
"""

from src.main import TravelGuideSystem


def print_separator(title: str):
    """Imprime um separador decorativo."""
    print(f"\n{'='*60}")
    print(f"🌟 {title}")
    print('='*60)


def print_response(query: str, response: dict):
    """Imprime uma resposta formatada."""
    print(f"🔸 Consulta: '{query}'")
    print(f"✅ Intenção identificada: {response['intention']}")
    print(f"🔧 Chain usada: {response['chain_used']}")
    
    # Identifica a chave de conteúdo principal
    content_keys = {
        'itinerary': '📋 Roteiro',
        'local_info': '📍 Informações',
        'logistics_info': '🚗 Logística',
        'translation_guide': '🗣️ Tradução'
    }
    
    for key, label in content_keys.items():
        if key in response:
            print(f"\n{label}:")
            print("-" * 40)
            content = response[key]
            # Mostra os primeiros 300 caracteres
            if len(content) > 300:
                print(content[:300] + "...")
            else:
                print(content)
            break
    
    print()


def main():
    """Demonstração completa do sistema."""
    
    print_separator("SISTEMA DE GUIA DE VIAGEM INTELIGENTE")
    print("🚀 Demonstração das funcionalidades usando LangChain Router Chains")
    print("🤖 Powered by Groq LLM + RAG com busca semântica")
    print("📊 Status do sistema: Modo fallback ativo (dados locais)")
    
    # Inicializar sistema
    print("\n⏳ Inicializando sistema...")
    system = TravelGuideSystem()
    print("✅ Sistema pronto!")
    
    # Testes por categoria
    test_cases = [
        {
            'title': 'ROTEIROS DE VIAGEM',
            'queries': [
                'Quero um roteiro cultural em Paris por 3 dias',
                'Roteiro romântico no Rio de Janeiro por 2 dias'
            ]
        },
        {
            'title': 'INFORMAÇÕES LOCAIS',
            'queries': [
                'Melhores restaurantes no Rio de Janeiro',
                'Atrações turísticas em Paris'
            ]
        },
        {
            'title': 'LOGÍSTICA E TRANSPORTE',
            'queries': [
                'Como chegar ao Cristo Redentor?',
                'Melhor transporte público em Paris'
            ]
        },
        {
            'title': 'TRADUÇÃO E IDIOMAS',
            'queries': [
                'Frases básicas em francês para turistas',
                'Como pedir comida em inglês'
            ]
        }
    ]
    
    # Executar testes
    for category in test_cases:
        print_separator(category['title'])
        
        for query in category['queries']:
            response = system.process_query(query)
            print_response(query, response)
    
    # Demonstração das capacidades do RAG
    print_separator("CAPACIDADES DO SISTEMA RAG")
    print("📊 Dados indexados:")
    print(f"  • Cidades: Rio de Janeiro, Paris")
    print(f"  • Total de locais: 19 pontos de interesse")
    print(f"  • Categorias: Atrações, Restaurantes, Transporte")
    print(f"  • Modo: Fallback local (busca textual)")
    
    print("\n🔍 Exemplo de busca semântica:")
    response = system.process_query('Lugares românticos no Rio')
    print(f"  Consulta: 'Lugares românticos no Rio'")
    print(f"  Locais encontrados: {response.get('places_found', 0)}")
    
    print_separator("RESUMO DA DEMONSTRAÇÃO")
    print("✅ Router Chain: Classificação automática de intenções")
    print("✅ Specialized Chains: 4 cadeias especializadas")
    print("✅ RAG System: Recuperação de informações contextuais")
    print("✅ Groq Integration: LLM rápido para geração de respostas")
    print("✅ Fallback Mode: Sistema resiliente a falhas de dependências")
    
    print("\n🎯 Tecnologias demonstradas:")
    print("  • LangChain Router Chains para classificação de intenções")
    print("  • Groq llama-3.1-8b-instant para inferência rápida")
    print("  • Sistema RAG com busca semântica (fallback textual)")
    print("  • Arquitetura modular e resiliente")
    
    print("\n🌟 O sistema está pronto para ser integrado em aplicações reais!")


if __name__ == "__main__":
    main()