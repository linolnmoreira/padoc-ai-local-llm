"""
API REST para PADOC AI usando Flask

Expõe a inteligência unificada da PADOC AI:
- Diagnósticos mecânicos e elétricos via Cérebro Especialista (PadocBrainEngine)
- Telemetria veicular preditiva (PadocPredictiveAI)
- Auto-Aprendizado contínuo (/api/aprender)
- Auditoria e persistência via Firebase (quando configurado)
"""

import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

from brain.padoc_brain_engine import brain_engine
from predictive_vehicle_ai import predictive_engine
from firebase_integration import (
    inicializar_firebase,
    salvar_diagnostico,
    salvar_evento,
    obter_estatisticas_globais
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("padoc_api")

app = Flask(__name__)
CORS(app)

firebase_pronto = False
try:
    if inicializar_firebase():
        firebase_pronto = True
        logger.info("✅ Conexão com Firebase estabelecida.")
    else:
        logger.warning("⚠️ Firebase em modo offline/local.")
except Exception as e:
    logger.warning(f"⚠️ Firebase não inicializado: {e}")


@app.route('/', methods=['GET'])
@app.route('/api/saude', methods=['GET'])
def health_check():
    """Verifica o status da API, Cérebro IA, Engine Preditivo e Banco."""
    return jsonify({
        "status": "ok",
        "versao": "2.5.0",
        "cerebro_ia": True,
        "engine_preditivo": True,
        "padroes_aprendidos": len(brain_engine.learner.memoria.get("padroes_aprendidos", {})),
        "firebase_pronto": firebase_pronto,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/diagnostico', methods=['POST'])
def diagnostico():
    """Endpoint principal de diagnóstico automotivo."""
    dados = request.get_json() or {}
    pergunta = dados.get("pergunta", "").strip()
    usuario_id = dados.get("usuario_id", "anonimo")
    contexto = dados.get("contexto", {})

    if not pergunta:
        return jsonify({"sucesso": False, "erro": "O campo 'pergunta' é obrigatório."}), 400

    logger.info(f"Diagnóstico solicitado por '{usuario_id}': '{pergunta[:80]}...'")

    try:
        resultado = brain_engine.processar_diagnostico(
            pergunta=pergunta,
            usuario_id=usuario_id,
            contexto_veiculo=contexto
        )

        if firebase_pronto:
            try:
                salvar_diagnostico(usuario_id, pergunta, resultado.get("resposta", ""))
            except Exception as fe:
                logger.warning(f"Aviso ao salvar no Firebase: {fe}")

        return jsonify(resultado)

    except Exception as e:
        logger.error(f"❌ Erro ao processar diagnóstico: {e}", exc_info=True)
        return jsonify({"sucesso": False, "erro": f"Erro interno no diagnóstico: {str(e)}"}), 500


@app.route('/api/evento', methods=['POST'])
def evento_veicular():
    """
    Recebe telemetria do veículo e executa análise de saúde dos componentes
    com cálculo de risco de falha em 7, 30 e 90 dias.
    """
    dados = request.get_json() or {}
    placa = dados.get("placa", dados.get("vehicle_id", "PADOC-001"))
    dados_telemetria = dados.get("dados_evento", dados.get("telemetria", dados))
    tipo_evento = dados.get("tipo_evento", "telemetria_continua")

    try:
        analise_preditiva = predictive_engine.processar_telemetria_json(
            vehicle_id=placa,
            dados=dados_telemetria
        )

        if firebase_pronto:
            try:
                salvar_evento(placa, tipo_evento, analise_preditiva)
            except Exception as fe:
                logger.warning(f"Aviso ao salvar evento no Firebase: {fe}")

        return jsonify({
            "sucesso": True,
            "veiculo_id": placa,
            "tipo_evento": tipo_evento,
            "analise_preditiva": analise_preditiva,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"❌ Erro ao processar telemetria preditiva: {e}", exc_info=True)
        return jsonify({"sucesso": False, "erro": f"Erro na análise preditiva: {str(e)}"}), 500


@app.route('/api/aprender', methods=['POST'])
def aprender():
    """
    Endpoint de Auto-Aprendizado:
    Mecânicos e oficinas registram a causa real confirmada e a solução eficaz.
    """
    dados = request.get_json() or {}
    problema = dados.get("problema", "").strip()
    solucao = dados.get("solucao", "").strip()
    veiculo = dados.get("veiculo", "Geral")
    eficacia = float(dados.get("eficacia", 1.0))
    autor = dados.get("autor", "oficina_parceira")

    if not problema or not solucao:
        return jsonify({"sucesso": False, "erro": "Campos 'problema' e 'solucao' são obrigatórios."}), 400

    resultado = brain_engine.retroalimentar_aprendizado(
        problema=problema,
        solucao=solucao,
        veiculo=veiculo,
        eficacia=eficacia,
        autor=autor
    )

    return jsonify(resultado)


@app.route('/api/estatisticas', methods=['GET'])
def stats():
    """Retorna estatísticas do Firebase e da memória da IA."""
    dados_aprendizado = brain_engine.learner.memoria
    stats_locais = {
        "padroes_aprendidos": len(dados_aprendizado.get("padroes_aprendidos", {})),
        "total_diagnosticos": dados_aprendizado.get("total_diagnosticos_processados", 0),
        "feedback_positivo": dados_aprendizado.get("feedback_positivo", 0),
        "historico_recente": dados_aprendizado.get("historico_recente", [])[:10]
    }

    if firebase_pronto:
        try:
            stats_fb = obter_estatisticas_globais()
            stats_locais["firebase"] = stats_fb
        except Exception:
            pass

    return jsonify(stats_locais)


if __name__ == '__main__':
    logger.info("🚀 Iniciando Servidor PADOC AI na porta 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)