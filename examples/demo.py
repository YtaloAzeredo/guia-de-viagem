"""
Exemplos de uso do Sistema de Guia de Viagem.
Demonstra diferentes tipos de consultas e funcionalidades.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.main import TravelGuideInterface


def run_example_queries():
    """Executa uma série de consultas de exemplo."""
    
    print("🧪 EXECUTANDO EXEMPLOS DE USO")
    print("="*60)
    
    # Inicializa sistema
    try:
        interface = TravelGuideInterface()
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        print("Verifique se as variáveis de ambiente estão configuradas corretamente.")
        return
    
    # Exemplos de consultas por categoria
    example_queries = [
        # Roteiros de viagem
        {
            "category": "ROTEIRO DE VIAGEM",
            "queries": [
                "Quero um roteiro cultural em Paris por 3 dias",
                "Roteiro romântico no Rio de Janeiro por 5 dias",
                "Plano de viagem gastronômico em Paris por 2 dias"
            ]
        },
        
        # Logística e transporte
        {
            "category": "LOGÍSTICA E TRANSPORTE", 
            "queries": [
                "Como chegar ao Cristo Redentor?",
                "Qual o melhor transporte público em Paris?",
                "Como ir do aeroporto ao centro do Rio de Janeiro?"
            ]
        },
        
        # Informações locais
        {
            "category": "INFORMAÇÕES LOCAIS",
            "queries": [
                "Melhores restaurantes veganos em Paris",
                "Horário de funcionamento do Louvre",
                "Preço dos ingressos para o Pão de Açúcar",
                "Restaurantes baratos no Rio de Janeiro"
            ]
        },
        
        # Tradução e idiomas
        {
            "category": "TRADUÇÃO E IDIOMAS",
            "queries": [
                "Frases úteis em francês para turistas",
                "Como pedir comida em francês",
                "Frases de emergência em inglês"
            ]
        }
    ]
    
    # Executa exemplos
    for category_info in example_queries:
        print(f"\n🔸 {category_info['category']}")
        print("-" * 40)
        
        for i, query in enumerate(category_info['queries'], 1):
            print(f"\n{i}. Consulta: '{query}'")
            
            try:
                response = interface.process_single_query(query, verbose=False)
                
                if response.get("success"):
                    print(f"   ✅ Sucesso - Intenção: {response['intention']}")
                    print(f"   🔧 Chain usada: {response['chain_used']}")
                    
                    # Mostra preview da resposta baseado no tipo
                    response_type = response.get("type")
                    if response_type == "itinerary":
                        city = response.get("city", "N/A")
                        duration = response.get("duration_days", "N/A")
                        print(f"   📋 Roteiro para {city} ({duration} dias)")
                    elif response_type == "logistics":
                        city = response.get("city", "N/A") 
                        print(f"   🚗 Informações logísticas para {city}")
                    elif response_type == "local_info":
                        places = response.get("places_found", 0)
                        print(f"   📍 {places} locais encontrados")
                    elif response_type == "translation":
                        language = response.get("target_language", "N/A")
                        print(f"   🗣️ Guia de tradução em {language}")
                        
                else:
                    print(f"   ❌ Erro: {response.get('error', 'Desconhecido')}")
                    
            except Exception as e:
                print(f"   💥 Exceção: {str(e)}")
    
    print(f"\n{'='*60}")
    print("🎉 EXEMPLOS CONCLUÍDOS!")
    print("Todos os tipos de consulta foram testados.")


def test_interactive_mode():
    """Testa o modo interativo com consultas pré-definidas."""
    
    print("\n🧪 TESTE DO MODO INTERATIVO")
    print("="*50)
    
    # Consultas de teste
    test_queries = [
        "Roteiro cultural em Paris por 3 dias",
        "Como chegar ao Cristo Redentor",
        "Melhores restaurantes no Rio",
        "Frases em francês para turistas"
    ]
    
    try:
        interface = TravelGuideInterface()
        
        print("\n🤖 Simulando interação do usuário...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Teste {i} ---")
            print(f"Consulta simulada: '{query}'")
            
            response = interface.process_single_query(query)
            
            if response.get("success"):
                print("✅ Processamento bem-sucedido")
                print(f"Intenção detectada: {response['intention']}")
            else:
                print(f"❌ Falha: {response.get('error')}")
        
        print(f"\n{'='*50}")
        print("✅ Teste do modo interativo concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")


def benchmark_system_performance():
    """Testa performance do sistema com múltiplas consultas."""
    
    import time
    
    print("\n⏱️ BENCHMARK DE PERFORMANCE")
    print("="*50)
    
    # Consultas para benchmark
    benchmark_queries = [
        "Roteiro em Paris",
        "Como chegar ao Louvre", 
        "Restaurantes em Ipanema",
        "Traduzir obrigado para francês",
        "Transporte público no Rio"
    ]
    
    try:
        interface = TravelGuideInterface()
        
        total_time = 0
        successful_queries = 0
        
        print(f"\nExecutando {len(benchmark_queries)} consultas...")
        
        for i, query in enumerate(benchmark_queries, 1):
            start_time = time.time()
            
            response = interface.process_single_query(query)
            
            end_time = time.time()
            query_time = end_time - start_time
            total_time += query_time
            
            if response.get("success"):
                successful_queries += 1
                status = "✅"
            else:
                status = "❌"
            
            print(f"{status} Consulta {i}: {query_time:.2f}s - '{query[:30]}...'")
        
        # Estatísticas
        avg_time = total_time / len(benchmark_queries)
        success_rate = (successful_queries / len(benchmark_queries)) * 100
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   ⏱️ Tempo total: {total_time:.2f}s")
        print(f"   📈 Tempo médio por consulta: {avg_time:.2f}s")
        print(f"   ✅ Taxa de sucesso: {success_rate:.1f}%")
        print(f"   🎯 Consultas bem-sucedidas: {successful_queries}/{len(benchmark_queries)}")
        
        if success_rate >= 80:
            print("🎉 Performance excelente!")
        elif success_rate >= 60:
            print("👍 Performance boa")
        else:
            print("⚠️ Performance precisa melhorar")
            
    except Exception as e:
        print(f"❌ Erro no benchmark: {str(e)}")


def main():
    """Função principal para executar todos os exemplos."""
    
    print("🚀 INICIANDO TESTES DO SISTEMA DE GUIA DE VIAGEM")
    print("="*70)
    
    # Menu de opções
    options = {
        "1": ("Executar exemplos por categoria", run_example_queries),
        "2": ("Testar modo interativo", test_interactive_mode),
        "3": ("Benchmark de performance", benchmark_system_performance),
        "4": ("Executar todos os testes", lambda: [run_example_queries(), test_interactive_mode(), benchmark_system_performance()])
    }
    
    print("\n📋 Escolha uma opção:")
    for key, (description, _) in options.items():
        print(f"   {key}. {description}")
    print("   0. Sair")
    
    try:
        choice = input("\n🎯 Sua escolha (0-4): ").strip()
        
        if choice == "0":
            print("👋 Saindo...")
            return
        
        if choice in options:
            print(f"\n🏃 Executando: {options[choice][0]}")
            options[choice][1]()
        else:
            print("❌ Opção inválida. Tente novamente.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário. Até logo!")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")


if __name__ == "__main__":
    main()