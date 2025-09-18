#!/usr/bin/env python3
"""
🌍 GUIA DE VIAGEM INTELIGENTE - INTERFACE INTERATIVA
====================================================

Execute este arquivo para iniciar o sistema completo com interface de chat.

Funcionalidades:
- Chat interativo em tempo real
- 4 tipos de consulta especializadas  
- Sistema RAG com busca semântica
- Groq LLM para respostas naturais

Uso: python run.py
"""

if __name__ == "__main__":
    try:
        # Importa e executa o sistema principal
        from src.main import main
        
        print("🚀 Iniciando Sistema de Guia de Viagem Inteligente...")
        print("="*60)
        
        main()
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Certifique-se de estar no diretório correto e ter as dependências instaladas")
        print("   Execute: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        print("💡 Verifique o arquivo .env e as configurações")