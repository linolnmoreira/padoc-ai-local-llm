import json
import logging
import os

from firebase_integration import inicializar_firebase, salvar_aprendizado

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.json")

def carregar_conhecimento():
    """Carrega o arquivo knowledge_base.json como dicionário."""
    try:
        with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"✅ Base de conhecimento carregada com {len(data)} itens.")
        return data
    except Exception as e:
        logger.error(f"❌ Erro ao ler knowledge_base.json: {e}")
        return {}

def publicar_conhecimento():
    """Publica cada entrada da base de conhecimento no Firebase usando salvar_aprendizado.
    Cada chave (ex: P0300) será transformada em uma pergunta; a resposta será um resumo
    contendo problema, causas e solução. Salva em `/conhecimento/<hash>`.
    """
    if not inicializar_firebase():
        logger.error("⚠️ Firebase não inicializado. Abortando upload.")
        return

    conhecimento = carregar_conhecimento()
    if not conhecimento:
        logger.warning("⚠️ Nenhum dado para publicar.")
        return

    sucesso_total = 0
    for codigo, detalhe in conhecimento.items():
        pergunta = f"Código de erro {codigo}"
        resposta = (
            f"Problema: {detalhe.get('problema', '')}\n"
            f"Causas: {', '.join(detalhe.get('causas', []))}\n"
            f"Solução: {detalhe.get('solucao', '')}"
        )
        if salvar_aprendizado(pergunta, resposta):
            sucesso_total += 1
        else:
            logger.error(f"Falha ao salvar conhecimento para {codigo}")
    logger.info(f"✅ Upload concluído. {sucesso_total}/{len(conhecimento)} itens publicados.")

if __name__ == "__main__":
    publicar_conhecimento()
