from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import os

class PadocRAG:

    def __init__(self):
        self.embedding = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        # Ensure the database directory exists
        os.makedirs("brain/database", exist_ok=True)

    def criar_base(self):
        # Ensure the documents directory exists
        os.makedirs("brain/documentos", exist_ok=True)

        arquivos = [
            "brain/documentos/manual_motor.txt",
            "brain/documentos/obd2.txt",
            "brain/documentos/defeitos.txt"
        ]

        documentos = []

        for arquivo in arquivos:
            if os.path.exists(arquivo):
                loader = TextLoader(
                    arquivo,
                    encoding="utf-8"
                )
                documentos.extend(loader.load())
            else:
                print(f"Aviso: Arquivo de documento não encontrado: {arquivo}. Criando um placeholder.")
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write(f"Conteúdo placeholder para {os.path.basename(arquivo)}.")
                loader = TextLoader(arquivo, encoding="utf-8")
                documentos.extend(loader.load())

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )

        partes = splitter.split_documents(documentos)

        banco = Chroma.from_documents(
            partes,
            self.embedding,
            persist_directory="brain/database"
        )
        return banco

    def buscar(self, pergunta):
        banco = Chroma(
            persist_directory="brain/database",
            embedding_function=self.embedding
        )
        resultado = banco.similarity_search(
            pergunta,
            k=3
        )
        resposta = []
        for item in resultado:
            resposta.append(item.page_content)
        return resposta