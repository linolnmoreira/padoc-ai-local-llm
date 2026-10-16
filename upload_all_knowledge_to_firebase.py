import os
import logging
from firebase_integration import inicializar_firebase, salvar_aprendizado

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of files to upload as knowledge entries
BASE_DIR = os.path.dirname(__file__)
FILES_TO_UPLOAD = [
    "knowledge_base.json",
    "manuals.txt",
    "manual_motor.txt",
    "toyota.txt",
    "defeitos.txt",
    "defeitos.csv",
    "codigos_obd2.csv",
]

def ler_conteudo(arquivo):
    caminho = os.path.join(BASE_DIR, arquivo)
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Erro ao ler {arquivo}: {e}")
        return None

def publicar_conteudo(nome, conteudo):
    if not conteudo:
        logger.warning(f"Conteúdo vazio para {nome}, pulando.")
        return False
    pergunta = f"{nome}"
    resposta = conteudo
    return salvar_aprendizado(pergunta, resposta)

def main():
    if not inicializar_firebase():
        logger.error("Firebase não inicializado. Abortando upload.")
        return
    sucesso_total = 0
    for arquivo in FILES_TO_UPLOAD:
        conteudo = ler_conteudo(arquivo)
        if publicar_conteudo(arquivo, conteudo):
            sucesso_total += 1
            logger.info(f"✅ {arquivo} enviado com sucesso.")
        else:
            logger.error(f"❌ Falha ao enviar {arquivo}.")
    logger.info(f"Upload concluído: {sucesso_total}/{len(FILES_TO_UPLOAD)} arquivos enviados.")

if __name__ == "__main__":
    main()
