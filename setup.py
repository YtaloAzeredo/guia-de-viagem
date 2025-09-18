"""
Script de configuração inicial para o Sistema de Guia de Viagem.
Configura ambiente e verifica dependências.
"""
import os
import sys
from pathlib import Path


def create_env_file():
    """Cria arquivo .env se não existir."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Criando arquivo .env...")
        
        # Lê template
        with open(env_example, 'r') as f:
            content = f.read()
        
        # Cria arquivo .env
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Arquivo .env criado!")
        print("⚠️ IMPORTANTE: Configure suas chaves de API no arquivo .env")
        print("   - GROQ_API_KEY: Obtenha em https://console.groq.com/")
        print("   - PINECONE_API_KEY: Obtenha em https://app.pinecone.io/")
        
        return True
    elif env_file.exists():
        print("✅ Arquivo .env já existe")
        return True
    else:
        print("❌ Arquivo .env.example não encontrado")
        return False


def check_dependencies():
    """Verifica se as dependências estão instaladas."""
    print("\n🔍 Verificando dependências...")
    
    required_packages = [
        "langchain",
        "langchain_groq", 
        "pinecone",
        "sentence_transformers",
        "pandas",
        "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # Tratamento especial para alguns pacotes
            if package == "python-dotenv":
                __import__("dotenv")
            elif package == "sentence_transformers":
                __import__("sentence_transformers")
            else:
                __import__(package.replace("-", "_"))
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package} (não instalado)")
    
    if missing_packages:
        print(f"\n⚠️ Pacotes em falta: {', '.join(missing_packages)}")
        print("📦 Instale com: pip install -r requirements.txt")
        return False
    else:
        print("\n🎉 Todas as dependências estão instaladas!")
        return True


def validate_env_variables():
    """Valida variáveis de ambiente."""
    print("\n🔐 Verificando variáveis de ambiente...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        "GROQ_API_KEY": "Chave da API Groq",
        "PINECONE_API_KEY": "Chave da API Pinecone"
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print(f"   ✅ {var}")
        else:
            missing_vars.append((var, description))
            print(f"   ❌ {var} (não configurada)")
    
    if missing_vars:
        print(f"\n⚠️ Configure as seguintes variáveis no arquivo .env:")
        for var, desc in missing_vars:
            print(f"   - {var}: {desc}")
        return False
    else:
        print("\n🎉 Todas as variáveis estão configuradas!")
        return True


def test_basic_functionality():
    """Testa funcionalidades básicas."""
    print("\n🧪 Testando funcionalidades básicas...")
    
    try:
        # Testa importações
        from src.config import Config
        config = Config()
        print("   ✅ Configuração carregada")
        
        # Testa validação (sem falhar se APIs não estão configuradas)
        try:
            config.validate()
            print("   ✅ Validação passou")
        except ValueError as e:
            print(f"   ⚠️ Validação falhou: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False


def setup_project_structure():
    """Verifica e cria estrutura de diretórios se necessário."""
    print("\n📁 Verificando estrutura do projeto...")
    
    required_dirs = [
        "src",
        "src/chains",
        "src/data", 
        "config",
        "examples"
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"   ✅ {dir_path}/")
        else:
            path.mkdir(parents=True, exist_ok=True)
            print(f"   📁 {dir_path}/ (criado)")
    
    return True


def main():
    """Executa configuração completa."""
    print("🚀 CONFIGURAÇÃO DO SISTEMA DE GUIA DE VIAGEM")
    print("="*60)
    
    success_steps = []
    
    # 1. Estrutura do projeto
    if setup_project_structure():
        success_steps.append("Estrutura")
    
    # 2. Arquivo .env
    if create_env_file():
        success_steps.append("Arquivo .env")
    
    # 3. Dependências
    deps_ok = check_dependencies()
    if deps_ok:
        success_steps.append("Dependências")
    
    # 4. Variáveis de ambiente (só se deps estão ok)
    if deps_ok:
        env_ok = validate_env_variables()
        if env_ok:
            success_steps.append("Variáveis de ambiente")
            
            # 5. Teste básico (só se tudo está ok)
            if test_basic_functionality():
                success_steps.append("Funcionalidade básica")
    
    # Resumo
    print(f"\n{'='*60}")
    print("📋 RESUMO DA CONFIGURAÇÃO")
    print("-"*30)
    
    for step in success_steps:
        print(f"✅ {step}")
    
    all_steps = ["Estrutura", "Arquivo .env", "Dependências", "Variáveis de ambiente", "Funcionalidade básica"]
    missing_steps = [step for step in all_steps if step not in success_steps]
    
    for step in missing_steps:
        print(f"❌ {step}")
    
    if len(success_steps) == len(all_steps):
        print(f"\n🎉 SISTEMA TOTALMENTE CONFIGURADO!")
        print("\n🚀 Próximos passos:")
        print("   1. Execute: python src/main.py")
        print("   2. Ou teste exemplos: python examples/demo.py")
    else:
        print(f"\n⚠️ Configuração incompleta ({len(success_steps)}/{len(all_steps)} passos)")
        print("\n📝 Resolva os problemas acima antes de continuar.")


if __name__ == "__main__":
    main()