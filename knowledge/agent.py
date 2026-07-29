"PADOC AI - Agente de Intenção (v2)
 
Este módulo determina a(s) intenção(ões) do usuário com base na mensagem,
com suporte a:
- normalização de acentos/pontuação
- pontuação por especificidade de palavra-chave (não é só "bateu ou não")
- múltiplas intenções na mesma mensagem, com respectivo grau de confiança
- intenção de urgência/segurança com prioridade máxima
- contexto de conversa simples, para interpretar respostas curtas ("sim"/"não")
  em função da última pergunta feita pelo bot
- extração básica de entidades (data/hora para agenda, termo de peça)
- log do que motivou a classificação (explicabilidade)
"""
 
import re
import unicodedata
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
 
logger = logging.getLogger("padoc_agent")
 
 
def normalizar(texto: str) -> str:
    """Minúsculas + remove acentos, para casar 'orçamento' com 'orcamento'."""
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))
 
 
@dataclass
class IntentMatch:
    intencao: str
    confianca: float
    palavras_encontradas: List[str] = field(default_factory=list)
 
 
@dataclass
class ResultadoIntencao:
    """Resultado completo da classificação — não só uma string."""
    principal: str
    confianca: float
    candidatos: List[IntentMatch]
    entidades: Dict[str, str] = field(default_factory=dict)
    requer_confirmacao: bool = False  # True quando há empate/ambiguidade real
 
 
class PadocAgent:
    """
    Agente de intenção com regras ponderadas + memória curta de conversa.
 
    Cada palavra-chave tem um peso: termos mais específicos/inequívocos
    ("quanto custa", "cheiro de gás") pesam mais que termos genéricos que
    podem aparecer em várias frases ("marca", "horário").
    """
 
    # peso maior = termo mais específico/decisivo
    REGRAS_INTENCAO: Dict[str, List[tuple]] = {
        "urgencia": [
            ("cheiro de gas", 5), ("cheiro de queimado", 5), ("fumaca", 4),
            ("pegando fogo", 6), ("freio nao para", 6), ("sem freio", 6),
            ("parou no meio da pista", 4), ("faisca", 4),
        ],
        "orcamento": [
            ("quanto custa", 4), ("orcamento", 4), ("preco para", 3),
            ("valor para", 3), ("quanto fica", 3), ("quanto sai", 3),
            ("qual o valor", 3),
        ],
        "agenda": [
            ("agendar", 4), ("marcar horario", 4), ("horario para", 3),
            ("posso levar", 3), ("tem vaga", 3), ("que dia", 2),
            ("amanha", 1), ("hoje a tarde", 2),
        ],
        "pecas": [
            ("qual peca", 4), ("fornecedor", 3), ("melhor marca", 3),
            ("onde comprar", 4), ("peca original", 3), ("peca paralela", 3),
        ],
        "saudacao": [
            ("bom dia", 3), ("boa tarde", 3), ("boa noite", 3),
            ("oi", 2), ("ola", 2), ("obrigado", 2), ("valeu", 2),
        ],
    }
 
    LIMIAR_CONFIANCA_MINIMO = 2      # abaixo disso, não conta como match
    LIMIAR_AMBIGUIDADE = 1.0         # diferença mínima entre 1º e 2º lugar
 
    # respostas curtas que só fazem sentido em função do contexto anterior
    RESPOSTAS_CONFIRMACAO_POSITIVA = {"sim", "pode", "isso", "confirmo", "ok", "beleza"}
    RESPOSTAS_CONFIRMACAO_NEGATIVA = {"nao", "não", "deixa", "cancela"}
 
    def __init__(self):
        # memória curta por sessão: {usuario_id: {"ultima_intencao": ..., "aguardando_confirmacao_de": ...}}
        self.contexto_por_usuario: Dict[str, dict] = {}
 
    # ------------------ API PRINCIPAL ------------------
 
    def executar(self, mensagem: str, usuario_id: str = "default") -> ResultadoIntencao:
        """
        Analisa a mensagem do usuário e retorna a intenção detectada,
        já considerando o contexto da conversa (se houver).
        """
        msg_norm = normalizar(mensagem)
        contexto = self.contexto_por_usuario.setdefault(usuario_id, {})
 
        # 1) Resposta curta a uma pergunta pendente do bot (ex: "sim" após "posso agendar?")
        resultado_contextual = self._resolver_por_contexto(msg_norm, contexto)
        if resultado_contextual:
            logger.debug("Intenção resolvida por contexto: %s", resultado_contextual)
            return resultado_contextual
 
        # 2) Classificação por regras ponderadas
        candidatos = self._pontuar_intencoes(msg_norm)
 
        # 3) Urgência sempre vence, mesmo com pontuação baixa — segurança primeiro
        urgencia = next((c for c in candidatos if c.intencao == "urgencia"), None)
        if urgencia and urgencia.confianca > 0:
            logger.info("Mensagem classificada como URGÊNCIA: %s", urgencia.palavras_encontradas)
            return ResultadoIntencao(
                principal="urgencia", confianca=urgencia.confianca, candidatos=candidatos
            )
 
        candidatos_validos = [c for c in candidatos if c.confianca >= self.LIMIAR_CONFIANCA_MINIMO]
 
        if not candidatos_validos:
            # Fallback não é mais "cego": mensagens muito curtas ou vazias
            # não deveriam acionar diagnóstico pesado sem necessidade.
            if len(msg_norm.split()) <= 2:
                intencao_final = "saudacao"
            else:
                intencao_final = "diagnostico"
            logger.debug("Nenhuma regra bateu com confiança suficiente. Fallback: %s", intencao_final)
            return ResultadoIntencao(principal=intencao_final, confianca=0.0, candidatos=candidatos)
 
        candidatos_validos.sort(key=lambda c: c.confianca, reverse=True)
        melhor = candidatos_validos[0]
        segundo = candidatos_validos[1] if len(candidatos_validos) > 1 else None
 
        ambiguo = bool(segundo and (melhor.confianca - segundo.confianca) < self.LIMIAR_AMBIGUIDADE)
 
        entidades = self._extrair_entidades(melhor.intencao, mensagem)
 
        # guarda contexto para a próxima mensagem (ex: se formos perguntar algo de volta)
        contexto["ultima_intencao"] = melhor.intencao
 
        return ResultadoIntencao(
            principal=melhor.intencao,
            confianca=melhor.confianca,
            candidatos=candidatos_validos,
            entidades=entidades,
            requer_confirmacao=ambiguo,
        )
 
    def registrar_pergunta_pendente(self, usuario_id: str, aguardando_confirmacao_de: str) -> None:
        """Chame isto quando o BOT fizer uma pergunta de sim/não ao usuário,
        para que a próxima mensagem curta seja interpretada corretamente.
        Ex: bot pergunta "posso agendar para amanhã 14h?" ->
            agent.registrar_pergunta_pendente(usuario_id, "agenda")
        """
        contexto = self.contexto_por_usuario.setdefault(usuario_id, {})
        contexto["aguardando_confirmacao_de"] = aguardando_confirmacao_de
 
    # ------------------ INTERNOS ------------------
 
    def _pontuar_intencoes(self, msg_norm: str) -> List[IntentMatch]:
        candidatos = []
        for intencao, palavras_pesos in self.REGRAS_INTENCAO.items():
            confianca = 0.0
            encontradas = []
            for palavra, peso in palavras_pesos:
                if palavra in msg_norm:
                    confianca += peso
                    encontradas.append(palavra)
            candidatos.append(IntentMatch(intencao, confianca, encontradas))
        return candidatos
 
    def _resolver_por_contexto(self, msg_norm: str, contexto: dict) -> Optional[ResultadoIntencao]:
        pendente = contexto.get("aguardando_confirmacao_de")
        if not pendente:
            return None
 
        palavras = set(msg_norm.split())
        if palavras & self.RESPOSTAS_CONFIRMACAO_POSITIVA:
            contexto.pop("aguardando_confirmacao_de", None)
            return ResultadoIntencao(principal=pendente, confianca=10.0, candidatos=[],
                                      entidades={"confirmacao": "sim"})
        if palavras & self.RESPOSTAS_CONFIRMACAO_NEGATIVA:
            contexto.pop("aguardando_confirmacao_de", None)
            return ResultadoIntencao(principal="cancelado", confianca=10.0, candidatos=[],
                                      entidades={"confirmacao": "nao"})
        # mensagem não é uma confirmação simples -> segue fluxo normal de classificação
        return None
 
    def _extrair_entidades(self, intencao: str, mensagem_original: str) -> Dict[str, str]:
        """Extração simples baseada em regex/palavras-chave. Para algo mais
        robusto, considere delegar essa etapa ao LLM local já carregado em
        PadocAI (prompt de extração estruturada), especialmente para datas
        por extenso ("semana que vem", "depois de amanhã")."""
        entidades = {}
 
        if intencao == "agenda":
            match_horario = re.search(r"(\d{1,2})[:h](\d{2})?", mensagem_original)
            if match_horario:
                entidades["horario"] = match_horario.group(0)
            for termo in ["amanhã", "hoje", "segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]:
                if termo in normalizar(mensagem_original):
                    entidades["dia"] = termo
                    break
 
        elif intencao == "pecas":
            # tenta capturar até 3 palavras após "peça de/do/da/para o/a" ou similar,
            # parando em vírgula/conectivos para não engolir a frase inteira
            match_peca = re.search(
                r"(?:pe[cç]a(?: d[eoa]| para [oa])?|de|do|da)\s+([a-zà-ú0-9]+(?:\s+[a-zà-ú0-9]+){0,3})",
                normalizar(mensagem_original), re.IGNORECASE,
            )

            if match_peca:
                entidades["peca_mencionada"] = match_peca.group(1).strip()
 
        return entidades
 
 
# ------------------ EXEMPLO DE ROTEAMENTO (integração com PadocAI) ------------------
#
# agent = PadocAgent()
# resultado = agent.executar(mensagem, usuario_id=usuario_id)
#
# if resultado.requer_confirmacao:
#     # não adivinha: pergunta de volta em vez de arriscar a intenção errada
#     resposta = f"Você quer falar sobre {resultado.candidatos[0].intencao} ou {resultado.candidatos[1].intencao}?"
# elif resultado.principal == "urgencia":
#     resposta = tratar_urgencia(mensagem)              # fluxo prioritário, sem fila
# elif resultado.principal == "orcamento":
#     resposta = padoc_ai.gerar_resumo_custo(...)
# elif resultado.principal == "agenda":
#     agent.registrar_pergunta_pendente(usuario_id, "agenda")
#     resposta = confirmar_agendamento(resultado.entidades)
# elif resultado.principal == "pecas":
#     resposta = consultar_pecas(resultado.entidades.get("peca_mencionada"))
# elif resultado.principal == "saudacao":
#     resposta = "Olá! Me conta o que está acontecendo com o veículo."
# else:  # diagnostico
#     resposta = padoc_ai.diagnosticar(usuario_id, mensagem)