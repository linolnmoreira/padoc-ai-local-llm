from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json
import os
from datetime import datetime

# Importar os módulos da PADOC AI
from core.agent import PadocAgent
from core.memory import VehicleMemory, carregar_historico_geral
from brain.rag.vector_search import SemanticKnowledgeBase # NOVO: Busca Semântica
from vision.vision_ai import PadocVision
from business.budget import BudgetAI
from business.scheduling import SchedulerAI
from business.parts_agent import PartsAgent
from memory.aprendizado import buscar_conhecimento, aprender
from brain.modelo_ia import PadocAI # Importa a classe principal com o LLM
# NOVO: Importar os novos analisadores de dados
from pdf_ai import PDFAI
from telemetry_ai import TelemetryAI
from video_ai import VideoAI
from wiring_ai import WiringAI

# from learning.vehicle_learning import FleetLearning # Não usado diretamente na API de interação

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Inicialização dos componentes da PADOC AI ---
# Estes componentes são inicializados uma vez quando a API é iniciada.
# A inicialização do LLM e da Visão pode ser demorada e consumir muita RAM/VRAM.
try:
    padoc_ai_instance = PadocAI() # Carrega o LLM e os módulos de voz
    padoc_agent = PadocAgent(llm_instance=padoc_ai_instance.llm) # NOVO: Agente com LLM
    padoc_memory = VehicleMemory()
    padoc_semantic_db = SemanticKnowledgeBase() # NOVO: Banco de dados vetorial
    padoc_vision = PadocVision() # Carrega o modelo YOLOv8n
    padoc_budget_ai = BudgetAI()
    padoc_scheduler_ai = SchedulerAI()
    padoc_parts_agent = PartsAgent()
    # NOVO: Instanciar os novos analisadores
    pdf_analyzer = PDFAI()
    telemetry_analyzer = TelemetryAI()
    video_analyzer = VideoAI()
    wiring_analyzer = WiringAI()


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

    try:
        dados = request.get_json()
        mensagem_motorista = dados.get("pergunta", "").strip()
        placa_veiculo = dados.get("usuario_id", "").strip().upper()
        imagem_path = dados.get("imagem_path", "").strip() # Para análise de imagem
        # NOVO: Receber caminhos para os novos tipos de arquivo
        pdf_path = dados.get("pdf_path", "").strip()
        video_path = dados.get("video_path", "").strip()
        wiring_path = dados.get("wiring_path", "").strip()
        telemetry_data = dados.get("telemetry_data", None) # Recebe dados de telemetria

        codigo_obd = dados.get("codigo_obd", "").strip().upper() # Para diagnóstico OBD direto

        if not any([mensagem_motorista, imagem_path, codigo_obd, pdf_path, video_path, wiring_path, telemetry_data]):
            return jsonify({"sucesso": False, "erro": "Mensagem, imagem ou código OBD são obrigatórios"}), 400

        # NOVO: Primeiro, buscar na base de aprendizado incremental
        conhecimento_previo = buscar_conhecimento(mensagem_motorista)
        if conhecimento_previo:
            logger.info(f"Resposta encontrada na base de aprendizado incremental para '{mensagem_motorista[:50]}...'")
            return jsonify({
                "sucesso": True,
                "resposta": conhecimento_previo['resposta'],
                "fonte": "Base de Conhecimento Rápida",
                "timestamp": datetime.now().isoformat()
            }), 200

        # NOVO: Se houver múltiplos inputs, usar o diagnóstico multimodal
        is_multimodal = sum([bool(imagem_path), bool(pdf_path), bool(video_path), bool(wiring_path), bool(telemetry_data)]) > 0

        if is_multimodal:
            logger.info(f"Requisição multimodal recebida para placa '{placa_veiculo}'.")
            # Chama o orquestrador multimodal e passa os analisadores e caminhos
            resposta_final = padoc_ai_instance.diagnostico_multimodal(
                caminho_foto=imagem_path,
                placa=placa_veiculo,
                codigo_obd=codigo_obd,
                # Passando os novos dados e analisadores
                pdf_path=pdf_path,
                video_path=video_path,
                wiring_path=wiring_path,
                telemetry_data=telemetry_data,
                pdf_analyzer=pdf_analyzer,
                video_analyzer=video_analyzer,
                wiring_analyzer=wiring_analyzer,
                telemetry_analyzer=telemetry_analyzer
            )
            return jsonify({"sucesso": True, "resposta": resposta_final, "timestamp": datetime.now().isoformat()}), 200

        # 1. Memória do Veículo
        historico_veiculo = "Nenhum histórico disponível."
        if placa_veiculo:
            carro = padoc_memory.memoria(placa_veiculo)
            if carro:
                historico_veiculo = carro.historico
            else:
                # Se o carro não existe, podemos criar um registro básico ou pedir mais dados
                # Por simplicidade, aqui apenas notamos que não há histórico
                historico_veiculo = f"Veículo com placa {placa_veiculo} não encontrado na memória."

        # 2. Análise de Imagem (se fornecida)
        defeito_imagem = "Nenhuma imagem fornecida para análise."
        if imagem_path:
            defeito_imagem = padoc_vision.analisar(imagem_path)
            defeito_imagem = f"Análise de imagem: {defeito_imagem}"

        # 3. NOVO: Busca Semântica na base de conhecimento
        # A busca agora é feita com base no significado da pergunta do usuário.
        conhecimento_semantico = padoc_semantic_db.search(mensagem_motorista)

        # 5. Carregar histórico recente de interações gerais para contexto de curto prazo
        historico_recente = carregar_historico_geral(linhas_max=5)
        contexto_recente = " ".join([f"Pergunta anterior: {h.get('pergunta')} Resposta dada: {h.get('resposta')}" for h in historico_recente])

        # Construir o contexto para o LLM
        contexto_llm = f"""
        Histórico do Veículo (Placa: {placa_veiculo}): {historico_veiculo}
        Análise de Imagem: {defeito_imagem}
        ---
        Base de Conhecimento Relevante (encontrada por busca semântica):
        {conhecimento_semantico}
        ---
        Contexto de Interações Recentes na Oficina: {contexto_recente}
        """

        # NOVO: Usar o agente para decidir a ferramenta a ser chamada
        tool_call = padoc_agent.decide_tool(mensagem_motorista)
        acao = tool_call.get("tool_name")
        argumentos = tool_call.get("arguments", {})
        resposta_final = ""

        if acao == "gerar_orcamento":
            orcamento_gerado = padoc_budget_ai.gerar(argumentos.get("servico", "Não especificado"), argumentos.get("pecas", []))
            resposta_final = f"PADOC AI (Orçamento): {json.dumps(orcamento_gerado, indent=2, ensure_ascii=False)}"
        
        elif acao == "criar_agendamento":
            agendamento = padoc_scheduler_ai.criar_agendamento("Cliente Teste", "Oficina PADOC", argumentos.get("data", "Não especificada"))
            resposta_final = f"PADOC AI (Agendamento): {json.dumps(agendamento, indent=2, ensure_ascii=False)}"
        
        elif acao == "escolher_melhor_peca":
            melhor_peca = padoc_parts_agent.escolher_melhor(argumentos.get("peca", "Não especificada"))
            resposta_final = f"PADOC AI (Peças): {json.dumps(melhor_peca, indent=2, ensure_ascii=False)}"
        
        else: # acao == "diagnostico_geral"
            # O LLM responderá com base no contexto e na pergunta do motorista
            # Usamos o método 'responder' da instância principal que já tem o LLM carregado
            resposta_final = padoc_ai_instance.llm(f"{contexto_llm}\n\nPergunta: {mensagem_motorista}\n\nResposta:", max_tokens=400)['choices'][0]['text'].strip()

        # Opcional: Salvar o diagnóstico no histórico do veículo
        if placa_veiculo and carro:
            historico_json = json.loads(carro.historico)
            historico_json["historico_diagnosticos"].append({
                "pergunta": mensagem_motorista,
                "resposta": resposta_final,
                "timestamp": datetime.now().isoformat()
            })
            padoc_memory.salvar(placa_veiculo, carro.modelo, carro.km, json.dumps(historico_json))

        # MELHORIA: Aprender com a nova interação, independentemente da ação,
        # desde que uma resposta final tenha sido gerada.
        aprender(mensagem_motorista, resposta_final)

        return jsonify({
            "sucesso": True,
            "resposta": resposta_final,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Erro ao processar requisição de diagnóstico: {e}", exc_info=True)
        return jsonify({
            "sucesso": False,
            "erro": str(e)
        }), 500


@app.route('/api/veiculo/salvar', methods=['POST'])
def salvar_veiculo_api():
    """Endpoint para salvar ou atualizar dados de um veículo."""
    try:
        dados = request.get_json()
        placa = dados.get("placa", "").strip().upper()
        modelo = dados.get("modelo", "").strip()
        km = dados.get("km", 0, type=int)
        historico = dados.get("historico", "{}") # Deve ser um JSON string

        if not placa or not modelo or not km:
            return jsonify({"sucesso": False, "erro": "Placa, modelo e KM são obrigatórios"}), 400
        
        # Verificar se já existe e atualizar, ou criar novo
        carro_existente = padoc_memory.memoria(placa)
        if carro_existente:
            # Lógica para atualizar (SQLite não tem update direto com o método salvar)
            # Para um update real, VehicleMemory precisaria de um método 'atualizar'
            # Por simplicidade, aqui vamos apenas "salvar" um novo registro, o que não é ideal para updates.
            # Uma implementação robusta usaria `db.query(Vehicle).filter_by(placa=placa).update(...)`
            return jsonify({"sucesso": False, "erro": "Veículo já existe. Implementar lógica de atualização."}), 409
        else:
            padoc_memory.salvar(placa, modelo, km, historico)
            return jsonify({"sucesso": True, "mensagem": f"Veículo {placa} salvo com sucesso."}), 201

    except Exception as e:
        logger.error(f"Erro ao salvar veículo: {e}")
        return jsonify({"sucesso": False, "erro": str(e)}), 500


@app.route('/api/veiculo/<string:placa>', methods=['GET'])
def buscar_veiculo_api(placa):
    """Endpoint para buscar dados de um veículo pela placa."""
    try:
        carro = padoc_memory.memoria(placa.upper())
        if carro:
            return jsonify({
                "sucesso": True,
                "placa": carro.placa,
                "modelo": carro.modelo,
                "km": carro.km,
                "historico": json.loads(carro.historico) # Retorna como objeto JSON
            }), 200
        else:
            return jsonify({"sucesso": False, "erro": "Veículo não encontrado"}), 404
    except Exception as e:
        logger.error(f"Erro ao buscar veículo: {e}")
        return jsonify({"sucesso": False, "erro": str(e)}), 500


@app.route('/api/obd/dados_motor', methods=['GET'])
def get_obd_dados_motor():
    """Endpoint para obter dados do motor via OBD2 em tempo real."""
    if not ia_pronta:
        return jsonify({"sucesso": False, "erro": "PADOC AI não inicializado"}), 500
    
    try:
        if padoc_obd_scanner.conectar():
            dados = padoc_obd_scanner.dados_motor()
            return jsonify({"sucesso": True, "dados_motor": dados}), 200
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

    try:
        dados = request.get_json()
        imagem_path = dados.get("imagem_path", "").strip()

        if not imagem_path:
            return jsonify({"sucesso": False, "erro": "Caminho da imagem é obrigatório"}), 400

        resultado = padoc_vision.analisar(imagem_path)
        return jsonify({"sucesso": True, "deteccoes": resultado}), 200
    except Exception as e:
        logger.error(f"Erro ao analisar imagem: {e}")
        return jsonify({"sucesso": False, "erro": str(e)}), 500


if __name__ == '__main__':
    # Para desenvolvimento:
    app.run(debug=True, host="0.0.0.0", port=5000)
    
    # Para produção, usar Gunicorn (exemplo):
    # gunicorn -w 4 -b 0.0.0.0:5000 api:app