# ===================================
# Guia de Viagem - Makefile
# ===================================

# Configurações
PYTHON := python3
PIP := pip3
VENV_NAME := venv
VENV_PATH := $(VENV_NAME)/bin
REQUIREMENTS := requirements.txt
SRC_DIR := src
MAIN_FILE := $(SRC_DIR)/main.py

# Cores para output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
RESET := \033[0m

.PHONY: help install setup-env run test clean lint format check-deps venv

# Comando padrão
.DEFAULT_GOAL := help

## 🆘 Ajuda - Lista todos os comandos disponíveis
help:
	@echo "$(BLUE)🌍 Sistema de Guia de Viagem - Comandos Disponíveis$(RESET)"
	@echo ""
	@echo "$(GREEN)📦 Instalação e Configuração:$(RESET)"
	@echo "  make install      - Instala todas as dependências"
	@echo "  make venv         - Cria ambiente virtual Python"
	@echo "  make setup-env    - Cria arquivo .env template"
	@echo ""
	@echo "$(GREEN)🚀 Execução:$(RESET)"
	@echo "  make run          - Executa o sistema principal"
	@echo "  make test         - Executa testes básicos"
	@echo ""
	@echo "$(GREEN)🔧 Desenvolvimento:$(RESET)"
	@echo "  make lint         - Verifica código com pylint"
	@echo "  make format       - Formata código com black"
	@echo "  make check-deps   - Verifica dependências desatualizadas"
	@echo ""
	@echo "$(GREEN)🧹 Limpeza:$(RESET)"
	@echo "  make clean        - Remove arquivos temporários"
	@echo "  make clean-all    - Remove tudo (incluindo venv)"
	@echo ""
	@echo "$(YELLOW)💡 Dica: Execute 'make install && make setup-env && make run' para começar!$(RESET)"

## 📦 Instala todas as dependências necessárias
install:
	@echo "$(BLUE)📦 Instalando dependências...$(RESET)"
	@if [ -f "$(VENV_PATH)/activate" ]; then \
		echo "$(GREEN)✅ Usando ambiente virtual existente$(RESET)"; \
		. $(VENV_PATH)/activate && $(PIP) install --upgrade pip && $(PIP) install -r $(REQUIREMENTS); \
	else \
		echo "$(YELLOW)⚠️  Instalando no ambiente global$(RESET)"; \
		$(PIP) install --upgrade pip; \
		$(PIP) install -r $(REQUIREMENTS); \
	fi
	@echo "$(GREEN)✅ Dependências instaladas com sucesso!$(RESET)"

## 🐍 Cria ambiente virtual Python
venv:
	@echo "$(BLUE)🐍 Criando ambiente virtual...$(RESET)"
	@if [ -d "$(VENV_NAME)" ]; then \
		echo "$(YELLOW)⚠️  Ambiente virtual já existe$(RESET)"; \
	else \
		$(PYTHON) -m venv $(VENV_NAME); \
		echo "$(GREEN)✅ Ambiente virtual criado em ./$(VENV_NAME)$(RESET)"; \
		echo "$(YELLOW)💡 Ative com: source $(VENV_PATH)/activate$(RESET)"; \
	fi

## ⚙️ Cria arquivo .env template para configuração
setup-env:
	@echo "$(BLUE)⚙️  Configurando ambiente...$(RESET)"
	@if [ -f ".env" ]; then \
		echo "$(YELLOW)⚠️  Arquivo .env já existe$(RESET)"; \
	else \
		echo "# Configurações do Guia de Viagem" > .env; \
		echo "# Obtenha suas chaves em:" >> .env; \
		echo "# Groq: https://console.groq.com/" >> .env; \
		echo "# Pinecone: https://app.pinecone.io/" >> .env; \
		echo "" >> .env; \
		echo "GROQ_API_KEY=gsk_your_actual_groq_api_key_here" >> .env; \
		echo "PINECONE_API_KEY=your_actual_pinecone_api_key_here" >> .env; \
		echo "PINECONE_ENVIRONMENT=gcp-starter" >> .env; \
		echo "PINECONE_INDEX_NAME=guia-viagem" >> .env; \
		echo "$(GREEN)✅ Arquivo .env criado!$(RESET)"; \
		echo "$(YELLOW)📝 Edite o arquivo .env com suas chaves de API$(RESET)"; \
	fi

## 🚀 Executa o sistema principal
run:
	@echo "$(BLUE)🚀 Iniciando Sistema de Guia de Viagem...$(RESET)"
	@if [ ! -f ".env" ]; then \
		echo "$(RED)❌ Arquivo .env não encontrado!$(RESET)"; \
		echo "$(YELLOW)💡 Execute: make setup-env$(RESET)"; \
		exit 1; \
	fi
	@if [ -f "$(VENV_PATH)/activate" ]; then \
		. $(VENV_PATH)/activate && $(PYTHON) -m src.main; \
	else \
		$(PYTHON) -m src.main; \
	fi

## 🧪 Executa testes básicos do sistema
test:
	@echo "$(BLUE)🧪 Executando testes básicos...$(RESET)"
	@if [ -f "$(VENV_PATH)/activate" ]; then \
		. $(VENV_PATH)/activate && $(PYTHON) -c "import src.config; print('✅ Configurações OK')"; \
		. $(VENV_PATH)/activate && $(PYTHON) -c "from src.rag import setup_rag_system; print('✅ RAG System OK')"; \
		. $(VENV_PATH)/activate && $(PYTHON) -c "from src.router import RouterChain; print('✅ Router OK')"; \
	else \
		$(PYTHON) -c "import src.config; print('✅ Configurações OK')"; \
		$(PYTHON) -c "from src.rag import setup_rag_system; print('✅ RAG System OK')"; \
		$(PYTHON) -c "from src.router import RouterChain; print('✅ Router OK')"; \
	fi
	@echo "$(GREEN)✅ Todos os testes passaram!$(RESET)"

## 🔍 Verifica código com pylint
lint:
	@echo "$(BLUE)🔍 Verificando código com pylint...$(RESET)"
	@if [ -f "$(VENV_PATH)/activate" ]; then \
		. $(VENV_PATH)/activate && $(PIP) install pylint > /dev/null 2>&1; \
		. $(VENV_PATH)/activate && pylint $(SRC_DIR) || true; \
	else \
		$(PIP) install pylint > /dev/null 2>&1; \
		pylint $(SRC_DIR) || true; \
	fi

## 🎨 Formata código com black
format:
	@echo "$(BLUE)🎨 Formatando código com black...$(RESET)"
	@if [ -f "$(VENV_PATH)/activate" ]; then \
		. $(VENV_PATH)/activate && $(PIP) install black > /dev/null 2>&1; \
		. $(VENV_PATH)/activate && black $(SRC_DIR); \
	else \
		$(PIP) install black > /dev/null 2>&1; \
		black $(SRC_DIR); \
	fi
	@echo "$(GREEN)✅ Código formatado!$(RESET)"

## 📋 Verifica dependências desatualizadas
check-deps:
	@echo "$(BLUE)📋 Verificando dependências...$(RESET)"
	@if [ -f "$(VENV_PATH)/activate" ]; then \
		. $(VENV_PATH)/activate && $(PIP) list --outdated; \
	else \
		$(PIP) list --outdated; \
	fi

## 🧹 Remove arquivos temporários
clean:
	@echo "$(BLUE)🧹 Limpando arquivos temporários...$(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Limpeza concluída!$(RESET)"

## 🗑️ Remove tudo (incluindo ambiente virtual)
clean-all: clean
	@echo "$(BLUE)🗑️  Removendo ambiente virtual...$(RESET)"
	@rm -rf $(VENV_NAME)
	@rm -f .env
	@echo "$(GREEN)✅ Limpeza completa concluída!$(RESET)"

## 🔄 Reinstala tudo do zero
reinstall: clean-all venv install setup-env
	@echo "$(GREEN)🎉 Reinstalação completa concluída!$(RESET)"
	@echo "$(YELLOW)📝 Lembre-se de editar o arquivo .env com suas chaves de API$(RESET)"

## 📊 Mostra informações do projeto
info:
	@echo "$(BLUE)📊 Informações do Projeto$(RESET)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "PIP: $(shell $(PIP) --version)"
	@echo "Diretório: $(shell pwd)"
	@echo "Ambiente Virtual: $(if $(wildcard $(VENV_PATH)), $(GREEN)✅ Ativo$(RESET), $(RED)❌ Não encontrado$(RESET))"
	@echo "Arquivo .env: $(if $(wildcard .env), $(GREEN)✅ Existe$(RESET), $(RED)❌ Não encontrado$(RESET))"
	@echo "Dependências: $(shell wc -l < $(REQUIREMENTS) | tr -d ' ') pacotes"