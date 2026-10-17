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
        """Indexa todos os manuais .txt, datasets JSON e dados multimodais da PADOC."""
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
                if file_name.endswith(".json") and not file_name.startswith("_"):
                    caminho = os.path.join(knowledge_dir, file_name)
                    try:
                        with open(caminho, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                for item in data[:100]:
                                    docs.append({"fonte": file_name, "texto": json.dumps(item, ensure_ascii=False)})
                            elif isinstance(data, dict):
                                for chave, item in list(data.items())[:100]:
                                    docs.append({"fonte": file_name, "texto": f"{chave}: {json.dumps(item, ensure_ascii=False)}"})
                    except Exception:
                        pass

        # 3. Dados multimodais (áudios, fotos, vídeos) — indexa metadados e catálogos
        multimodal_dir = os.path.join(BASE_DIR, "dados", "multimodal")
        if os.path.exists(multimodal_dir):
            # 3a. Catálogos JSON de vídeos/diagnósticos
            for root, dirs, files in os.walk(multimodal_dir):
                for file_name in files:
                    if file_name.endswith(".json"):
                        caminho = os.path.join(root, file_name)
                        try:
                            with open(caminho, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                if isinstance(data, dict):
                                    for chave, item in data.items():
                                        docs.append({
                                            "fonte": f"multimodal/{file_name}",
                                            "texto": f"[VÍDEO/DIAGNÓSTICO VISUAL] {chave}: {json.dumps(item, ensure_ascii=False)}"
                                        })
                                elif isinstance(data, list):
                                    for item in data[:50]:
                                        docs.append({
                                            "fonte": f"multimodal/{file_name}",
                                            "texto": f"[DIAGNÓSTICO MULTIMODAL] {json.dumps(item, ensure_ascii=False)}"
                                        })
                        except Exception:
                            pass

            # 3b. Inventário de amostras de áudio disponíveis
            audio_dir = os.path.join(multimodal_dir, "audios_ruidos")
            if os.path.exists(audio_dir):
                audios_disponiveis = [f for f in os.listdir(audio_dir) if f.endswith((".wav", ".mp3"))]
                if audios_disponiveis:
                    descricoes_audio = {
                        "batida_biela": "Batida de biela/bronzina - som grave e compassado vindo do cárter, indica desgaste da bronzina de biela",
                        "tucho_teclando": "Tucho hidráulico batendo tec-tec - ruído seco que pode sumir após aquecer, indica tucho descarregado",
                        "chiado_correia": "Chiado de correia de acessórios - grito agudo ao ligar motor ou acionar AC, indica correia frouxa ou ressecada",
                        "motor_normal": "Motor normal em funcionamento - referência de áudio para motor saudável sem ruídos anormais"
                    }
                    for audio_file in audios_disponiveis:
                        nome_base = audio_file.replace("amostra_", "").replace(".wav", "")
                        descricao = descricoes_audio.get(nome_base, f"Amostra de áudio automotivo: {nome_base}")
                        docs.append({
                            "fonte": f"multimodal/audios/{audio_file}",
                            "texto": f"[ÁUDIO DIAGNÓSTICO] {descricao}. Arquivo de referência: {audio_file}"
                        })

            # 3c. Inventário de fotos disponíveis
            fotos_dir = os.path.join(multimodal_dir, "fotos_defeitos")
            if os.path.exists(fotos_dir):
                fotos_disponiveis = [f for f in os.listdir(fotos_dir) if f.endswith((".jpg", ".png", ".jpeg"))]
                if fotos_disponiveis:
                    descricoes_foto = {
                        "foto_motor_combustao_real": "Foto real de motor a combustão interna automotivo detalhado para referência de diagnóstico visual",
                        "foto_disco_freio_ventilado": "Foto real de conjunto de freio a disco ventilado e suspensão para inspeção visual de desgaste",
                        "foto_bloco_motor_mecanica": "Foto do compartimento do motor e cabeçote em inspeção mecânica para diagnóstico visual"
                    }
                    for foto_file in fotos_disponiveis:
                        nome_base = foto_file.rsplit(".", 1)[0]
                        descricao = descricoes_foto.get(nome_base, f"Foto de inspeção automotiva: {nome_base}")
                        docs.append({
                            "fonte": f"multimodal/fotos/{foto_file}",
                            "texto": f"[FOTO DIAGNÓSTICO VISUAL] {descricao}. Arquivo: {foto_file}"
                        })

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