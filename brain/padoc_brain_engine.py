"""
PADOC AI - Unified Brain Engine (Cérebro Central com Auto-Aprendizado)

Este módulo é o núcleo inteligente da PADOC AI. Ele unifica:
1. Classificação de intenções e urgência máxima
2. Sistema Especialista Automotivo (sensores, faixas elétricas, fusíveis, relés, DTCs)
3. RAG Técnico (manuais de montadoras, esquemas e procedimentos)
4. Telemetria Preditiva (saúde de componentes e probabilidade de falhas em 7/30/90 dias)
5. Auto-Aprendizado Contínuo (ContinuousLearner): armazena e retroalimenta novos
   diagnósticos validados por mecânicos e oficinas.
6. Firebase Realtime Database: armazenamento e pesquisa distribuída de padrões
   aprendidos, cache de respostas e histórico global de diagnósticos.
"""

import os
import json
import re
import hashlib
import unicodedata
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger("padoc_brain")

# ── Firebase Realtime Database (opcional — fallback local se indisponível) ──
try:
    import firebase_admin
    from firebase_admin import db as firebase_db
    _FIREBASE_SDK = True
except ImportError:
    firebase_db = None
    _FIREBASE_SDK = False


def _get_firebase_db():
    """Retorna o módulo db do Firebase Admin se inicializado, senão None."""
    if not _FIREBASE_SDK:
        return None
    try:
        # Tenta obter app já inicializado
        firebase_admin.get_app()
    except Exception:
        # Inicializa usando credenciais padrão do ambiente (ex.: GOOGLE_APPLICATION_CREDENTIALS)
        try:
            firebase_admin.initialize_app()
            logger.info("✅ Firebase Admin SDK inicializado com credenciais padrão.")
        except Exception as init_err:
            logger.warning(f"⚠️ Falha ao iniciar Firebase Admin SDK: {init_err}")
            return None
    return firebase_db

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

    Armazenamento em dois níveis:
    - Primário: Firebase Realtime Database (compartilhado entre instâncias)
    - Fallback: arquivo JSON local (quando Firebase indisponível)
    """

    # Nós no Firebase Realtime Database
    FB_PADROES_PATH = "cerebro/padroes_aprendidos"
    FB_MEMORIA_PATH = "cerebro/memoria"

    def __init__(self, storage_path: str = LEARNING_FILE):
        self.storage_path = storage_path
        self.memoria: Dict[str, Any] = self._carregar()

    # ── Persistência local (fallback) ──────────────────────────────────────

    def _carregar(self) -> Dict[str, Any]:
        """Carrega memória: tenta Firebase primeiro, fallback para arquivo local."""
        # Tenta carregar do Firebase
        dados_fb = self._carregar_firebase()
        if dados_fb:
            logger.info("🔥 Memória PADOC carregada do Firebase Realtime Database.")
            # Sincroniza arquivo local com o Firebase
            self._salvar_local(dados_fb)
            return dados_fb

        # Fallback: arquivo local
        if not os.path.exists(self.storage_path):
            dados_iniciais = {
                "versao": "2.0",
                "padroes_aprendidos": {},
                "total_diagnosticos_processados": 0,
                "feedback_positivo": 0,
                "historico_recente": []
            }
            self._salvar_local(dados_iniciais)
            return dados_iniciais
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar base de auto-aprendizado: {e}")
            return {"padroes_aprendidos": {}, "total_diagnosticos_processados": 0,
                    "feedback_positivo": 0, "historico_recente": []}

    def _salvar_local(self, dados: Optional[Dict[str, Any]] = None):
        """Persiste memória no arquivo JSON local."""
        if dados is None:
            dados = self.memoria
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar base local de auto-aprendizado: {e}")

    # Alias para compatibilidade com código legado
    def _salvar(self, dados: Optional[Dict[str, Any]] = None):
        self._salvar_local(dados)
        self._salvar_firebase(dados or self.memoria)

    # ── Firebase: leitura ──────────────────────────────────────────────────

    def _carregar_firebase(self) -> Optional[Dict[str, Any]]:
        """Busca memória completa do Firebase Realtime Database."""
        db = _get_firebase_db()
        if not db:
            return None
        try:
            ref = db.reference(self.FB_MEMORIA_PATH)
            dados = ref.get()
            if dados and isinstance(dados, dict):
                # Firebase não suporta listas nativas; converte historico_recente
                if "historico_recente" in dados and isinstance(dados["historico_recente"], dict):
                    dados["historico_recente"] = list(dados["historico_recente"].values())
                if "padroes_aprendidos" not in dados:
                    dados["padroes_aprendidos"] = {}
                # Busca padrões separados (nó próprio para melhor indexação)
                padroes_ref = db.reference(self.FB_PADROES_PATH)
                padroes = padroes_ref.get()
                if padroes and isinstance(padroes, dict):
                    dados["padroes_aprendidos"] = padroes
                return dados
        except Exception as e:
            logger.warning(f"⚠️ Falha ao carregar do Firebase: {e}")
        return None

    def _carregar_padroes_firebase(self) -> Dict[str, Any]:
        """Busca apenas os padrões aprendidos do Firebase (mais leve)."""
        db = _get_firebase_db()
        if not db:
            return {}
        try:
            ref = db.reference(self.FB_PADROES_PATH)
            padroes = ref.get()
            return padroes if isinstance(padroes, dict) else {}
        except Exception as e:
            logger.warning(f"⚠️ Falha ao buscar padrões do Firebase: {e}")
            return {}

    # ── Firebase: escrita ──────────────────────────────────────────────────

    def _salvar_firebase(self, dados: Dict[str, Any]):
        """Persiste memória e padrões no Firebase Realtime Database."""
        db = _get_firebase_db()
        if not db:
            return
        try:
            # Salva padrões no nó dedicado (para indexação e busca eficiente)
            padroes = dados.get("padroes_aprendidos", {})
            if padroes:
                db.reference(self.FB_PADROES_PATH).set(padroes)

            # Salva metadados de memória (sem padroes_aprendidos para evitar duplicata)
            meta = {k: v for k, v in dados.items() if k != "padroes_aprendidos"}
            # Firebase não suporta listas como chave raiz; converte historico_recente
            if "historico_recente" in meta and isinstance(meta["historico_recente"], list):
                meta["historico_recente"] = {
                    str(i): item for i, item in enumerate(meta["historico_recente"][:100])
                }
            db.reference(self.FB_MEMORIA_PATH).update(meta)
            logger.debug("🔥 Memória PADOC sincronizada com Firebase.")
        except Exception as e:
            logger.warning(f"⚠️ Falha ao salvar no Firebase: {e}")

    def _salvar_padrao_firebase(self, chave: str, entrada: Dict[str, Any]):
        """Atualiza um único padrão no Firebase (mais eficiente que re-salvar tudo)."""
        db = _get_firebase_db()
        if not db:
            return
        try:
            # Chave Firebase não pode ter caracteres especiais
            chave_safe = hashlib.sha1(chave.encode()).hexdigest()[:16]
            db.reference(f"{self.FB_PADROES_PATH}/{chave_safe}").set({
                **entrada,
                "_chave_original": chave
            })
            logger.debug(f"🔥 Padrão '{chave[:30]}' salvo no Firebase.")
        except Exception as e:
            logger.warning(f"⚠️ Falha ao salvar padrão no Firebase: {e}")

    # ── Lógica de aprendizado ───────────────────────────────────────────────

    def registrar_aprendizado(self, problema: str, solucao: str, veiculo: str = "Geral",
                              eficacia: float = 1.0, autor: str = "oficina"):
        """
        Registra um caso resolvido com sucesso para auto-retroalimentação.
        Persiste localmente E no Firebase Realtime Database.
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
        solucao_existente = next(
            (s for s in entrada["solucoes"]
             if normalizar_texto(s["texto"]) == normalizar_texto(solucao)), None
        )
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

        # Histórico recente (últimos 100)
        historico = self.memoria.setdefault("historico_recente", [])
        historico.insert(0, {
            "timestamp": datetime.now().isoformat(),
            "veiculo": veiculo,
            "problema": problema,
            "solucao": solucao,
            "eficacia": eficacia
        })
        self.memoria["historico_recente"] = historico[:100]

        # Persiste local e Firebase
        self._salvar_local()
        self._salvar_padrao_firebase(chave_problema, entrada)

        # Atualiza contadores no Firebase
        db = _get_firebase_db()
        if db:
            try:
                db.reference(self.FB_MEMORIA_PATH).update({
                    "total_diagnosticos_processados": self.memoria["total_diagnosticos_processados"],
                    "feedback_positivo": self.memoria["feedback_positivo"],
                    "versao": self.memoria.get("versao", "2.0")
                })
            except Exception:
                pass

        logger.info(
            f"✅ PADOC AI aprendeu: '{problema}' -> '{solucao}' "
            f"(Confiança: {entrada['score_confianca']:.2f}) [Firebase+Local]"
        )

    def consultar_aprendizado(self, texto_sintoma: str) -> List[Dict[str, Any]]:
        """
        Busca padrões aprendidos. Consulta Firebase (conhecimento global)
        e merge com padrões locais.
        """
        texto_norm = normalizar_texto(texto_sintoma)
        resultados = []

        # Merge: padrões locais + Firebase (Firebase tem precedência se mais recente)
        padroes_locais = self.memoria.get("padroes_aprendidos", {})
        padroes_fb = self._carregar_padroes_firebase()
        padroes = {**padroes_locais, **padroes_fb}  # Firebase sobrepõe local

        for chave, info in padroes.items():
            chave_busca = chave.replace("_", " ")
            if chave_busca in texto_norm or any(
                palavra in texto_norm for palavra in chave_busca.split() if len(palavra) > 3
            ):
                if isinstance(info, dict) and "solucoes" in info:
                    resultados.append(info)

        return sorted(resultados, key=lambda x: x.get("score_confianca", 0), reverse=True)


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

    # ── Cache de respostas no Firebase ────────────────────────────────────

    FB_CACHE_PATH = "cerebro/cache_respostas"
    FB_HISTORICO_PATH = "cerebro/historico_diagnosticos"

    def _hash_pergunta(self, pergunta: str) -> str:
        """Gera chave de cache baseada na pergunta normalizada."""
        return hashlib.sha1(normalizar_texto(pergunta).encode()).hexdigest()[:20]

    def _buscar_cache_firebase(self, pergunta: str) -> Optional[Dict[str, Any]]:
        """Busca resposta em cache no Firebase para evitar reprocessamento."""
        db = _get_firebase_db()
        if not db:
            return None
        try:
            chave = self._hash_pergunta(pergunta)
            ref = db.reference(f"{self.FB_CACHE_PATH}/{chave}")
            cached = ref.get()
            if cached and isinstance(cached, dict):
                logger.info(f"🔥 Cache hit Firebase para: '{pergunta[:50]}'")
                cached["_fonte"] = "cache_firebase"
                cached["_cache_hit"] = True
                return cached
        except Exception as e:
            logger.warning(f"⚠️ Falha ao buscar cache Firebase: {e}")
        return None

    def _salvar_cache_firebase(self, pergunta: str, resultado: Dict[str, Any]):
        """Salva resposta no cache Firebase para futuras consultas idênticas."""
        db = _get_firebase_db()
        if not db:
            return
        try:
            chave = self._hash_pergunta(pergunta)
            # Salva sem campos voláteis
            cache_entry = {
                k: v for k, v in resultado.items()
                if k not in ("timestamp", "usuario_id", "_cache_hit", "_fonte")
            }
            cache_entry["pergunta_original"] = pergunta[:200]
            cache_entry["cached_at"] = datetime.now().isoformat()
            cache_entry["cache_hits"] = (resultado.get("cache_hits", 0) or 0) + 1
            db.reference(f"{self.FB_CACHE_PATH}/{chave}").set(cache_entry)
            logger.debug(f"🔥 Resposta cacheada no Firebase: chave={chave}")
        except Exception as e:
            logger.warning(f"⚠️ Falha ao salvar cache Firebase: {e}")

    def _salvar_historico_firebase(self, usuario_id: str, pergunta: str, resultado: Dict[str, Any]):
        """Registra histórico de diagnósticos no Firebase para análise e auditoria."""
        db = _get_firebase_db()
        if not db:
            return
        try:
            ref = db.reference(self.FB_HISTORICO_PATH)
            ref.push({
                "usuario_id": usuario_id,
                "pergunta": pergunta[:300],
                "intencao": resultado.get("intencao", "desconhecida"),
                "dtcs_detectados": resultado.get("dtcs_detectados", []),
                "aprendizado_aplicado": resultado.get("aprendizado_aplicado", False),
                "cache_hit": resultado.get("_cache_hit", False),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.warning(f"⚠️ Falha ao salvar histórico Firebase: {e}")

    # ── Diagnóstico principal ──────────────────────────────────────────────

    def processar_diagnostico(self, pergunta: str, usuario_id: str = "anonimo", contexto_veiculo: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processamento completo do diagnóstico:
        0. Busca em cache Firebase (resposta idêntica já processada)
        1. Classificação de intenção e urgência
        2. Extração de códigos DTC (ex: P0300)
        3. Consulta ao motor de Auto-Aprendizado (local + Firebase)
        4. Consulta ao Sistema Especialista e RAG
        5. Formulação de resposta técnica estruturada
        6. Salva resultado no cache e histórico Firebase
        """
        # 0. Verifica cache Firebase para perguntas idênticas (exceto urgências)
        cached = self._buscar_cache_firebase(pergunta)
        if cached and cached.get("intencao") != "urgencia":
            cached["usuario_id"] = usuario_id
            cached["timestamp"] = datetime.now().isoformat()
            self._salvar_historico_firebase(usuario_id, pergunta, cached)
            return cached

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

        resultado = {
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

        # 6. Persiste no Firebase: cache (para reutilização) e histórico (para auditoria)
        self._salvar_cache_firebase(pergunta, resultado)
        self._salvar_historico_firebase(usuario_id, pergunta, resultado)

        return resultado

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
