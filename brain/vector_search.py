"""
PADOC AI - Módulo de Busca Semântica e RAG Automotivo.

Indexa manuais técnicos (.txt, .pdf, .json) e realiza busca semântica por similaridade
com fallback inteligente para garantir disponibilidade contínua da IA.
"""

import os
import json
import math
import re
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tokenizar(texto: str) -> List[str]:
    """Converte texto em tokens limpos."""
    return re.findall(r"\w+", texto.lower())


class FallbackVectorSearch:
    """
    Motor vetorial local embutido (TF-IDF / Cosseno de termos) que não requer
    compilação C++ ou downloads pesados, garantindo 100% de disponibilidade.
    """
    def __init__(self):
        self.documentos: List[Dict[str, Any]] = []
        self.vocabulario: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

    def indexar(self, documentos: List[Dict[str, str]]):
        self.documentos = documentos
        num_docs = len(documentos)
        if num_docs == 0:
            return

        doc_freq = {}
        for doc in documentos:
            tokens = set(tokenizar(doc["texto"]))
            for token in tokens:
                doc_freq[token] = doc_freq.get(token, 0) + 1

        self.idf = {term: math.log((num_docs + 1) / (freq + 1)) + 1.0 for term, freq in doc_freq.items()}

    def buscar(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_tokens = tokenizar(query)
        if not query_tokens or not self.documentos:
            return []

        scores = []
        for doc in self.documentos:
            doc_tokens = tokenizar(doc["texto"])
            doc_len = max(len(doc_tokens), 1)
            score = 0.0
            for qt in query_tokens:
                if qt in doc_tokens:
                    tf = doc_tokens.count(qt) / doc_len
                    score += tf * self.idf.get(qt, 1.0)
            
            if score > 0:
                scores.append({
                    "fonte": doc.get("fonte", "manual"),
                    "texto": doc["texto"],
                    "score": round(score, 4)
                })

        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:top_k]


class SemanticKnowledgeBase:
    """
    Gerencia a base de conhecimento vetorial usando ChromaDB quando disponível,
    ou fallback vetorial de alta performance.
    """

    def __init__(self, persist_directory="chroma_db"):
        self.persist_directory = persist_directory
        self.use_chroma = False
        self.fallback = FallbackVectorSearch()
        
        # Tenta inicializar ChromaDB
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.client.get_or_create_collection(
                name="padoc_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
            self.use_chroma = True
        except Exception:
            self.use_chroma = False

        self.carregar_e_indexar_todos_manuais()

    def carregar_e_indexar_todos_manuais(self):
        """Indexa todos os manuais .txt e datasets da PADOC."""
        docs = []

        # 1. Manuais .txt na raiz
        for arquivo in ["manuais.txt", "manual_motor.txt", "toyota.txt", "defeitos.txt", "obd2.txt"]:
            caminho = os.path.join(BASE_DIR, arquivo)
            if os.path.exists(caminho):
                try:
                    with open(caminho, "r", encoding="utf-8") as f:
                        conteudo = f.read()
                        paragrafos = [p.strip() for p in conteudo.split("\n\n") if p.strip()]
                        for p in paragrafos:
                            docs.append({"fonte": arquivo, "texto": p})
                except Exception:
                    pass

        # 2. Datasets de knowledge/
        knowledge_dir = os.path.join(BASE_DIR, "knowledge")
        if os.path.exists(knowledge_dir):
            for file_name in os.listdir(knowledge_dir):
                if file_name.endswith(".json"):
                    caminho = os.path.join(knowledge_dir, file_name)
                    try:
                        with open(caminho, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                for item in data[:50]:
                                    docs.append({"fonte": file_name, "texto": json.dumps(item, ensure_ascii=False)})
                            elif isinstance(data, dict):
                                for chave, item in list(data.items())[:50]:
                                    docs.append({"fonte": file_name, "texto": f"{chave}: {json.dumps(item, ensure_ascii=False)}"})
                    except Exception:
                        pass

        # Indexa no motor ativo
        self.fallback.indexar(docs)

    def search(self, query: str, n_results: int = 3) -> str:
        """Busca os trechos mais relevantes para alimentar o prompt do especialista."""
        if self.use_chroma:
            try:
                query_emb = self.embedding_model.encode([query]).tolist()
                results = self.collection.query(query_embeddings=query_emb, n_results=n_results)
                if results and results.get("documents") and results["documents"][0]:
                    return "\n\n".join(results["documents"][0])
            except Exception:
                pass

        # Fallback
        resultados = self.fallback.buscar(query, top_k=n_results)
        if not resultados:
            return "Nenhum trecho de manual correspondente localizado."
        return "\n\n".join([f"[{r['fonte']}] {r['texto']}" for r in resultados])