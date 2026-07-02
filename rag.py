from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
import os


class PadocRAG:


    def __init__(self):
        self.embedding = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        # Ensure the database directory exists
        os.makedirs("database/rag", exist_ok=True)
        self.db = None # Initialize db as None


    def carregar(self):
        # Ensure the knowledge directory exists
        os.makedirs("knowledge", exist_ok=True)

        docs = []
        for arquivo_path in [
            "knowledge/manuais.txt",
            "knowledge/obd2.txt"
        ]:
            if not os.path.exists(arquivo_path):
                print(f"Aviso: Arquivo de conhecimento não encontrado: {arquivo_path}. Criando um placeholder.")
                with open(arquivo_path, 'w', encoding='utf-8') as f:
                    f.write(f"Conteúdo placeholder para {os.path.basename(arquivo_path)}.")
            
            loader = TextLoader(arquivo_path, encoding="utf-8")
            docs.extend(loader.load())

        if not docs:
            print("Aviso: Nenhum documento carregado para o RAG. A busca pode não retornar resultados.")
            return

        self.db = Chroma.from_documents(
            docs,
            self.embedding,
            persist_directory="database/rag"
        )


    def buscar(self, pergunta):
        if self.db is None:
            self.carregar() # Ensure the database is loaded if not already
        resultado = self.db.similarity_search(pergunta, k=3)
        return "\n".join([r.page_content for r in resultado])