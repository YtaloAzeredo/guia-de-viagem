# 🌍 Guia de Instalação e Uso - Sistema de Guia de Viagem

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conta Groq (para LLM) - [console.groq.com](https://console.groq.com/)
- Conta Pinecone (para base vetorial) - [app.pinecone.io](https://app.pinecone.io/)

## 🚀 Instalação Rápida

### 1. Clone/Baixe o projeto
```bash
# Se usando git
git clone [URL_DO_REPOSITORIO]
cd guia_viagem

# Ou descompacte o arquivo zip e navegue para a pasta
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as chaves de API
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas chaves
nano .env  # ou use seu editor preferido
```

**Conteúdo do arquivo .env:**
```bash
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
PINECONE_API_KEY=your_actual_pinecone_api_key_here
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=guia-viagem
```

### 4. Execute a configuração inicial
```bash
python setup.py
```

### 5. Inicie o sistema
```bash
python src/main.py
```

## 🔧 Configuração Automática (Alternativa)

Execute o script de setup que faz tudo automaticamente:
```bash
python setup.py
```

Este script irá:
- ✅ Verificar estrutura de diretórios
- ✅ Criar arquivo .env
- ✅ Verificar dependências instaladas  
- ✅ Validar configurações
- ✅ Testar funcionalidades básicas

## 🎯 Como Usar

### Modo Interativo
```bash
python src/main.py
```

Digite suas perguntas no terminal:
- `"Quero um roteiro cultural em Paris por 3 dias"`
- `"Como chegar ao Cristo Redentor?"`
- `"Melhores restaurantes no Rio de Janeiro"`
- `"Frases úteis em francês para turistas"`

### Exemplos e Testes
```bash
# Execute exemplos pré-definidos
python examples/demo.py

# Execute testes básicos
python examples/test_basic.py
```

### Uso Programático
```python
from src.main import TravelGuideInterface

# Inicialize o sistema
guide = TravelGuideInterface()

# Processe uma consulta
response = guide.process_single_query("Roteiro em Paris por 2 dias")

if response["success"]:
    print(response["itinerary"])
else:
    print(f"Erro: {response['error']}")
```

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

### Erro: "Variáveis de ambiente não encontradas"
```bash
# Verifique se o arquivo .env existe e tem as chaves corretas
ls -la .env
cat .env
```

### Erro: "Módulo não encontrado"
```bash
# Reinstale dependências
pip install -r requirements.txt
```

### Erro: "Pinecone connection failed"
```bash
# Verifique suas credenciais Pinecone
# Certifique-se de que está usando o environment correto
```

### Erro: "Groq API error"
```bash
# Verifique sua chave Groq
# Certifique-se de que tem créditos na conta
```

### Problemas de Performance
```bash
# Execute o benchmark para verificar
python examples/demo.py
# Escolha opção 3 (Benchmark)
```

## 📊 Estrutura do Projeto

```
guia_viagem/
├── src/
│   ├── __init__.py
│   ├── config.py           # Configurações centrais
│   ├── rag.py              # Sistema RAG + Pinecone
│   ├── router.py           # Router Chain
│   ├── main.py             # Sistema principal
│   ├── chains/             # Cadeias especializadas
│   │   ├── __init__.py
│   │   ├── itinerary_chain.py
│   │   ├── logistics_chain.py
│   │   ├── local_info_chain.py
│   │   └── translation_chain.py
│   └── data/               # Dados das cidades
│       ├── rio_janeiro.json
│       └── paris.json
├── examples/               # Exemplos e testes
│   ├── demo.py
│   └── test_basic.py
├── config/                 # Arquivos de configuração
├── setup.py               # Script de configuração
├── requirements.txt       # Dependências
├── .env.example          # Template de configuração
└── README.md             # Documentação
```

## 🎛️ Configurações Avançadas

### Personalizar Modelo Groq
No arquivo `src/config.py`:
```python
GROQ_MODEL = "llama3-70b-8192"  # Modelo mais poderoso
```

### Ajustar RAG
```python
TOP_K_RESULTS = 10  # Mais resultados
SIMILARITY_THRESHOLD = 0.6  # Threshold mais baixo
```

### Adicionar Nova Cidade
1. Crie arquivo JSON em `src/data/nova_cidade.json`
2. Adicione cidade em `SUPPORTED_CITIES` no `config.py`
3. Execute `python src/main.py` e digite `reload` para recarregar

## 🆘 Suporte

Se encontrar problemas:

1. **Verifique logs:** Execute `python setup.py` para diagnóstico completo
2. **Teste conexões:** Execute `python examples/test_basic.py`
3. **Benchmarks:** Execute `python examples/demo.py` opção 3

## 📈 Próximas Melhorias

- [ ] Interface web com Streamlit
- [ ] Suporte a mais cidades
- [ ] Integração com APIs de transporte em tempo real
- [ ] Cache inteligente para respostas frequentes
- [ ] Suporte a imagens de locais

---

**🎉 Pronto! Seu sistema de guia de viagem está configurado e funcionando!**