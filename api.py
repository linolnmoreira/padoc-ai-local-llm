from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json
import os
import tempfile
from werkzeug.utils import secure_filename
from datetime import datetime

# --- Importações dos Módulos PADOC AI ---
from agent import PadocAgent
from llm_local import responder as responder_rapido # 'aprender' foi movido para o Firebase
from firebase_integration import inicializar_firebase, salvar_diagnostico, obter_diagnosticos_usuario, salvar_aprendizado # IMPORTAR A NOVA FUNÇÃO
from brain.modelo_ia import get_padoc_instance # Cérebro principal com LLM
from detect import PadocVision
from budget import BudgetAI
# from scheduling import SchedulerAI # Descomente se tiver o módulo
# from parts_agent import PartsAgent # Descomente se tiver o módulo
from elm327 import LeitorTelemetriaOBD

# NOVO: Importar os novos analisadores de dados
from audio_ai import AudioAI
from image_ai import ImageAI

# from learning.vehicle_learning import FleetLearning # Não usado diretamente na API de interação

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Inicialização dos componentes da PADOC AI ---
# Estes componentes são inicializados uma vez quando a API é iniciada.
# A inicialização do LLM e da Visão pode ser demorada e consumir muita RAM/VRAM.
try:
    # ** PASSO 1: INICIALIZAR O FIREBASE **
    inicializar_firebase()

    padoc_ai_instance = get_padoc_instance() # Carrega o LLM e os módulos de voz
    padoc_agent = PadocAgent()
    padoc_vision = PadocVision() # Carrega o modelo YOLOv8n
    padoc_budget_ai = BudgetAI()
    # padoc_scheduler_ai = SchedulerAI()
    # padoc_parts_agent = PartsAgent()

    # NOVO: Instanciar os novos analisadores
    audio_analyzer = AudioAI()
    image_analyzer = ImageAI()

    padoc_obd_scanner = LeitorTelemetriaOBD()


    logger.info("✓ PADOC AI Core inicializado com sucesso.")
    ia_pronta = True
except Exception as e:
    logger.error(f"✗ Erro ao inicializar PADOC AI Core: {e}")
    ia_pronta = False
    # Em um ambiente de produção, você pode querer sair ou ter um fallback.


@app.route('/api/saude', methods=['GET'])
def saude():
    """Verifica se a API está funcionando e se a IA está pronta."""
    return jsonify({
        "status": "ok",
        "ia_pronta": ia_pronta,
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/diagnostico', methods=['POST'])
def diagnostico_geral():
    """
    Endpoint principal para interagir com a PADOC AI.
    Usa o PadocAgent para determinar a intenção e direcionar a requisição.
    """
    if not ia_pronta:
        return jsonify({"sucesso": False, "erro": "PADOC AI não inicializado"}), 500

    imagem_path = None
    temp_dir = None

    try:
        # Lida com 'multipart/form-data' (com upload de arquivo) ou 'application/json'
        if request.content_type.startswith('multipart/form-data'):
            dados = request.form
            if 'imagem' in request.files:
                imagem_file = request.files['imagem']
                if imagem_file.filename != '':
                    # Cria um diretório temporário seguro para salvar o upload
                    temp_dir = tempfile.mkdtemp()
                    filename = secure_filename(imagem_file.filename)
                    imagem_path = os.path.join(temp_dir, filename)
                    imagem_file.save(imagem_path)
        else:
            dados = request.get_json()

        mensagem_motorista = dados.get("pergunta", "").strip()
        usuario_id = dados.get("usuario_id", "anonimo").strip()
        
        # Se a imagem não veio por upload, verifica se o caminho foi passado no JSON (para testes)
        if not imagem_path:
            imagem_path = dados.get("imagem_path", "").strip()

        # Inputs adicionais para diagnóstico multimodal
        telemetria = dados.get("telemetria", None)
        codigo_obd = dados.get("codigo_obd", "").strip().upper()

        if not any([mensagem_motorista, imagem_path, codigo_obd, telemetria]):
            return jsonify({"sucesso": False, "erro": "Mensagem, imagem ou código OBD são obrigatórios"}), 400

        # 1. Tenta responder com a memória de aprendizado rápido (JSON)
        conhecimento_previo = responder_rapido(mensagem_motorista)
        if conhecimento_previo:
            logger.info(f"Resposta encontrada na base de aprendizado incremental para '{mensagem_motorista[:50]}...'")
            return jsonify({
                "sucesso": True,
                "resposta": conhecimento_previo,
                "fonte": "Base de Conhecimento Rápida",
                "timestamp": datetime.now().isoformat()
            }), 200

        # 2. Se não encontrou na memória rápida, o AGENTE orquestra a resposta.
        logger.info(f"Agente processando a requisição: '{mensagem_motorista[:50]}...'")

        # O agente decide qual ferramenta usar e executa a tarefa.
        resposta_final = padoc_agent.executar_tarefa(
            mensagem=mensagem_motorista,
            usuario_id=usuario_id,
            ferramentas={
                "diagnostico": padoc_ai_instance,
                "orcamento": padoc_budget_ai,
                # Adicione outras ferramentas aqui quando disponíveis
                # "agendamento": padoc_scheduler_ai,
            },
            # Passa dados extras que as ferramentas possam precisar
            dados_extras={
                "codigo_obd": codigo_obd,
                "telemetria": telemetria
            }
        )

        # 3. Salva a nova interação para aprendizado futuro no FIREBASE
        salvar_aprendizado(mensagem_motorista, resposta_final)

        # 4. Salva o diagnóstico no Firebase para histórico do usuário
        salvar_diagnostico(usuario_id, mensagem_motorista, resposta_final)

        return jsonify({
            "sucesso": True,
            "resposta": resposta_final,
            "fonte": "PADOC AI LLM",
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Erro ao processar requisição de diagnóstico: {e}", exc_info=True)
        return jsonify({
            "sucesso": False,
            "erro": f"Ocorreu um erro interno no servidor: {e}"
        }), 500
    finally:
        # Garante que o arquivo temporário seja sempre excluído
        if imagem_path and temp_dir and os.path.exists(imagem_path):
            os.remove(imagem_path)
        if temp_dir and os.path.exists(temp_dir):
            os.rmdir(temp_dir)


@app.route('/api/historico/<string:usuario_id>', methods=['GET'])
def buscar_historico_usuario(usuario_id):
    """Endpoint para buscar o histórico de diagnósticos de um usuário no Firebase."""
    if not ia_pronta:
        return jsonify({"sucesso": False, "erro": "PADOC AI não inicializado"}), 500

    try:
        limite = request.args.get('limite', 10, type=int)
        historico = obter_diagnosticos_usuario(usuario_id, limite=limite)
        
        if historico:
            return jsonify({
                "sucesso": True,
                "usuario_id": usuario_id,
                "historico": historico
            }), 200
        else:
            return jsonify({"sucesso": False, "erro": "Veículo não encontrado"}), 404
    except Exception as e:
        logger.error(f"Erro ao buscar veículo: {e}")
        return jsonify({"sucesso": False, "erro": str(e)}), 500


@app.route('/api/obd/conectar', methods=['GET'])
def get_obd_dados_motor():
    """Endpoint para obter dados do motor via OBD2 em tempo real."""
    if not ia_pronta:
        return jsonify({"sucesso": False, "erro": "PADOC AI não inicializado"}), 500
    
    try:
        if padoc_obd_scanner.conectar_veiculo():
            dados = padoc_obd_scanner.ler_dados_vivos_criticos()
            codigos_falha = padoc_obd_scanner.ler_codigos_falha_dtc()
            
            return jsonify({"sucesso": True, "dados_motor": dados, "codigos_falha": codigos_falha}), 200
        else:
            return jsonify({"sucesso": False, "erro": "Não foi possível conectar ao scanner OBD2"}), 503
    except Exception as e:
        logger.error(f"Erro ao obter dados OBD: {e}")
        return jsonify({"sucesso": False, "erro": str(e)}), 500


@app.route('/api/vision/analisar_imagem', methods=['POST'])
def analisar_imagem_api():
    """Endpoint para analisar uma imagem de defeito."""
    if not ia_pronta:
        return jsonify({"sucesso": False, "erro": "PADOC AI não inicializado"}), 500

    imagem_path = None
    temp_dir = None
    try:
        if 'imagem' not in request.files:
            return jsonify({"sucesso": False, "erro": "Nenhum arquivo de imagem enviado. Use o campo 'imagem'."}), 400

        imagem_file = request.files['imagem']
        if imagem_file.filename == '':
            return jsonify({"sucesso": False, "erro": "Nome de arquivo vazio."}), 400

        # Cria um diretório e arquivo temporários seguros
        temp_dir = tempfile.mkdtemp()
        filename = secure_filename(imagem_file.filename)
        imagem_path = os.path.join(temp_dir, filename)
        imagem_file.save(imagem_path)

        resultado = padoc_vision.analisar(imagem_path)
        return jsonify({"sucesso": True, "deteccoes": resultado}), 200

    except Exception as e:
        logger.error(f"Erro ao analisar imagem: {e}")
        return jsonify({"sucesso": False, "erro": str(e)}), 500
    finally:
        # Garante que o arquivo e o diretório temporários sejam sempre excluídos
        if imagem_path and os.path.exists(imagem_path):
            os.remove(imagem_path)
        if temp_dir and os.path.exists(temp_dir):
            os.rmdir(temp_dir)


if __name__ == '__main__':
    # Para desenvolvimento:
    app.run(debug=True, host="0.0.0.0", port=5000)
    
    # Para produção, usar Gunicorn (exemplo):
    # gunicorn -w 4 -b 0.0.0.0:5000 api:app