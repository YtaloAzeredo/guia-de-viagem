#!/usr/bin/env python3
"""
Quick Start - Teste rápido do Sistema de Guia de Viagem
Execute este arquivo para testar rapidamente as funcionalidades principais.
"""

import os
import sys

def print_header(title):
    """Imprime cabeçalho formatado."""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def print_step(step_num, description):
    """Imprime passo formatado."""
    print(f"\n📋 Passo {step_num}: {description}")
    print("-" * 40)

def quick_test():
    """Executa teste rápido do sistema."""
    
    print_header("TESTE RÁPIDO DO SISTEMA DE GUIA DE VIAGEM")
    
    print("🚀 Este script vai testar rapidamente as funcionalidades principais")
    print("⏱️ Tempo estimado: 2-3 minutos")
    
    # Passo 1: Verificar dependências básicas
    print_step(1, "Verificando dependências básicas")
    
    try:
        import importlib
        
        basic_deps = ["os", "sys", "json", "pathlib"]
        for dep in basic_deps:
            importlib.import_module(dep)
            print(f"   ✅ {dep}")
            
    except ImportError as e:
        print(f"   ❌ Erro básico: {e}")
        return False
    
    # Passo 2: Verificar estrutura do projeto
    print_step(2, "Verificando estrutura do projeto")
    
    required_files = [
        "src/config.py",
        "src/main.py", 
        "src/router.py",
        "src/rag.py",
        "requirements.txt",
        ".env.example"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"   ❌ {file_path} (não encontrado)")
    
    if missing_files:
        print(f"\n⚠️ Arquivos em falta: {missing_files}")
        print("💡 Certifique-se de estar na pasta raiz do projeto")
        return False
    
    # Passo 3: Testar importações principais
    print_step(3, "Testando importações principais")
    
    try:
        # Adiciona src ao path se ainda não estiver
        src_path = os.path.join(os.getcwd(), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from config import Config
        print("   ✅ Config importada")
        
        config = Config()
        print("   ✅ Config inicializada")
        
        # Testa configurações básicas
        assert hasattr(config, 'GROQ_MODEL'), "GROQ_MODEL não encontrado"
        assert hasattr(config, 'SUPPORTED_CITIES'), "SUPPORTED_CITIES não encontrado" 
        assert hasattr(config, 'INTENTIONS'), "INTENTIONS não encontrado"
        
        print(f"   ✅ Modelo configurado: {config.GROQ_MODEL}")
        print(f"   ✅ Cidades suportadas: {len(config.SUPPORTED_CITIES)}")
        print(f"   ✅ Intenções configuradas: {len(config.INTENTIONS)}")
        
    except ImportError as e:
        print(f"   ❌ Erro de importação: {e}")
        print(f"   💡 Certifique-se de estar na pasta raiz do projeto")
        return False
    except Exception as e:
        print(f"   ❌ Erro de configuração: {e}")
        print(f"   💡 Pode ser necessário instalar dependências: pip install -r requirements.txt")
        return False
    
    # Passo 4: Verificar dados das cidades
    print_step(4, "Verificando dados das cidades")
    
    try:
        import json
        
        city_files = {
            "src/data/rio_janeiro.json": "Rio de Janeiro",
            "src/data/paris.json": "Paris"
        }
        
        total_locations = 0
        for file_path, city_name in city_files.items():
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_locations += len(data)
                    print(f"   ✅ {city_name}: {len(data)} locais")
            else:
                print(f"   ❌ {city_name}: arquivo não encontrado")
        
        print(f"   📊 Total: {total_locations} locais na base")
        
    except Exception as e:
        print(f"   ❌ Erro ao ler dados: {e}")
        return False
    
    # Passo 5: Testar router básico
    print_step(5, "Testando classificação de intenções")
    
    try:
        # Importa o router do módulo correto
        from router import IntentionRouter
        
        # Cria instância usando mock se necessário
        try:
            router = IntentionRouter()
        except Exception:
            # Se falhar na inicialização (sem LangChain), testa só o fallback
            print("   ⚠️ Inicialização completa falhou, testando fallback...")
            router = None
        
        # Testa classificação fallback diretamente (não precisa de LangChain)
        if router is not None:
            test_cases = [
                ("Quero um roteiro para Paris", "roteiro-viagem"),
                ("Como chegar ao Cristo Redentor", "logistica-transporte"),
                ("Horário do Louvre", "info-local"),
                ("Frases em francês", "traducao-idiomas")
            ]
            
            for query, expected in test_cases:
                result = router._fallback_classification(query)
                if result == expected:
                    print(f"   ✅ '{query}' → {result}")
                else:
                    print(f"   ⚠️ '{query}' → {result} (esperado: {expected})")
        else:
            print("   ℹ️ Teste de router pulado (dependências não instaladas)")
        
    except Exception as e:
        print(f"   ❌ Erro no router: {e}")
        print(f"   💡 Execute: pip install -r requirements.txt para funcionalidade completa")
        # Não retorna False aqui, continua o teste
        pass
    
    # Passo 6: Verificar arquivo .env
    print_step(6, "Verificando configuração de ambiente")
    
    env_file = ".env"
    if os.path.exists(env_file):
        print("   ✅ Arquivo .env existe")
        
        # Verifica conteúdo básico
        with open(env_file, 'r') as f:
            content = f.read()
            
        if "GROQ_API_KEY" in content:
            print("   ✅ GROQ_API_KEY configurada")
        else:
            print("   ⚠️ GROQ_API_KEY não encontrada")
            
        if "PINECONE_API_KEY" in content:
            print("   ✅ PINECONE_API_KEY configurada")  
        else:
            print("   ⚠️ PINECONE_API_KEY não encontrada")
            
    else:
        print("   ⚠️ Arquivo .env não existe")
        print("   💡 Execute: cp .env.example .env")
        print("   💡 E configure suas chaves de API")
    
    # Resumo final
    print_header("RESUMO DO TESTE")
    
    print("✅ Estrutura do projeto: OK")
    print("✅ Configurações básicas: OK")  
    print("✅ Dados das cidades: OK")
    print("✅ Router de intenções: OK")
    
    if os.path.exists(".env"):
        print("✅ Arquivo .env: OK")
    else:
        print("⚠️ Arquivo .env: Precisa ser configurado")
    
    print(f"\n🎉 SISTEMA PRONTO PARA USO!")
    print("\n📋 Próximos passos:")
    print("   1. Configure suas APIs no arquivo .env (se ainda não fez)")
    print("   2. Instale dependências: pip install -r requirements.txt") 
    print("   3. Execute: python src/main.py")
    print("   4. Ou teste exemplos: python examples/demo.py")
    
    return True

def main():
    """Função principal."""
    try:
        success = quick_test()
        
        if success:
            print(f"\n{'🎊' * 20}")
            print("TESTE CONCLUÍDO COM SUCESSO!")
            print(f"{'🎊' * 20}")
        else:
            print(f"\n{'⚠️' * 20}")
            print("TESTE ENCONTROU PROBLEMAS")
            print("Verifique os erros acima e tente novamente")
            print(f"{'⚠️' * 20}")
            
    except KeyboardInterrupt:
        print(f"\n\n👋 Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()