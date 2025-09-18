# 🌍 Guia de Instalação - Sistema de Guia de Viagem

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conta Groq (para LLM) - [console.groq.com](https://console.groq.com/)
- Conta Pinecone (para base vetorial) - [app.pinecone.io](https://app.pinecone.io/)
- Make (opcional, para usar comandos facilitados)

## 🚀 Instalação Rápida

### Opção 1: Usando Makefile (Recomendado)
```bash
# Instala tudo automaticamente
make install

# Configure suas chaves de API
make setup-env

# Inicie o sistema
make run
```

### Opção 2: Instalação Manual
```bash
# Crie ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas chaves de API

# Execute o sistema
python src/main.py
```

## 🔧 Configuração das Chaves de API

Crie um arquivo `.env` na raiz do projeto:
```bash
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
PINECONE_API_KEY=your_actual_pinecone_api_key_here
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=guia-viagem
```

## 🎯 Como Usar

### Comandos Makefile Disponíveis
```bash
make install        # Instala todas as dependências
make setup-env      # Cria arquivo .env template
make run           # Executa o sistema
make test          # Executa testes
make clean         # Limpa arquivos temporários
make help          # Mostra todos os comandos
```

### Modo Interativo
```bash
make run
# ou
python src/main.py
```

### Exemplos de Consultas
- `"Quero um roteiro cultural em Paris por 3 dias"`
- `"Como chegar ao Cristo Redentor?"`
- `"Melhores restaurantes no Rio de Janeiro"`
- `"Frases úteis em francês para turistas"`

## 📚 Tipos de Consulta Suportadas

### 1. 🗺️ Roteiros de Viagem (`roteiro-viagem`)
- **Exemplos:**
  - "Roteiro cultural em Paris por 3 dias"
  - "Plano de viagem gastronômico no Rio por 5 dias"
  - "Itinerário romântico em Paris"
- **Retorna:** Roteiro detalhado com locais, horários e dicas

### 2. 🚗 Logística e Transporte (`logistica-transporte`)  
- **Exemplos:**
  - "Como chegar ao Cristo Redentor?"
  - "Melhor transporte público em Paris"
  - "Como ir do aeroporto ao centro?"
- **Retorna:** Informações de transporte, preços e dicas

### 3. 📍 Informações Locais (`info-local`)
- **Exemplos:**
  - "Horário de funcionamento do Louvre"
  - "Melhores restaurantes veganos em Paris"
  - "Preço dos ingressos para o Pão de Açúcar"
- **Retorna:** Detalhes específicos sobre locais e atrações

### 4. 🗣️ Tradução e Idiomas (`traducao-idiomas`)
- **Exemplos:**
  - "Frases úteis em francês para turistas"
  - "Como pedir comida em francês"
  - "Frases de emergência em inglês"
- **Retorna:** Guia de tradução com pronúncia

## 🏙️ Cidades Disponíveis

- **Rio de Janeiro** - Cristo Redentor, Pão de Açúcar, Copacabana, Ipanema, Santa Teresa, restaurantes locais
- **Paris** - Torre Eiffel, Louvre, Notre-Dame, Champs-Élysées, Montmartre, bistrôs tradicionais

## 🔧 Solução de Problemas

### Usando Makefile
```bash
make clean          # Limpa cache e arquivos temporários
make install        # Reinstala dependências
make test           # Testa configuração
```

### Problemas Comuns
- **Variáveis de ambiente**: Execute `make setup-env` e edite o `.env`
- **Módulo não encontrado**: Execute `make install`
- **Erro de conexão**: Verifique suas chaves de API no arquivo `.env`

## 📊 Estrutura do Projeto

```
guia_viagem/
├── Makefile               # Scripts de automação
├── requirements.txt       # Dependências Python
├── .env.example          # Template de configuração
├── src/                  # Código fonte
│   ├── main.py           # Sistema principal
│   ├── config.py         # Configurações
│   ├── rag.py           # Sistema RAG + Pinecone
│   ├── router.py        # Roteamento de consultas
│   ├── chains/          # Cadeias especializadas
│   └── data/            # Dados das cidades
└── README.md            # Documentação principal
```

---

**🎉 Use `make help` para ver todos os comandos disponíveis!**