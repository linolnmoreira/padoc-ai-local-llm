"""
PADOC AI
Leitor de manuais PDF para extração de conhecimento.
Requer: pip install pypdf
"""

from pypdf import PdfReader
import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "dados", "treinamentos.json")


def extrair_manual(arquivo_pdf):
    """Extrai todo o texto de um arquivo PDF."""
    if not os.path.exists(arquivo_pdf):
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {arquivo_pdf}")

    leitor = PdfReader(arquivo_pdf)
    texto = ""

    for pagina in leitor.pages:
        texto += pagina.extract_text() or ""

    return texto


def salvar_conhecimento(texto):
    """Salva o texto extraído em um arquivo JSON de conhecimento."""
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    dados = {
        "manual": texto
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

    print(f"Conhecimento salvo em: {OUTPUT_FILE}")