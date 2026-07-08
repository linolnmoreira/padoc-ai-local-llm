"""
Script para indexar toda a base de conhecimento JSON no ChromaDB.
Execute este arquivo sempre que os arquivos em 'knowledge/' forem atualizados.
"""
import os
from brain.rag.vector_search import SemanticKnowledgeBase

def main():
    print("Iniciando processo de indexação semântica...")
    
    # Inicializa a base de conhecimento vetorial
    knowledge_base = SemanticKnowledgeBase(persist_directory="chroma_db")

    # Lista de arquivos JSON a serem indexados
    knowledge_files = [
        "knowledge/historico_ordens_servico.json",
        "knowledge/defeitos_mecanicos_e_manutencao.json",
        "knowledge/problemas_conhecidos_por_modelo.json"
    ]

    for file_path in knowledge_files:
        knowledge_base.index_knowledge(file_path)

    print("\nProcesso de indexação concluído!")

if __name__ == "__main__":
    main()