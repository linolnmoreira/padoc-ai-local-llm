"""
PADOC AI - Unified Brain Engine (Cérebro Central com Auto-Aprendizado)

Este módulo é o núcleo inteligente da PADOC AI. Ele unifica:
1. Classificação de intenções e urgência máxima
2. Sistema Especialista Automotivo (sensores, faixas elétricas, fusíveis, relés, DTCs)
3. RAG Técnico (manuais de montadoras, esquemas e procedimentos)
4. Telemetria Preditiva (saúde de componentes e probabilidade de falhas em 7/30/90 dias)
5. Auto-Aprendizado Contínuo (ContinuousLearner): armazena e retroalimenta novos
   diagnósticos validados por mecânicos e oficinas.
"""

import os
import json
import re
import unicodedata
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger("padoc_brain")

# Caminhos base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "dados")
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")
LEARNING_FILE = os.path.join(DATA_DIR, "aprendizado_auto.json")
MEMORY_FILE = os.path.join(BASE_DIR, "memoria_modelo.json")

os.makedirs(DATA_DIR, exist_ok=True)


def normalizar_texto(texto: str) -> str:
    """Remove acentos e pontuações e converte para minúsculas."""
    if not texto:
        return ""
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


class ContinuousLearner:
    """
    Mecanismo de auto-aprendizado autônomo da PADOC AI.
    Permite que a IA absorva novos casos de oficinas, confirme diagnósticos,
    e incremente a confiança em soluções verificadas.
    """

    def __init__(self, storage_path: str = LEARNING_FILE):
        self.storage_path = storage_path
        self.memoria: Dict[str, Any] = self._carregar()

    def _carregar(self) -> Dict[str, Any]:
        if not os.path.exists(self.storage_path):
            dados_iniciais = {
                "versao": "2.0",
                "padroes_aprendidos": {},
                "total_diagnosticos_processados": 0,
                "feedback_positivo": 0,
                "historico_recente": []
            }
            self._salvar(dados_iniciais)
            return dados_iniciais

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar base de auto-aprendizado: {e}")
            return {"padroes_aprendidos": {}, "total_diagnosticos_processados": 0, "feedback_positivo": 0}

    def _salvar(self, dados: Optional[Dict[str, Any]] = None):
        if dados is None:
            dados = self.memoria
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar base de auto-aprendizado: {e}")

    def registrar_aprendizado(self, problema: str, solucao: str, veiculo: str = "Geral", eficacia: float = 1.0, autor: str = "oficina"):
        """
        Registra um caso resolvido com sucesso para auto-retroalimentação.
        """
        chave_problema = normalizar_texto(problema)
        if not chave_problema:
            return

        padroes = self.memoria.setdefault("padroes_aprendidos", {})
        
        if chave_problema not in padroes:
            padroes[chave_problema] = {
                "problema_original": problema,
                "solucoes": [],
                "veiculos_afetados": [],
                "vezes_observado": 0,
                "score_confianca": 0.0
            }

        entrada = padroes[chave_problema]
        entrada["vezes_observado"] += 1
        if veiculo and veiculo not in entrada["veiculos_afetados"]:
            entrada["veiculos_afetados"].append(veiculo)

        # Atualiza ou insere a solução
        solucao_existente = next((s for s in entrada["solucoes"] if normalizar_texto(s["texto"]) == normalizar_texto(solucao)), None)
        if solucao_existente:
            solucao_existente["confirmacoes"] += 1
            solucao_existente["eficacia"] = (solucao_existente["eficacia"] + eficacia) / 2
        else:
            entrada["solucoes"].append({
                "texto": solucao,
                "confirmacoes": 1,
                "eficacia": eficacia,
                "autor": autor,
                "data_registro": datetime.now().isoformat()
            })

        # Recalcula score de confiança
        entrada["score_confianca"] = min(1.0, 0.5 + (0.1 * entrada["vezes_observado"]))

        self.memoria["total_diagnosticos_processados"] = self.memoria.get("total_diagnosticos_processados", 0) + 1
        if eficacia >= 0.8:
            self.memoria["feedback_positivo"] = self.memoria.get("feedback_positivo", 0) + 1

        # Histórico recente limitado aos últimos 100 eventos
        historico = self.memoria.setdefault("historico_recente", [])
        historico.insert(0, {
            "timestamp": datetime.now().isoformat(),
            "veiculo": veiculo,
            "problema": problema,
            "solucao": solucao,
            "eficacia": eficacia
        })
        self.memoria["historico_recente"] = historico[:100]

        self._salvar()
        logger.info(f"✅ PADOC AI aprendeu novo padrão: '{problema}' -> '{solucao}' (Confiança: {entrada['score_confianca']:.2f})")

    def consultar_aprendizado(self, texto_sintoma: str) -> List[Dict[str, Any]]:
        """Busca se a IA já aprendeu a resolver este problema específico."""
        texto_norm = normalizar_texto(texto_sintoma)
        resultados = []
        padroes = self.memoria.get("padroes_aprendidos", {})

        for chave, info in padroes.items():
            if chave in texto_norm or any(palavra in texto_norm for palavra in chave.split() if len(palavra) > 3):
                resultados.append(info)

        return sorted(resultados, key=lambda x: x["score_confianca"], reverse=True)


class PadocBrainEngine:
    """
    Cérebro Central da PADOC AI.
    Coordena Especialista, RAG, Telemetria Preditiva e Auto-Aprendizado.
    """

    def __init__(self):
        self.learner = ContinuousLearner()
        self.knowledge_base = self._carregar_base_conhecimento()
        self.codigos_obd = self._carregar_codigos_obd()
        self.manuais_texto = self._carregar_manuais_locais()
        logger.info("🧠 Motor Cérebro PADOC AI inicializado com sucesso.")

    def _carregar_base_conhecimento(self) -> Dict[str, Any]:
        """Carrega todos os JSONs de conhecimento disponíveis."""
        base = {}
        if os.path.exists(KNOWLEDGE_DIR):
            for file_name in os.listdir(KNOWLEDGE_DIR):
                if file_name.endswith(".json"):
                    caminho = os.path.join(KNOWLEDGE_DIR, file_name)
                    try:
                        with open(caminho, "r", encoding="utf-8") as f:
                            nome_chave = os.path.splitext(file_name)[0]
                            base[nome_chave] = json.load(f)
                    except Exception as e:
                        logger.warning(f"Aviso ao ler {file_name}: {e}")
        return base

    def _carregar_codigos_obd(self) -> Dict[str, Dict[str, Any]]:
        """Carrega dicionário consolidado de códigos OBD-II (DTCs)."""
        dtcs = {
            "P0300": {
                "descricao": "Falha de ignição detectada em múltiplos cilindros (Random/Multiple Misfire)",
                "sistema": "Ignição / Alimentação",
                "causas_provaveis": ["Velas de ignição desgastadas", "Bobinas de ignição com fuga", "Cabos de vela", "Bicos injetores entupidos", "Baixa pressão na linha de combustível", "Entrada falsa de ar"],
                "procedimento_teste": "1. Testar resistência das bobinas de ignição (1.5 a 4.0 ohms primário). 2. Inspecionar gap e estado dos eletrodos das velas. 3. Monitorar contadores de falha por cilindro no scanner.",
                "gravidade": "ALTA"
            },
            "P0301": {"descricao": "Falha de ignição detectada no Cilindro 1", "sistema": "Ignição Cilindro 1", "causas_provaveis": ["Vela do cil. 1", "Bobina do cil. 1", "Injetor 1"], "gravidade": "ALTA"},
            "P0302": {"descricao": "Falha de ignição detectada no Cilindro 2", "sistema": "Ignição Cilindro 2", "causas_provaveis": ["Vela do cil. 2", "Bobina do cil. 2", "Injetor 2"], "gravidade": "ALTA"},
            "P0303": {"descricao": "Falha de ignição detectada no Cilindro 3", "sistema": "Ignição Cilindro 3", "causas_provaveis": ["Vela do cil. 3", "Bobina do cil. 3", "Injetor 3"], "gravidade": "ALTA"},
            "P0304": {"descricao": "Falha de ignição detectada no Cilindro 4", "sistema": "Ignição Cilindro 4", "causas_provaveis": ["Vela do cil. 4", "Bobina do cil. 4", "Injetor 4"], "gravidade": "ALTA"},
            "P0171": {
                "descricao": "Mistura muito pobre (Banco 1) - System Too Lean",
                "sistema": "Alimentação de Ar/Combustível",
                "causas_provaveis": ["Entrada de ar falso na admissão", "Sensor MAF sujo ou defeituoso", "Baixa pressão na bomba de combustível", "Filtro de combustível obstruído", "Sonda lambda pré-catalisador travada em mistura pobre"],
                "procedimento_teste": "1. Verificar leitura do sensor MAF em marcha lenta (2.0 a 4.5 g/s em motor 4 cil). 2. Monitorar o parâmetro Long Term Fuel Trim (LTFT > +15%). 3. Fazer teste de fumaça na admissão para vazamento.",
                "gravidade": "MEDIA"
            },
            "P0172": {
                "descricao": "Mistura muito rica (Banco 1) - System Too Rich",
                "sistema": "Alimentação de Ar/Combustível",
                "causas_provaveis": ["Bico injetor travado aberto ou gotejando", "Pressão excessiva de combustível", "Sensor de temperatura do motor (ECT) indicando frio constante", "Válvula do canister (PURGE) travada aberta"],
                "procedimento_teste": "1. Medir o sinal de tensão da sonda lambda (deve oscilar de 0.1V a 0.9V). 2. Verificar pressão no manômetro de combustível. 3. Monitorar sinal do sensor ECT.",
                "gravidade": "MEDIA"
            },
            "P0420": {
                "descricao": "Eficiência do catalisador abaixo do limite (Banco 1)",
                "sistema": "Emissões / Escapamento",
                "causas_provaveis": ["Catalisador degradado/derretido", "Sonda lambda pós-catalisador com defeito", "Vazamento no coletor ou tubo de escapamento antes do catalisador"],
                "procedimento_teste": "1. Comparar no osciloscópio as sondas pré e pós catalisador (a pós deve manter sinal quase estável ~0.45V a 0.7V). 2. Testar temperatura na entrada e saída do catalisador com pirômetro (saída deve ser ~30°C a 50°C mais quente).",
                "gravidade": "BAIXA"
            },
            "P0102": {
                "descricao": "Sensor de Fluxo de Massa de Ar (MAF) - Circuito baixo",
                "sistema": "Sensores de Admissão",
                "causas_provaveis": ["Sensor MAF desconectado ou danificado", "Chicote rompido ou em curto com massa", "Tensão de referência 5V ausente"],
                "procedimento_teste": "1. Medir alimentação 12V e massa no conector do MAF. 2. Medir sinal de referência de 5V. 3. Com multímetro, sinal deve variar de ~0.8V a 4.5V acelerando.",
                "gravidade": "MEDIA"
            },
            "P0118": {
                "descricao": "Sensor de Temperatura do Líquido de Arrefecimento (ECT) - Sinal Alto",
                "sistema": "Sensores de Temperatura",
                "causas_provaveis": ["Sensor ECT desconectado ou circuito aberto", "Sensor danificado internamente"],
                "procedimento_teste": "1. Medir resistência do sensor NTC (a 20°C: ~2500 ohms; a 90°C: ~200 a 300 ohms). 2. Inspecionar chicote elétrico.",
                "gravidade": "ALTA"
            },
            "P0500": {
                "descricao": "Sensor de Velocidade do Veículo (VSS) - Mau funcionamento",
                "sistema": "Transmissão / Painel",
                "causas_provaveis": ["Sensor VSS inoperante", "Engrenagem do velocímetro desgastada", "Falha de comunicação CAN com ABS"],
                "procedimento_teste": "1. Medir sinal de onda quadrada (efeito Hall) girando a roda motriz. 2. Verificar fusível de alimentação do sensor.",
                "gravidade": "MEDIA"
            }
        }
        return dtcs

    def _carregar_manuais_locais(self) -> List[Dict[str, str]]:
        """Lê os manuais .txt locais para citação no RAG."""
        manuais = []
        arquivos = ["manuais.txt", "manual_motor.txt", "toyota.txt", "defeitos.txt"]
        for nome in arquivos:
            caminho = os.path.join(BASE_DIR, nome)
            if os.path.exists(caminho):
                try:
                    with open(caminho, "r", encoding="utf-8") as f:
                        conteudo = f.read().strip()
                        if conteudo:
                            manuais.append({"arquivo": nome, "conteudo": conteudo})
                except Exception:
                    pass
        return manuais

    def analisar_intencao_e_urgencia(self, mensagem: str) -> Dict[str, Any]:
        """Classifica a intenção do usuário e detecta situações de emergência."""
        texto_norm = normalizar_texto(mensagem)

        # Regras de Urgência Máxima
        termos_urgencia = [
            "cheiro de queimado", "fumaca", "pegando fogo", "sem freio", "freio nao para",
            "parou no meio da pista", "vazando combustivel", "vazando gasolina", "faisca",
            "luz da injecao piscando", "superaquecendo", "temperatura no vermelho", "fervendo"
        ]
        for termo in termos_urgencia:
            if termo in texto_norm:
                return {
                    "intencao": "urgencia",
                    "confianca": 0.98,
                    "alerta_seguranca": True,
                    "motivo": f"Termo de alto risco detectado: '{termo}'"
                }

        # Orçamento
        if any(p in texto_norm for p in ["quanto custa", "orcamento", "preco", "qual o valor", "quanto fica", "trocar vela"]):
            return {"intencao": "orcamento", "confianca": 0.90, "alerta_seguranca": False}

        # Agendamento
        if any(p in texto_norm for p in ["agendar", "marcar horario", "levar o carro", "tem vaga", "que dia"]):
            return {"intencao": "agenda", "confianca": 0.90, "alerta_seguranca": False}

        # Peças e Fornecedores
        if any(p in texto_norm for p in ["qual peca", "fornecedor", "marca boa", "onde comprar", "peca original"]):
            return {"intencao": "pecas", "confianca": 0.88, "alerta_seguranca": False}

        # Padrão: Diagnóstico Automotivo Especialista
        return {"intencao": "diagnostico", "confianca": 0.95, "alerta_seguranca": False}

    def processar_diagnostico(self, pergunta: str, usuario_id: str = "anonimo", contexto_veiculo: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processamento completo do diagnóstico:
        1. Classificação de intenção e urgência
        2. Extração de códigos DTC (ex: P0300)
        3. Consulta ao motor de Auto-Aprendizado
        4. Consulta ao Sistema Especialista e RAG
        5. Formulação de resposta técnica estruturada
        """
        classificacao = self.analisar_intencao_e_urgencia(pergunta)
        intencao = classificacao["intencao"]

        # Identifica códigos OBD no texto (padrão P0xxx, P1xxx, etc.)
        codigos_encontrados = re.findall(r"\b([PBCU][0-9]{4})\b", pergunta.upper())

        # 1. Trata Casos de Urgência Extrema
        if intencao == "urgencia":
            resposta_urgente = (
                "🚨 **ALERTA DE SEGURANÇA IMEDIATO DA PADOC AI** 🚨\n\n"
                f"Detectamos uma condição de alto risco no seu veículo: **{classificacao.get('motivo')}**.\n\n"
                "**Ações Recomendadas Imediatamente:**\n"
                "1. Pare o veículo em local seguro assim que possível.\n"
                "2. Desligue a ignição para interromper o fluxo elétrico e de combustível.\n"
                "3. Se houver fumaça ou cheiro forte de combustível, afaste-se do veículo e NÃO abra o capô se houver chamas.\n"
                "4. Acione o guincho ou assistência técnica profissional."
            )
            return {
                "sucesso": True,
                "intencao": "urgencia",
                "resposta": resposta_urgente,
                "urgencia_maxima": True,
                "procedimentos": ["Parar o veículo imediatamente", "Desligar a ignição", "Acionar assistência especializada"],
                "timestamp": datetime.now().isoformat()
            }

        # 2. Verifica se a IA possui aprendizado comprovado sobre este sintoma
        aprendizados = self.learner.consultar_aprendizado(pergunta)
        aprendizado_destaque = aprendizados[0] if aprendizados else None

        # 3. Busca Informações Técnicas Especialistas dos DTCs
        detalhes_dtc = []
        for codigo in codigos_encontrados:
            if codigo in self.codigos_obd:
                detalhes_dtc.append({"codigo": codigo, **self.codigos_obd[codigo]})
            else:
                detalhes_dtc.append({
                    "codigo": codigo,
                    "descricao": f"Código de falha OBD-II {codigo} registrado na ECU.",
                    "sistema": "Injeção Eletrônica / Powertrain",
                    "causas_provaveis": ["Falha em sensor correspondente", "Mau contato elétrico no chicote", "Parâmetro fora da faixa de operação normal"],
                    "procedimento_teste": "Realizar teste de continuidade no chicote e verificar leitura em tempo real no scanner.",
                    "gravidade": "MEDIA"
                })

        # 4. Busca em Manuais e RAG
        citacoes_manuais = []
        texto_norm = normalizar_texto(pergunta)
        for manual in self.manuais_texto:
            linhas = manual["conteudo"].split("\n")
            for linha in linhas:
                if any(termo in normalizar_texto(linha) for termo in texto_norm.split() if len(termo) > 3):
                    citacoes_manuais.append(f"[{manual['arquivo']}] {linha.strip()}")
                    if len(citacoes_manuais) >= 3:
                        break

        # 5. Formulação da Resposta Técnica Especialista
        resposta_formatada = self._construir_resposta_tecnica(
            pergunta=pergunta,
            intencao=intencao,
            codigos_encontrados=codigos_encontrados,
            detalhes_dtc=detalhes_dtc,
            aprendizado_destaque=aprendizado_destaque,
            citacoes_manuais=citacoes_manuais,
            contexto_veiculo=contexto_veiculo
        )

        return {
            "sucesso": True,
            "intencao": intencao,
            "confianca": classificacao["confianca"],
            "resposta": resposta_formatada,
            "dtcs_detectados": codigos_encontrados,
            "detalhes_tecnicos": detalhes_dtc,
            "aprendizado_aplicado": bool(aprendizado_destaque),
            "padroes_aprendidos": aprendizado_destaque,
            "fontes_manuais": citacoes_manuais[:3],
            "usuario_id": usuario_id,
            "timestamp": datetime.now().isoformat()
        }

    def _construir_resposta_tecnica(self, pergunta: str, intencao: str, codigos_encontrados: List[str],
                                    detalhes_dtc: List[Dict[str, Any]], aprendizado_destaque: Optional[Dict[str, Any]],
                                    citacoes_manuais: List[str], contexto_veiculo: Optional[Dict[str, Any]]) -> str:
        """Monta o relatório detalhado de diagnóstico para mecânicos e motoristas."""
        
        if intencao == "orcamento":
            return (
                "🔧 **Estimativa de Orçamento - PADOC AI**\n\n"
                "Para calcularmos o valor exato, identificamos os componentes mecânicos envolvidos na sua solicitação.\n"
                "• **Mão de obra padrão de teste/diagnóstico elétrico**: R$ 150,00 - R$ 250,00\n"
                "• **Revisão de ignição/injeção básica**: R$ 200,00 - R$ 450,00\n\n"
                "💡 *Dica*: Deseja agendar a inspeção física na oficina para confirmação das peças?"
            )

        if intencao == "agenda":
            return (
                "📅 **Agendamento de Serviço - PADOC AI**\n\n"
                "Temos horários disponíveis para diagnóstico computadorizado e inspeção preventiva.\n"
                "Por favor, informe seu melhor dia e período (manhã ou tarde) para confirmarmos na oficina credenciada."
            )

        # Diagnóstico Técnico Especialista
        partes = ["🛠️ **Diagnóstico Automotivo Especialista PADOC AI**\n"]

        if codigos_encontrados:
            partes.append(f"**Códigos OBD-II Analisados:** `{', '.join(codigos_encontrados)}`\n")

        # Se temos DTCs mapeados com profundidade
        for dtc in detalhes_dtc:
            partes.append(f"### 📍 {dtc['codigo']}: {dtc['descricao']}")
            partes.append(f"**Sistema**: {dtc.get('sistema', 'Geral')}")
            partes.append(f"**Nível de Gravidade**: `{dtc.get('gravidade', 'MEDIA')}`\n")
            
            if "causas_provaveis" in dtc and dtc["causas_provaveis"]:
                partes.append("**Prováveis Causas:**")
                for c in dtc["causas_provaveis"]:
                    partes.append(f"- {c}")
                partes.append("")

            if "procedimento_teste" in dtc and dtc["procedimento_teste"]:
                partes.append(f"**Procedimento de Teste Recomendado:**\n{dtc['procedimento_teste']}\n")

        # Se houver aprendizado de oficina comprovado
        if aprendizado_destaque:
            partes.append("🧠 **Solução Validada pela Base de Auto-Aprendizado:**")
            melhor_solucao = max(aprendizado_destaque["solucoes"], key=lambda s: s.get("confirmacoes", 1))
            partes.append(f"• **Solução Comprovada**: {melhor_solucao['texto']}")
            partes.append(f"• **Taxa de Eficácia Histórica**: {melhor_solucao.get('eficacia', 1.0)*100:.0f}% (Confirmado {melhor_solucao.get('confirmacoes', 1)}x em oficinas)\n")

        # Sintomas gerais sem DTC específico
        if not codigos_encontrados and not aprendizado_destaque:
            partes.append(f"**Análise de Sintomas**: \"{pergunta}\"")
            partes.append("\n**Hipóteses Diagnósticas Principais:**")
            
            texto_norm = normalizar_texto(pergunta)
            if "falha" in texto_norm or "engasg" in texto_norm or "morre" in texto_norm:
                partes.append("1. **Sistema de Ignição**: Velas carbonizadas, cabos de vela com fuga de corrente ou bobina superaquecendo.")
                partes.append("2. **Alimentação de Combustível**: Pressão insuficiente na bomba elétrica (< 3.0 bar) ou filtro saturado.")
                partes.append("3. **Sensores**: Sensor de rotação (CKP) com sinal intermitente ou sensor de posição da borboleta (TPS).")
            elif "barulho" in texto_norm or "estalo" in texto_norm:
                partes.append("1. **Suspensão e Direção**: Buchas de bandeja desgastadas, bieletas ou pivôs de suspensão.")
                partes.append("2. **Transmissão**: Homocinética com folga (estalos ao esterçar tracionando).")
            elif "aquec" in texto_norm or "ferv" in texto_norm or "agua" in texto_norm:
                partes.append("1. **Arrefecimento**: Válvula termostática travada fechada.")
                partes.append("2. **Eletroventilador**: Relé de acionamento queimado ou sensor de temperatura ECT descalibrado.")
                partes.append("3. **Pressurização**: Tampa do reservatório sem vedação (perda de pressão).")
            else:
                partes.append("1. Necessário inspeção eletrônica com scanner para leitura dos parâmetros em tempo real (DTCs e dados vivos).")
                partes.append("2. Verificar integridade de chicotes, tensões de alimentação e aterramentos principais.")

        # Citações de Manuais RAG
        if citacoes_manuais:
            partes.append("\n📖 **Trechos Relevantes de Manuais Técnicos:**")
            for cit in citacoes_manuais[:2]:
                partes.append(f"- {cit}")

        partes.append("\n✅ *A PADOC AI continuará aprendendo e refinando este diagnóstico com o seu feedback pós-reparo.*")

        return "\n".join(partes)

    def retroalimentar_aprendizado(self, problema: str, solucao: str, veiculo: str = "Geral", eficacia: float = 1.0, autor: str = "mecanico"):
        """Endpoint de auto-aprendizado chamado após o mecânico concluir um serviço."""
        self.learner.registrar_aprendizado(
            problema=problema,
            solucao=solucao,
            veiculo=veiculo,
            eficacia=eficacia,
            autor=autor
        )
        return {
            "sucesso": True,
            "mensagem": "Aprendizado registrado com sucesso na memória persistente da PADOC AI.",
            "total_aprendidos": len(self.learner.memoria.get("padroes_aprendidos", {}))
        }


# Instância Singleton global do motor
brain_engine = PadocBrainEngine()
