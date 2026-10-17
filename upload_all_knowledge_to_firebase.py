import os
import json
import logging
from datetime import datetime
from firebase_admin import db
from firebase_integration import inicializar_firebase, salvar_aprendizado

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(__file__)
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")

FILES_TO_UPLOAD = [
    "knowledge_base.json",
    "manuals.txt",
    "manual_motor.txt",
    "toyota.txt",
    "defeitos.txt",
    "defeitos.csv",
    "codigos_obd2.csv",
]

def sanitizar_para_firebase(data):
    """Substitui caracteres proibidos pelo Firebase RTDB (. $ # [ ] /) em chaves de dicionário."""
    if isinstance(data, dict):
        novo = {}
        for k, v in data.items():
            k_limpo = str(k).replace(".", "_").replace("$", "_").replace("#", "_").replace("[", "_").replace("]", "_").replace("/", "_")
            novo[k_limpo] = sanitizar_para_firebase(v)
        return novo
    elif isinstance(data, list):
        return [sanitizar_para_firebase(item) for item in data]
    return data

def ler_conteudo(arquivo):
    caminho = os.path.join(BASE_DIR, arquivo)
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Erro ao ler {arquivo}: {e}")
        return None

def ler_json(caminho):
    try:
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao ler json {caminho}: {e}")
    return None

def publicar_cerebro_firebase():
    """Publica no Firebase Realtime Database os dados estruturados do cérebro atualizado."""
    logger.info("📤 Publicando auditoria e dados atualizados do cérebro no Firebase Realtime Database...")
    
    # 1. Auditoria geral do cérebro
    relatorio_path = os.path.join(KNOWLEDGE_DIR, "_relatorio_cerebro.json")
    relatorio = ler_json(relatorio_path)
    if relatorio:
        db.reference("cerebro_ia/auditoria").set(sanitizar_para_firebase(relatorio))
        logger.info("✅ Auditoria do cérebro enviada para /cerebro_ia/auditoria")

    # 2. Recalls reais (NHTSA)
    recalls_path = os.path.join(KNOWLEDGE_DIR, "nhtsa_recalls_veiculos.json")
    recalls = ler_json(recalls_path)
    if recalls:
        amostra = recalls[:30] if isinstance(recalls, list) else recalls
        total = len(recalls) if isinstance(recalls, list) else 1
        db.reference("cerebro_ia/recalls").set(sanitizar_para_firebase({
            "total": total,
            "amostra": amostra,
            "atualizado_em": datetime.now().isoformat()
        }))
        logger.info(f"✅ Recalls enviados para /cerebro_ia/recalls ({total} registros)")

    # 3. Reclamações reais de donos
    reclamacoes_path = os.path.join(KNOWLEDGE_DIR, "nhtsa_reclamacoes_donos.json")
    reclamacoes = ler_json(reclamacoes_path)
    if reclamacoes:
        amostra = reclamacoes[:30] if isinstance(reclamacoes, list) else reclamacoes
        total = len(reclamacoes) if isinstance(reclamacoes, list) else 1
        db.reference("cerebro_ia/reclamacoes").set(sanitizar_para_firebase({
            "total": total,
            "amostra": amostra,
            "atualizado_em": datetime.now().isoformat()
        }))
        logger.info(f"✅ Reclamações enviadas para /cerebro_ia/reclamacoes ({total} registros)")

    # 4. Resumo de códigos OBD-II e DTCs
    obd_pt_path = os.path.join(KNOWLEDGE_DIR, "obdii_codigos_genericos_ptbr.json")
    obd_pt = ler_json(obd_pt_path)
    if obd_pt:
        amostra = obd_pt[:25] if isinstance(obd_pt, list) else obd_pt
        total = len(obd_pt) if isinstance(obd_pt, list) else 1
        db.reference("cerebro_ia/obdii_resumo").set(sanitizar_para_firebase({
            "total_codigos_ptbr": total,
            "amostra": amostra,
            "atualizado_em": datetime.now().isoformat()
        }))
        logger.info(f"✅ Resumo OBD-II enviado para /cerebro_ia/obdii_resumo ({total} códigos)")

def main():
    if not inicializar_firebase():
        logger.error("Firebase não inicializado. Abortando upload.")
        return

    # Upload arquivos de texto/base
    sucesso_total = 0
    for arquivo in FILES_TO_UPLOAD:
        conteudo = ler_conteudo(arquivo)
        if conteudo and salvar_aprendizado(f"{arquivo}", conteudo):
            sucesso_total += 1
            logger.info(f"✅ {arquivo} enviado com sucesso.")
        else:
            logger.error(f"❌ Falha ao enviar {arquivo}.")
    
    # Upload cérebro estruturado
    publicar_cerebro_firebase()

    logger.info(f"🎉 Deploy no Firebase Database concluído com sucesso! {sucesso_total}/{len(FILES_TO_UPLOAD)} arquivos de texto + cérebro IA estruturado.")

if __name__ == "__main__":
    main()
