"""
Sistema RAG (Retrieval-Augmented Generation) integrado com Pinecone.
"""
import json
import os
from typing import List, Dict, Any, Optional

# Importações com tratamento de erro
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

# Importação do Pinecone moderno
try:
    from pinecone import Pinecone, ServerlessSpec
except ImportError:
    Pinecone = None
    ServerlessSpec = None

try:
    from .config import Config
except ImportError:
    from config import Config


class RAGSystem:
    """Sistema RAG para recuperação e geração de conteúdo."""
    
    def __init__(self):
        """Inicializa o sistema RAG."""
        self.config = Config()
        self.config.validate()
        
        # Verifica se as dependências estão disponíveis
        if SentenceTransformer is None or Pinecone is None:
            print("⚠️  Dependências não disponíveis - usando modo fallback")
            self.use_fallback = True
            self.embedding_model = None
            self.pc = None
            self.index = None
            self._load_local_data()
            return
        
        self.use_fallback = False
        
        # Inicializa modelo de embedding
        try:
            self.embedding_model = SentenceTransformer(self.config.EMBEDDING_MODEL)
        except Exception as e:
            print(f"Erro ao carregar modelo de embedding: {e}")
            self.use_fallback = True
            self.embedding_model = None
            self.pc = None
            self.index = None
            self._load_local_data()
            return
        
        # Inicializa Pinecone
        try:
            self.pc = Pinecone(api_key=self.config.PINECONE_API_KEY)
            self.index = None
            self._setup_pinecone()
        except Exception as e:
            print(f"Erro ao conectar com Pinecone: {e}")
            self.use_fallback = True
            self.pc = None
            self.index = None
            self._load_local_data()
    
    def _load_local_data(self):
        """Carrega dados localmente quando Pinecone não está disponível."""
        self.local_data = []
        
        # Carrega dados das cidades
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        
        # Carrega dados do Rio de Janeiro
        rio_file = os.path.join(data_dir, "rio_janeiro.json")
        if os.path.exists(rio_file):
            with open(rio_file, 'r', encoding='utf-8') as f:
                rio_data = json.load(f)
                self.local_data.extend(rio_data)
        
        # Carrega dados de Paris
        paris_file = os.path.join(data_dir, "paris.json")
        if os.path.exists(paris_file):
            with open(paris_file, 'r', encoding='utf-8') as f:
                paris_data = json.load(f)
                self.local_data.extend(paris_data)
        
        print(f"📁 Dados locais carregados: {len(self.local_data)} itens")
    
    def _setup_pinecone(self):
        """Configura o índice do Pinecone."""
        if ServerlessSpec is None:
            print("ServerlessSpec não disponível")
            self.use_fallback = True
            self._load_local_data()
            return
            
        index_name = self.config.PINECONE_INDEX_NAME
        
        # Verifica se o índice existe
        existing_indexes = self.pc.list_indexes()
        index_names = [idx['name'] for idx in existing_indexes.indexes]
        
        if index_name not in index_names:
            print(f"Criando índice {index_name}...")
            self.pc.create_index(
                name=index_name,
                dimension=self.config.EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
        
        # Conecta ao índice
        self.index = self.pc.Index(index_name)
        
    def load_and_index_data(self, force_reload: bool = False):
        """Carrega e indexa dados dos arquivos JSON."""
        # Modo fallback: dados já carregados
        if self.use_fallback:
            print("💾 Modo fallback: dados já disponíveis localmente")
            return
            
        # Verifica se já existem dados no índice (a menos que force_reload seja True)
        if not force_reload:
            try:
                stats = self.index.describe_index_stats()
                if stats.total_vector_count > 0:
                    print(f"Índice já contém {stats.total_vector_count} vetores. Use force_reload=True para recarregar.")
                    return
            except Exception as e:
                print(f"Erro ao verificar status do índice: {e}")
                return
        
        # Carrega dados das cidades
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        all_data = []
        
        # Carrega dados do Rio de Janeiro
        rio_file = os.path.join(data_dir, "rio_janeiro.json")
        if os.path.exists(rio_file):
            with open(rio_file, 'r', encoding='utf-8') as f:
                rio_data = json.load(f)
                all_data.extend(rio_data)
        
        # Carrega dados de Paris
        paris_file = os.path.join(data_dir, "paris.json")
        if os.path.exists(paris_file):
            with open(paris_file, 'r', encoding='utf-8') as f:
                paris_data = json.load(f)
                all_data.extend(paris_data)
        
        if not all_data:
            print("Nenhum dado encontrado para indexar.")
            return
        
        print(f"Indexando {len(all_data)} itens...")
        
        # Processa e indexa dados em lotes
        vectors = []
        for item in all_data:
            # Cria texto para embedding
            text_content = self._create_text_for_embedding(item)
            
            # Gera embedding
            embedding = self.embedding_model.encode(text_content).tolist()
            
            # Prepara vetor para Pinecone
            vector = {
                "id": item["id"],
                "values": embedding,
                "metadata": item
            }
            vectors.append(vector)
        
        # Indexa em lotes de 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            try:
                self.index.upsert(vectors=batch)
            except Exception as e:
                print(f"Erro ao indexar lote: {e}")
                continue
        
        print(f"Indexação concluída! {len(vectors)} vetores indexados.")
    
    def _create_text_for_embedding(self, item: Dict[str, Any]) -> str:
        """Cria texto otimizado para embedding a partir do item."""
        text_parts = [
            f"Cidade: {item.get('cidade', '')}",
            f"Categoria: {item.get('categoria', '')}",
            f"Nome: {item.get('nome', '')}",
            f"Descrição: {item.get('descricao', '')}",
        ]
        
        # Adiciona campos opcionais se existirem
        if item.get('endereco'):
            text_parts.append(f"Endereço: {item['endereco']}")
        if item.get('dicas'):
            text_parts.append(f"Dicas: {item['dicas']}")
        if item.get('como_chegar'):
            text_parts.append(f"Como chegar: {item['como_chegar']}")
        
        return " | ".join(text_parts)
    
    def search_similar(self, query: str, top_k: int = None, filter_dict: Dict = None) -> List[Dict]:
        """Busca itens similares baseados na consulta."""
        if top_k is None:
            top_k = self.config.TOP_K_RESULTS
        
        # Modo fallback: busca textual simples
        if self.use_fallback:
            return self._search_local(query, top_k, filter_dict)
            
        # Gera embedding da consulta
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Busca no Pinecone
        search_params = {
            "vector": query_embedding,
            "top_k": top_k,
            "include_metadata": True
        }
        
        if filter_dict:
            search_params["filter"] = filter_dict
            
        results = self.index.query(**search_params)
        
        # Processa resultados
        similar_items = []
        for match in results.matches:
            if match.score >= self.config.SIMILARITY_THRESHOLD:
                item = match.metadata.copy()
                item['similarity_score'] = match.score
                similar_items.append(item)
        
        return similar_items
    
    def _search_local(self, query: str, top_k: int, filter_dict: Dict = None) -> List[Dict]:
        """Busca local usando correspondência textual simples."""
        query_lower = query.lower()
        results = []
        
        for item in self.local_data:
            # Aplicar filtros se fornecidos
            if filter_dict:
                skip_item = False
                for key, condition in filter_dict.items():
                    if key in item:
                        if "$eq" in condition and item[key] != condition["$eq"]:
                            skip_item = True
                            break
                if skip_item:
                    continue
            
            # Busca textual simples
            searchable_text = self._create_text_for_embedding(item).lower()
            
            # Calcula pontuação simples baseada em palavras-chave
            score = 0
            query_words = query_lower.split()
            for word in query_words:
                if word in searchable_text:
                    score += searchable_text.count(word)
            
            if score > 0:
                item_copy = item.copy()
                item_copy['similarity_score'] = score / len(query_words)
                results.append(item_copy)
        
        # Ordena por pontuação e retorna top_k
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:top_k]
    
    def search_by_city(self, query: str, city: str, top_k: int = None) -> List[Dict]:
        """Busca itens similares filtrados por cidade."""
        filter_dict = {"cidade": {"$eq": city}}
        return self.search_similar(query, top_k, filter_dict)
    
    def search_by_category(self, query: str, category: str, top_k: int = None) -> List[Dict]:
        """Busca itens similares filtrados por categoria."""
        filter_dict = {"categoria": {"$eq": category}}
        return self.search_similar(query, top_k, filter_dict)
    
    def get_all_cities(self) -> List[str]:
        """Retorna lista de todas as cidades disponíveis."""
        return self.config.SUPPORTED_CITIES
    
    def get_city_overview(self, city: str) -> List[Dict]:
        """Retorna visão geral de uma cidade (todos os pontos)."""
        filter_dict = {"cidade": {"$eq": city}}
        
        # Busca genérica para pegar vários tipos de lugares
        overview_query = f"pontos turísticos atrações restaurantes {city}"
        return self.search_similar(overview_query, top_k=20, filter_dict=filter_dict)


def setup_rag_system() -> RAGSystem:
    """Factory function para configurar sistema RAG."""
    rag = RAGSystem()
    
    # Carrega dados se necessário (apenas se não estiver em modo fallback)
    if not rag.use_fallback:
        try:
            if rag.index:
                stats = rag.index.describe_index_stats()
                if stats.total_vector_count == 0:
                    print("Índice vazio. Carregando dados iniciais...")
                    rag.load_and_index_data()
        except Exception as e:
            print(f"Erro ao verificar índice: {e}")
            print("Tentando carregar dados...")
            rag.load_and_index_data()
    
    return rag