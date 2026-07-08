"""
PADOC AI - Módulo de Busca Semântica com ChromaDB e Embeddings.

Este módulo transforma a base de conhecimento em vetores (embeddings) e
permite a busca por similaridade de significado, em vez de palavras-chave.
"""
import chromadb
import json
import os

class SemanticKnowledgeBase:
    """
    Gerencia a base de conhecimento vetorial usando ChromaDB.
    """
    def __init__(self, persist_directory="chroma_db"):
        """
        Inicializa o cliente ChromaDB e o modelo de embedding.
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Execute: pip install sentence-transformers")

        # Garante que o diretório de persistência exista
        os.makedirs(persist_directory, exist_ok=True)

        # Modelo de embedding leve e eficiente que roda localmente
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Cliente persistente para salvar os dados em disco
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Coleção onde os vetores serão armazenados
        self.collection = self.client.get_or_create_collection(
            name="padoc_knowledge",
            metadata={"hnsw:space": "cosine"} # Usa similaridade de cosseno
        )
        print("✓ Base de conhecimento semântica (ChromaDB) inicializada.")

    def index_knowledge(self, knowledge_path: str):
        """
        Carrega um arquivo JSON, gera embeddings e o indexa no ChromaDB.
        Este processo é feito apenas uma vez ou quando a base de dados muda.
        """
        if not os.path.exists(knowledge_path):
            print(f"Aviso: Arquivo de conhecimento não encontrado em {knowledge_path}")
            return

        with open(knowledge_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        documents = []
        metadatas = []
        ids = []

        # Extrai a chave principal (ex: 'ordens_servico', 'defeitos_mecanicos')
        main_key = next(iter(data))
        items = data.get(main_key, [])

        print(f"Indexando {len(items)} documentos de '{knowledge_path}'...")

        for i, item in enumerate(items):
            # Converte o item JSON em uma string de texto coesa
            content = json.dumps(item, ensure_ascii=False)
            doc_id = f"{os.path.basename(knowledge_path)}-{i}"

            # Evita reindexar documentos já existentes
            if self.collection.get(ids=[doc_id])['ids']:
                continue

            documents.append(content)
            # Adiciona metadados para filtragem futura, se necessário
            metadatas.append({"source": os.path.basename(knowledge_path)})
            ids.append(doc_id)

        if not documents:
            print("Nenhum documento novo para indexar.")
            return

        # Gera os embeddings para todos os documentos de uma vez (mais eficiente)
        embeddings = self.embedding_model.encode(documents).tolist()

        # Adiciona ao ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✓ {len(documents)} novos documentos indexados com sucesso.")

    def search(self, query: str, n_results: int = 3) -> str:
        """
        Realiza uma busca semântica na base de conhecimento.

        Args:
            query: A pergunta do usuário.
            n_results: O número de resultados mais relevantes a serem retornados.

        Returns:
            Uma string contendo o contexto mais relevante encontrado.
        """
        if self.collection.count() == 0:
            return "A base de conhecimento semântica está vazia. Execute a indexação primeiro."

        # Gera o embedding para a pergunta do usuário
        query_embedding = self.embedding_model.encode([query]).tolist()

        # Realiza a busca no ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )

        # Concatena os documentos encontrados para formar o contexto
        context = "\n\n".join(results['documents'][0])
        return context