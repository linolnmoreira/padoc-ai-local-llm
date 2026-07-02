"""API REST para PADOC AI usando Flask"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from brain.modelo_ia import PadocAI
from memory.memoria import salvar_memoria
from datetime import datetime
import logging
import os

app = Flask(__name__)
allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "*")
CORS(app, origins=allowed_origins)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar IA uma vez ao start da API
ia = None

@app.before_first_request
def inicializar_ia():
    """Inicializar IA na primeira requisição"""
    global ia
    try:
        ia = PadocAI()
        logger.info("✓ PADOC AI inicializado com sucesso")
    except Exception as e:
        logger.error(f"✗ Erro ao inicializar PADOC AI: {e}")


@app.route('/api/diagnostico', methods=['POST'])
def diagnostico():
    """Endpoint para obter diagnóstico automotivo.
    
    Request:
        {
            "pergunta": "Meu carro não pega",
            "usuario_id": "user123"  # Opcional
        }
    
    Response:
        {
            "sucesso": true,
            "resposta": "Possíveis causas...",
            "timestamp": "2026-06-17T10:30:00"
        }
    """
    if ia is None:
        return jsonify({
            "sucesso": False,
            "erro": "PADOC AI não inicializado"
        }), 500
    
    try:
        # Validar entrada
        dados = request.get_json()
        if not dados or "pergunta" not in dados:
            return jsonify({
                "sucesso": False,
                "erro": "Campo 'pergunta' obrigatório"
            }), 400
        
        pergunta = dados["pergunta"].strip()
        if not pergunta or len(pergunta) < 5:
            return jsonify({
                "sucesso": False,
                "erro": "Pergunta muito curta (mínimo 5 caracteres)"
            }), 400
        
        # Gerar diagnóstico
        logger.info(f"Nova pergunta: {pergunta[:50]}...")
        resposta = ia.diagnosticar(pergunta)
        
        # Salvar em histórico
        usuario_id = dados.get("usuario_id", "anonimo")
        salvar_memoria(pergunta, resposta)
        
        return jsonify({
            "sucesso": True,
            "resposta": resposta,
            "usuario_id": usuario_id,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao processar diagnóstico: {e}")
        return jsonify({
            "sucesso": False,
            "erro": str(e)
        }), 500


@app.route('/api/saude', methods=['GET'])
def saude():
    """Verificar se API está funcionando."""
    return jsonify({
        "status": "ok",
        "ia_pronta": ia is not None,
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/historico', methods=['GET'])
def historico():
    """Obter últimos diagnósticos."""
    from memory.memoria import carregar_historico
    
    try:
        linhas = request.args.get("linhas", 10, type=int)
        if linhas > 100:
            linhas = 100  # Limitar para não sobrecarregar
        
        historico_list = carregar_historico(linhas_max=linhas)
        
        return jsonify({
            "total": len(historico_list),
            "historico": historico_list
        }), 200
    except Exception as e:
        logger.error(f"Erro ao recuperar histórico: {e}")
        return jsonify({"erro": str(e)}), 500


@app.errorhandler(404)
def nao_encontrado(erro):
    """Tratamento para rotas não encontradas"""
    return jsonify({
        "erro": "Endpoint não encontrado",
        "status": 404
    }), 404


@app.errorhandler(500)
def erro_interno(erro):
    """Tratamento para erros internos"""
    return jsonify({
        "erro": "Erro interno do servidor",
        "status": 500
    }), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
    
    # Para produção, usar Gunicorn:
    # gunicorn -w 4 -b 0.0.0.0:$PORT api:app
