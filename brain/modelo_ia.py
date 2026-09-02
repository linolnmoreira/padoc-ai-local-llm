"""Motor LLM local para diagnóstico automotivo PADOC AI

VERSÃO CORRIGIDA PARA API WEB (multi-usuário)

Mudanças em relação à versão original:
1. Removido acesso direto a microfone/alto-falante do servidor (ouvir/falar).
   Voz agora é responsabilidade do app Android (grava e envia áudio / usa TTS nativo).
2. Histórico de conversa agora é por usuário/sessão, não compartilhado globalmente.
3. Diagnóstico guiado não usa mais input() — recebe respostas como parâmetros.
4. Modelo LLM é carregado UMA VEZ (padrão singleton) e reutilizado em todas as requisições.
"""

import os
import json, dataclasses
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional


@dataclass
class Sensor:
    """Estrutura detalhada para um sensor automotivo."""
    id: str
    fabricante: str
    modelo: str
    motor: str
    ano_inicio: int
    ano_fim: int
    sistema: str
    nome: str
    sigla: str
    funcao: str
    unidade: str
    tensao_min: Optional[float]
    tensao_max: Optional[float]
    resistencia_min: Optional[float]
    resistencia_max: Optional[float]
    frequencia_min: Optional[float]
    frequencia_max: Optional[float]
    descricao: str
    sintomas: List[str]
    codigos_obd: List[str]


@dataclass
class Fusivel:
    numero: str
    amperagem: int
    circuito: str


@dataclass
class Rele:
    nome: str
    funcao: str


# ------------------ NOVAS ESTRUTURAS TÉCNICAS DETALHADAS ------------------

@dataclass
class SensorValor:
    """Valores de referência para um sensor específico."""
    nome: str
    sigla: str
    tensao_min: float
    tensao_max: float
    resistencia_min: float
    resistencia_max: float
    frequencia_min: float
    frequencia_max: float
    unidade: str

@dataclass
class Atuador:
    """Informações detalhadas sobre um atuador do veículo."""
    id: str
    fabricante: str
    modelo: str
    motor: str
    ano_inicio: int
    ano_fim: int
    sistema: str
    nome: str
    tipo: str
    alimentacao: str
    controle: str
    localizacao: str
    resistencia_min: Optional[float]
    resistencia_max: Optional[float]
    tensao_min: Optional[float]
    tensao_max: Optional[float]
    pwm_min: Optional[int]
    pwm_max: Optional[int]
    frequencia_min: Optional[int]
    frequencia_max: Optional[int]
    descricao: str
    sintomas: List[str]
    codigos_obd: List[str]

@dataclass
class Reaprendizado:
    """Procedimento de reaprendizado para um componente."""
    componente: str
    passos: List[str]

@dataclass
class ResetServico:
    """Procedimento para reset de avisos de serviço/manutenção."""
    servico: str
    passos: List[str]

@dataclass
class Procedimento:
    """Estrutura para procedimentos de reaprendizado, reset e codificação."""
    id: str
    fabricante: str
    modelo: str
    motor: str
    categoria: str
    nome: str
    scanner_obrigatorio: bool
    passos: List[str]
    tempo_estimado: int
    observacoes: str
@dataclass

@dataclass
class Torque:
    """Dados de torque para um componente específico."""
    componente: str
    torque_nm: float
    angulo: str

@dataclass
class Ferramenta:
    """Ferramenta especial necessária para um procedimento."""
    codigo: str
    descricao: str

@dataclass
class Sincronismo:
    """Informações de sincronismo do motor."""
    fabricante: str
    modelo: str
    motor: str
    ano: int
    tipo_distribuicao: str
    ordem_ignicao: str
    procedimento: str
    folga_admissao: str
    folga_escape: str
    correia: str
    corrente: str
    observacoes: str
    torques: List[Torque]
    ferramentas: List[Ferramenta]


@dataclass
class ECU:
    """Estrutura genérica para um Módulo de Controle Eletrônico."""
    id: str
    fabricante: str
    modelo: str
    sistema: str
    funcao: str
    localizacao: str
    diagnostico_comum: List[str] = field(default_factory=list)
    codigos_falha_comuns: List[str] = field(default_factory=list)

@dataclass
class BCM(ECU):
    """Body Control Module."""
    funcoes_controladas: List[str] = field(default_factory=list)

@dataclass
class BMS(ECU):
    """Battery Management System."""
    tipo_bateria: str
    capacidade_kwh: Optional[float]
    tensao_nominal: Optional[float]
    monitora_celulas: bool

@dataclass
class AirbagModule(ECU):
    """Módulo de Airbag (SRS)."""
    sensores_colisao: int
    airbags_instalados: int

@dataclass
class ElectricSteeringModule(ECU):
    """Módulo de Direção Elétrica."""
    tipo_assistencia: str # EPS, EHPS

@dataclass
class HVACModule(ECU):
    """Módulo de Climatização (Heating, Ventilation, and Air Conditioning)."""
    sensores_temperatura_interna: int
    atuadores_dutos: int
    funcoes: List[str] = field(default_factory=list)

@dataclass
class ADASModule(ECU):
    """Advanced Driver-Assistance Systems Module."""
    funcoes_adas: List[str] = field(default_factory=list)
    sensores_integrados: List[str] = field(default_factory=list) # Câmeras, radar, lidar

@dataclass
class InfotainmentModule(ECU):
    """Módulo de Multimídia/Infotainment."""
    funcoes_multimidia: List[str] = field(default_factory=list)
    conectividade: List[str] = field(default_factory=list)

@dataclass
class TelematicsModule(ECU):
    """Módulo de Telemática (GPS, comunicação remota)."""
    funcoes_telematica: List[str] = field(default_factory=list)
    conectividade: List[str] = field(default_factory=list)

@dataclass
class SensorReading:
    """Estrutura para uma leitura de sensor em tempo real."""
    nome: str
    valor: float
    unidade: str
    timestamp: datetime = field(default_factory=datetime.now)
    limite_min: Optional[float] = None
    limite_max: Optional[float] = None
    status: Optional[str] = None # "Normal", "Alerta", "Crítico"

@dataclass
class EspecificacoesVeiculo:
    """Estrutura unificada para armazenar especificações técnicas detalhadas de um veículo."""
    # Informações básicas
    fabricante: str
    modelo: str
    ano: int
    motor: str

    # Manutenção e Fluidos
    torque_componentes: Dict[str, int]
    oleo_motor: str
    capacidade_oleo: float
    intervalo_oleo_km: int
    intervalo_oleo_meses: int
    filtro_oleo_km: int
    filtro_ar_km: int
    filtro_combustivel_km: int
    filtro_cabine_km: int
    capacidade_arrefecimento: float
    tipo_aditivo: str
    capacidade_tanque: float

    # Elétrica e Componentes
    pneus: Dict[str, float]
    porta_obd: str
    fusiveis: List[Fusivel]
    reles: List[Rele]
    sensores: List[Sensor]
    diagrama: str
    esquema_fusiveis: str

    # Novas especificações técnicas detalhadas
    valores_sensores: List[SensorValor]
    atuadores: List[Atuador] # Usará a nova dataclass Atuador
    procedimentos_reaprendizado: List[Reaprendizado]
    procedimentos_reset: List[ResetServico]
    procedimentos: List[Procedimento]
    sincronismo: Optional[Sincronismo]

    # NOVOS CAMPOS PARA ECUs e Sensores Avançados
    ecus_motor: List[ECU] = field(default_factory=list) # ECU do motor (PCM/ECM)
    tcu_modules: List[ECU] = field(default_factory=list) # TCU/câmbio
    abs_esp_modules: List[ECU] = field(default_factory=list) # ABS/ESP
    bcm_modules: List[BCM] = field(default_factory=list)
    bms_modules: List[BMS] = field(default_factory=list)
    airbag_modules: List[AirbagModule] = field(default_factory=list)
    electric_steering_modules: List[ElectricSteeringModule] = field(default_factory=list)
    hvac_modules: List[HVACModule] = field(default_factory=list)
    adas_modules: List[ADASModule] = field(default_factory=list)
    infotainment_modules: List[InfotainmentModule] = field(default_factory=list)
    telematics_modules: List[TelematicsModule] = field(default_factory=list)
    ultimas_leituras_sensores: Dict[str, SensorReading] = field(default_factory=dict)

"""Módulo de Análise de Imagem - PADOC AI

Usa CLIP (zero-shot image classification) para identificar problemas visuais
comuns em fotos de motor/peças: vazamento de óleo, correia gasta, corrosão, etc.

Por que CLIP e não um YOLO treinado do zero:
- CLIP já vem pré-treinado com milhões de imagens + descrições em texto
- Funciona em modo "zero-shot": você só passa uma lista de descrições possíveis
  e ele diz qual bate melhor com a imagem, SEM precisar treinar nada
- YOLO fine-tuned dá resultados mais precisos, mas exige você mesmo coletar e
  rotular centenas/milhares de fotos de motores com defeito — comece com CLIP,
  migre para YOLO fine-tuned depois que tiver seu próprio banco de imagens

Instalação necessária:
"""


class AnalisadorImagemAutomotivo:
    """Identifica problemas visuais em fotos de motor/peças usando CLIP."""

    # Lista de problemas visuais que o sistema sabe reconhecer.
    # Adicione novos itens aqui conforme for testando em campo — cada string
    # funciona melhor quanto mais descritiva e específica for.
    DESCRICOES_PROBLEMAS = [
        "vazamento de óleo escorrendo no motor",
        "correia dentada ou correia poly-v desgastada e trincada",
        "corrosão e ferrugem em peça metálica do motor",
        "vazamento de líquido de arrefecimento (radiador)",
        "conector elétrico ou chicote queimado/derretido",
        "bateria com terminais oxidados (sulfatação)",
        "mangueira de borracha ressecada ou rachada",
        "filtro de ar sujo e obstruído",
        "vela de ignição com depósito de carvão (fuligem)",
        "motor limpo e sem sinais visíveis de problema",
    ]

    def __init__(self, modelo_clip="openai/clip-vit-base-patch32"):
        """
        Args:
            modelo_clip: nome do modelo CLIP no Hugging Face. O modelo base
                (patch32) é mais leve e rápido; existe também patch16, mais
                pesado e um pouco mais preciso, se sua hospedagem aguentar.
        """
        from transformers import CLIPProcessor, CLIPModel

        self.torch = __import__("torch")

        self.model = CLIPModel.from_pretrained(modelo_clip)
        self.processor = CLIPProcessor.from_pretrained(modelo_clip)
        self.model.eval()  # modo de inferência, não treino

    def analisar_imagem(self, caminho_imagem, top_k=3, limiar_confianca=0.15):
        """Analisa uma foto e retorna os problemas visuais mais prováveis.

        Args:
            caminho_imagem: caminho do arquivo de imagem (já salvo localmente
                após o upload do app Android — ver nota em padoc_ai.py sobre
                salvar uploads em arquivo temporário antes de chamar isso)
            top_k: quantos resultados mais prováveis retornar
            limiar_confianca: ignora resultados abaixo dessa confiança (0-1)

        Returns:
            Lista de dicts: [{"problema": str, "confianca": float}, ...]
            ordenada da maior para a menor confiança.
        """
        try:
            from PIL import Image

            imagem = Image.open(caminho_imagem).convert("RGB")
        except Exception as e:
            return {"erro": f"Não foi possível abrir a imagem: {e}"}

        inputs = self.processor(
            text=self.DESCRICOES_PROBLEMAS,
            images=imagem,
            return_tensors="pt",
            padding=True
        )

        with self.torch.no_grad():
            outputs = self.model(**inputs)
            # logits_per_image: similaridade da imagem com cada descrição de texto
            logits_por_imagem = outputs.logits_per_image
            probabilidades = logits_por_imagem.softmax(dim=1)[0]

        resultados = []
        for descricao, prob in zip(self.DESCRICOES_PROBLEMAS, probabilidades):
            resultados.append({
                "problema": descricao,
                "confianca": round(float(prob), 4)
            })

        resultados.sort(key=lambda x: x["confianca"], reverse=True)
        resultados_filtrados = [r for r in resultados if r["confianca"] >= limiar_confianca]

        return resultados_filtrados[:top_k] if resultados_filtrados else [
            {"problema": "Nenhum problema visual reconhecido com confiança suficiente", "confianca": 0.0}
        ]

    def gerar_resumo_para_prompt(self, caminho_imagem):
        """Gera um texto curto resumindo a análise, pronto para injetar no
        prompt do LLM (usado em diagnostico_multimodal no padoc_ai.py).
        """
        if not caminho_imagem:
            return "[Nenhuma imagem fornecida para análise visual.]"
            
        resultados = self.analisar_imagem(caminho_imagem)

        if isinstance(resultados, dict) and "erro" in resultados:
            return f"[Análise de imagem indisponível: {resultados['erro']}]"

        linhas = ["Análise visual da imagem enviada:"]
        for r in resultados:
            percentual = round(r["confianca"] * 100, 1)
            linhas.append(f"- {r['problema']} (confiança: {percentual}%)")

        return "\n".join(linhas)


# ------------------ SINGLETON (mesma lógica do padoc_ai.py) ------------------
# Carregar o CLIP também é custoso — reutilize a mesma instância entre requisições.
_analisador_instance = None


def get_analisador_instance():
    global _analisador_instance
    if _analisador_instance is None:
        _analisador_instance = AnalisadorImagemAutomotivo()
    return _analisador_instance


"""Módulo de Histórico do Veículo - PADOC AI

Mantém o histórico de manutenção de cada carro específico (identificado pela
placa), permitindo que a IA correlacione problemas atuais com reparos
anteriores daquele MESMO veículo — não só do modelo em geral.

Exemplo de valor: se o carro já trocou a bomba de combustível há 6 meses e
agora apresenta sintoma parecido, a IA pode sugerir "verificar se a bomba
trocada não tem defeito de fábrica" em vez de repetir o diagnóstico genérico.

Por simplicidade, este módulo usa um arquivo JSON como "banco de dados".
Para produção real com múltiplas oficinas e mais volume, troque por SQLite
ou Postgres — a interface (métodos) pode continuar a mesma.
"""

class HistoricoVeiculo:
    """Gerencia o histórico de manutenção de cada veículo, indexado por placa."""

    def __init__(self, caminho_arquivo=None):
        if caminho_arquivo is None:
            caminho_arquivo = os.environ.get(
                "PADOC_HISTORICO_VEICULOS_PATH",
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "historico_veiculos.json")
            )
        self.caminho_arquivo = caminho_arquivo
        self._dados = self._carregar()

    def _carregar(self):
        if os.path.exists(self.caminho_arquivo):
            with open(self.caminho_arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _salvar(self):
        with open(self.caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(self._dados, f, indent=2, ensure_ascii=False)

    def _normalizar_placa(self, placa):
        """Remove espaços/traços e deixa maiúsculo, para evitar duplicidade
        (ex: 'abc-1234' e 'ABC1234' devem ser tratados como a mesma placa)."""
        if not placa: return ""
        return placa.upper().replace("-", "").replace(" ", "").strip()

    def registrar_servico(self, placa, modelo, servico_realizado, codigo_obd=None,
                           pecas_trocadas=None, data=None):
        """Registra um novo serviço/reparo no histórico do veículo."""
        placa_norm = self._normalizar_placa(placa)
        if not placa_norm: return

        if placa_norm not in self._dados:
            self._dados[placa_norm] = {
                "modelo": modelo,
                "servicos": []
            }

        self._dados[placa_norm]["servicos"].append({
            "data": data or datetime.now().isoformat(),
            "servico": servico_realizado,
            "codigo_obd": codigo_obd,
            "pecas_trocadas": pecas_trocadas or []
        })

        self._salvar()

    def consultar_historico(self, placa):
        """Retorna o histórico completo de um veículo específico."""
        placa_norm = self._normalizar_placa(placa)
        return self._dados.get(placa_norm, {"modelo": None, "servicos": []})

    def buscar_servicos_relacionados(self, placa, codigo_obd=None, palavra_chave=None,
                                       dias_recentes=180):
        """Busca serviços anteriores relacionados ao problema atual."""
        historico = self.consultar_historico(placa)
        limite_data = datetime.now() - timedelta(days=dias_recentes)

        relacionados = []
        for servico in historico.get("servicos", []):
            try:
                data_servico = datetime.fromisoformat(servico["data"])
            except (ValueError, KeyError):
                continue

            if data_servico < limite_data:
                continue

            bate_codigo = codigo_obd and servico.get("codigo_obd") == codigo_obd
            bate_palavra = palavra_chave and palavra_chave.lower() in servico.get("servico", "").lower()

            if bate_codigo or bate_palavra or (not codigo_obd and not palavra_chave):
                relacionados.append(servico)

        relacionados.sort(key=lambda s: s["data"], reverse=True)
        return relacionados

    def gerar_resumo_para_prompt(self, placa, codigo_obd=None):
        """Gera um texto curto resumindo o histórico relevante, pronto para
        injetar no prompt do LLM."""
        if not placa:
            return "[Nenhuma placa de veículo fornecida para consulta de histórico.]"
            
        historico = self.consultar_historico(placa)

        if not historico.get("servicos"):
            return f"Nenhum histórico de serviço registrado para o veículo (placa {placa})."

        relacionados = self.buscar_servicos_relacionados(placa, codigo_obd=codigo_obd)

        linhas = [f"Histórico do veículo (placa {placa}, modelo {historico.get('modelo', 'N/A')}):"]

        if relacionados:
            linhas.append("⚠️ Serviços relacionados ao problema atual nos últimos 6 meses:")
            for s in relacionados:
                data_fmt = s.get("data", "Data N/A")[:10]
                linhas.append(f"  - {data_fmt}: {s.get('servico', 'Serviço N/A')} (código: {s.get('codigo_obd', 'N/A')})")
        else:
            linhas.append("Nenhum serviço relacionado encontrado nos últimos 6 meses.")

        total_servicos = len(historico.get("servicos", []))
        linhas.append(f"Total de {total_servicos} serviço(s) registrado(s) no histórico completo deste veículo.")

        return "\n".join(linhas)

"""Módulo de Estimativa de Custo e Tempo de Reparo - PADOC AI

Fornece uma estimativa de peça necessária, faixa de preço e tempo de mão de
obra para um diagnóstico. Os valores abaixo são uma BASE INICIAL de exemplo —
o real valor pra você é substituir/completar essa tabela com preços
praticados na sua região (fornecedores, tabelas de peças, sindicato dos
mecânicos, etc). Preços de peças automotivas variam MUITO por região e
marca da peça (original vs paralela), então trate os valores abaixo como
ponto de partida, não como verdade absoluta.
"""


class EstimadorCustoReparo:
    """Estima peça, faixa de preço e tempo de mão de obra para um reparo."""

    # Tabela de referência: chave é um identificador do tipo de reparo.
    # "preco_peca_min/max" em reais (R$), "horas_mao_obra" é tempo estimado
    # de serviço (não inclui espera por peça).
    TABELA_REFERENCIA = {
        "termoestato": {
            "peca": "Termoestato / válvula termostática",
            "preco_peca_min": 40,
            "preco_peca_max": 150,
            "horas_mao_obra": 1.5,
        },
        "bomba_combustivel": {
            "peca": "Bomba de combustível elétrica",
            "preco_peca_min": 250,
            "preco_peca_max": 700,
            "horas_mao_obra": 2.0,
        },
        "corpo_borboleta": {
            "peca": "Corpo de borboleta (TBI)",
            "preco_peca_min": 300,
            "preco_peca_max": 900,
            "horas_mao_obra": 1.0,
        },
        "junta_cabecote": {
            "peca": "Junta do cabeçote",
            "preco_peca_min": 80,
            "preco_peca_max": 300,
            "horas_mao_obra": 6.0,  # serviço grande, exige desmontagem do motor
        },
        "vela_ignicao": {
            "peca": "Jogo de velas de ignição (4 unidades)",
            "preco_peca_min": 60,
            "preco_peca_max": 250,
            "horas_mao_obra": 0.5,
        },
        "correia_dentada": {
            "peca": "Kit correia dentada + tensor",
            "preco_peca_min": 150,
            "preco_peca_max": 400,
            "horas_mao_obra": 3.0,
        },
        "rolamento_roda": {
            "peca": "Rolamento de roda",
            "preco_peca_min": 90,
            "preco_peca_max": 250,
            "horas_mao_obra": 2.0,
        },
        "sensor_map": {
            "peca": "Sensor MAP",
            "preco_peca_min": 100,
            "preco_peca_max": 300,
            "horas_mao_obra": 0.5,
        },
    }

    # Valor da hora de mão de obra — ajuste pra sua região/oficina.
    VALOR_HORA_MAO_OBRA = 80  # R$ por hora, valor de exemplo

    def __init__(self, tabela_customizada=None, valor_hora=None):
        """
        Args:
            tabela_customizada: dict para sobrescrever/adicionar itens à
                tabela de referência sem editar o código-fonte
            valor_hora: valor da hora de mão de obra da sua oficina/região
        """
        self.tabela = dict(self.TABELA_REFERENCIA)
        if tabela_customizada:
            self.tabela.update(tabela_customizada)

        self.valor_hora = valor_hora or self.VALOR_HORA_MAO_OBRA

    def estimar(self, chave_reparo, urgencia="normal"):
        """Gera a estimativa de custo e tempo para um tipo de reparo.

        Args:
            chave_reparo: chave da tabela de referência (ex: "termoestato").
                Idealmente, o LLM/diagnóstico já indica qual chave usar,
                mapeando a causa identificada para uma dessas chaves.
            urgencia: "normal" ou "urgente" — reparos urgentes podem ter
                acréscimo de custo (peça expressa, hora extra), configurável.

        Returns:
            Dict com a estimativa completa, ou dict de erro se a chave
            não estiver cadastrada.
        """
        if chave_reparo not in self.tabela:
            return {
                "erro": f"Reparo '{chave_reparo}' não cadastrado na tabela de referência.",
                "reparos_disponiveis": list(self.tabela.keys())
            }

        item = self.tabela[chave_reparo]
        custo_mao_obra = round(item["horas_mao_obra"] * self.valor_hora, 2)
        custo_total_min = item["preco_peca_min"] + custo_mao_obra
        custo_total_max = item["preco_peca_max"] + custo_mao_obra

        fator_urgencia = 1.25 if urgencia == "urgente" else 1.0
        custo_total_min = round(custo_total_min * fator_urgencia, 2)
        custo_total_max = round(custo_total_max * fator_urgencia, 2)

        return {
            "peca": item["peca"],
            "faixa_preco_peca": f"R$ {item['preco_peca_min']:.2f} - R$ {item['preco_peca_max']:.2f}",
            "tempo_mao_obra_horas": item["horas_mao_obra"],
            "custo_mao_obra": f"R$ {custo_mao_obra:.2f}",
            "faixa_custo_total": f"R$ {custo_total_min:.2f} - R$ {custo_total_max:.2f}",
            "urgencia": urgencia,
            "aviso": "Valores de referência — confirme preço atualizado com fornecedor local antes de repassar ao cliente."
        }

    def gerar_resumo_para_prompt(self, chave_reparo, urgencia="normal"):
        """Gera texto curto pronto para injetar no prompt do LLM, ou para
        exibir direto na interface do app."""
        estimativa = self.estimar(chave_reparo, urgencia)

        if not chave_reparo:
            return "[Nenhuma chave de reparo fornecida para estimativa de custo.]"

        if "erro" in estimativa:
            return f"[Estimativa de custo indisponível: {estimativa['erro']}]"

        linhas = [
            f"Estimativa de reparo — {estimativa['peca']}:",
            f"- Peça: {estimativa['faixa_preco_peca']}",
            f"- Mão de obra: {estimativa['tempo_mao_obra_horas']}h (~{estimativa['custo_mao_obra']})",
            f"- Total estimado: {estimativa['faixa_custo_total']}",
            f"- {estimativa['aviso']}"
        ]
        return "\n".join(linhas)


class BaseConhecimento:
    """
    NOVA CLASSE: Centraliza o carregamento e o acesso a toda a base de
    conhecimento a partir de arquivos JSON, separando dados da lógica.
    """
    def __init__(self):
        self.dados = self._carregar_todos_dados()

    def _carregar_todos_dados(self):
        """Carrega todos os arquivos JSON do diretório de conhecimento."""
        base_dados = {}
        knowledge_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "knowledge")
        
        if not os.path.isdir(knowledge_path):
            print(f"Aviso: Diretório de conhecimento não encontrado em {knowledge_path}")
            return base_dados

        for filename in os.listdir(knowledge_path):
            if filename.endswith(".json"):
                file_path = os.path.join(knowledge_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # Usa o nome do arquivo (sem extensão) como chave
                        chave = os.path.splitext(filename)[0]
                        base_dados[chave] = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Aviso: Falha ao carregar ou decodificar {filename}: {e}")
        return base_dados

    def get_dados_veiculo(self, codigo_veiculo):
        """Busca especificações de um veículo na base de conhecimento."""
        # Assumindo que os dados dos veículos estão em 'dados_tecnicos_veiculos.json'
        # e foram carregados sob a chave 'dados_tecnicos_veiculos'
        dados_modelos = self.dados.get("dados_tecnicos_veiculos", {}).get("modelos", {})
        return dados_modelos.get(codigo_veiculo)


class SistemaEspecialistaAutomotivo:
    def __init__(self):
        self.base_dados = {
            "modelos": {},
            "esquemas_eletricos": {},
            "sintomas_visuais": {},
            "historico_ordens_servico": [],
            "codigos_obd2": {} # NOVO: Base de códigos OBD-II
        }
        # A inicialização agora pode ser simplificada para usar a nova classe
        # ou carregar de arquivos específicos, como já faz com o histórico.
        self._inicializar_base_conhecimento()
        self._carregar_historico_servico()

    def _carregar_historico_servico(self):
        """Carrega o histórico de ordens de serviço do JSON.

        Usa variável de ambiente PADOC_KNOWLEDGE_PATH se definida (mais seguro
        para deploy em Docker/nuvem, onde a estrutura de pastas pode mudar).
        """
        env_path = os.environ.get("PADOC_KNOWLEDGE_PATH")
        if env_path:
            json_path = os.path.join(env_path, "historico_ordens_servico.json")
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.normpath(
                os.path.join(base_path, "..", "knowledge", "historico_ordens_servico.json")
            )

        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                # O arquivo JSON contém uma chave "ordens_servico" que é a lista que queremos.
                if isinstance(dados, dict) and "ordens_servico" in dados:
                    self.base_dados["historico_ordens_servico"] = dados["ordens_servico"]

    def _inicializar_base_conhecimento(self):
        """
        Inicializa a base de conhecimento interna com dados de exemplo e estruturas essenciais.
        """
        # 1. MÓDULO DE MODELOS + LIVE DATA (PARÂMETROS EM TEMPO REAL)
        # NOVO: Usando a estrutura EspecificacoesVeiculo para dados técnicos detalhados.
        self.base_dados["modelos"]["ONIX_2023_10T"] = EspecificacoesVeiculo(
            fabricante="Chevrolet",
            modelo="Onix",
            ano=2023,
            motor="1.0 Turbo",
            torque_componentes={
                "Parafuso Cabeçote": 30,
                "Mancal Virabrequim": 65,
                "Biela": 35,
                "Velas": 25,
                "Rodas": 110,
                "Cárter": 12,
                "Coletor Escape": 25,
                "Coletor Admissão": 20
            },
            oleo_motor="Dexos1 Gen3 0W20",
            capacidade_oleo=3.5,
            intervalo_oleo_km=10000,
            intervalo_oleo_meses=12,
            filtro_oleo_km=10000,
            filtro_ar_km=10000,
            filtro_combustivel_km=30000,
            filtro_cabine_km=10000,
            capacidade_arrefecimento=5.8,
            tipo_aditivo="Dex-Cool",
            capacidade_tanque=44,
            # Inicializando novos campos com valores vazios/padrão
            pneus={},
            porta_obd="",
            fusiveis=[],
            reles=[],
            sensores=[],
            diagrama="",
            esquema_fusiveis="",
            valores_sensores=[],
            atuadores=[],
            procedimentos_reaprendizado=[],
            procedimentos_reset=[],
            procedimentos=[], # Corrigido abaixo
            sincronismo=None,
        )
        # Adicionando os novos campos da estrutura unificada
        self.base_dados["modelos"]["ONIX_2023_10T"].pneus = {
            "Dianteiro": 32,
            "Traseiro": 30,
            "Estepe": 60
        }
        self.base_dados["modelos"]["ONIX_2023_10T"].porta_obd = "Abaixo do painel, lado esquerdo do volante."
        self.base_dados["modelos"]["ONIX_2023_10T"].fusiveis = [
            Fusivel("F01", 15, "Injeção Eletrônica"),
            Fusivel("F02", 10, "ABS"),
            Fusivel("F03", 20, "Faróis"),
            Fusivel("F04", 30, "Ventoinha"),
            Fusivel("F05", 15, "ECU"),
            Fusivel("F06", 10, "Airbag")
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].reles = [
            Rele("R1", "Bomba de combustível"),
            Rele("R2", "Ventoinha"),
            Rele("R3", "Ar condicionado"),
            Rele("R4", "Faróis"),
            Rele("R5", "Partida")
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].sensores = [
            Sensor(id="S01", fabricante="N/A", modelo="N/A", motor="N/A", ano_inicio=0, ano_fim=0, sistema="Injeção", nome="Sensor MAF", sigla="MAF", funcao="Fluxo de ar", unidade="", tensao_min=None, tensao_max=None, resistencia_min=None, resistencia_max=None, frequencia_min=None, frequencia_max=None, descricao="", sintomas=[], codigos_obd=[]),
            Sensor(id="S02", fabricante="N/A", modelo="N/A", motor="N/A", ano_inicio=0, ano_fim=0, sistema="Injeção", nome="Sensor MAP", sigla="MAP", funcao="Pressão coletor", unidade="", tensao_min=None, tensao_max=None, resistencia_min=None, resistencia_max=None, frequencia_min=None, frequencia_max=None, descricao="", sintomas=[], codigos_obd=[]),
            Sensor(id="S03", fabricante="N/A", modelo="N/A", motor="N/A", ano_inicio=0, ano_fim=0, sistema="Injeção", nome="Sensor TPS", sigla="TPS", funcao="Posição borboleta", unidade="", tensao_min=None, tensao_max=None, resistencia_min=None, resistencia_max=None, frequencia_min=None, frequencia_max=None, descricao="", sintomas=[], codigos_obd=[]),
            Sensor(id="S04", fabricante="N/A", modelo="N/A", motor="N/A", ano_inicio=0, ano_fim=0, sistema="Ignição", nome="Sensor CKP", sigla="CKP", funcao="Virabrequim", unidade="", tensao_min=None, tensao_max=None, resistencia_min=None, resistencia_max=None, frequencia_min=None, frequencia_max=None, descricao="", sintomas=[], codigos_obd=[]),
            Sensor(id="S05", fabricante="N/A", modelo="N/A", motor="N/A", ano_inicio=0, ano_fim=0, sistema="Ignição", nome="Sensor CMP", sigla="CMP", funcao="Comando", unidade="", tensao_min=None, tensao_max=None, resistencia_min=None, resistencia_max=None, frequencia_min=None, frequencia_max=None, descricao="", sintomas=[], codigos_obd=[]),
            Sensor(id="S06", fabricante="N/A", modelo="N/A", motor="N/A", ano_inicio=0, ano_fim=0, sistema="Arrefecimento", nome="Sensor ECT", sigla="ECT", funcao="Temperatura motor", unidade="", tensao_min=None, tensao_max=None, resistencia_min=None, resistencia_max=None, frequencia_min=None, frequencia_max=None, descricao="", sintomas=[], codigos_obd=[]),
            Sensor(id="S07", fabricante="N/A", modelo="N/A", motor="N/A", ano_inicio=0, ano_fim=0, sistema="Injeção", nome="Sensor IAT", sigla="IAT", funcao="Temperatura admissão", unidade="", tensao_min=None, tensao_max=None, resistencia_min=None, resistencia_max=None, frequencia_min=None, frequencia_max=None, descricao="", sintomas=[], codigos_obd=[]),
            Sensor(id="S08", fabricante="N/A", modelo="N/A", motor="N/A", ano_inicio=0, ano_fim=0, sistema="Emissões", nome="Sonda Lambda", sigla="O2", funcao="Mistura ar combustível", unidade="", tensao_min=None, tensao_max=None, resistencia_min=None, resistencia_max=None, frequencia_min=None, frequencia_max=None, descricao="", sintomas=[], codigos_obd=[]),
            Sensor(id="S09", fabricante="N/A", modelo="N/A", motor="N/A", ano_inicio=0, ano_fim=0, sistema="Ignição", nome="Sensor de Detonação", sigla="KS", funcao="Detonação", unidade="", tensao_min=None, tensao_max=None, resistencia_min=None, resistencia_max=None, frequencia_min=None, frequencia_max=None, descricao="", sintomas=[], codigos_obd=[]),
            Sensor(id="GM_MAP_001", fabricante="Chevrolet", modelo="Onix", motor="1.0 Turbo", ano_inicio=2020, ano_fim=2026, sistema="Injeção", nome="Sensor MAP", sigla="MAP", unidade="Volts", tensao_min=0.5, tensao_max=4.8, resistencia_min=None, resistencia_max=None, frequencia_min=None, frequencia_max=None, descricao="Mede pressão absoluta do coletor.", sintomas=["Motor fraco", "Consumo elevado"], codigos_obd=["P0106", "P0107", "P0108"])
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].diagrama = """
Bateria -> Fusível Principal -> Chave Ignição -> ECU
ECU -> Sensores (MAP, TPS, MAF)
ECU -> Atuadores (Injetores, Bobinas)
"""
        self.base_dados["modelos"]["ONIX_2023_10T"].esquema_fusiveis = """
F01 ECU | F02 ABS | F03 Farol
F04 Ventoinha | F05 Injeção | F06 Airbag
"""
        # Adicionando os dados técnicos mais detalhados
        self.base_dados["modelos"]["ONIX_2023_10T"].valores_sensores = [
            SensorValor("Sensor MAP", "MAP", 0.5, 4.8, 0, 0, 0, 0, "Volts"),
            SensorValor("Sensor TPS", "TPS", 0.4, 4.5, 0, 0, 0, 0, "Volts"),
            SensorValor("Sensor CKP", "CKP", 0.5, 50, 500, 1500, 200, 3000, "Hz"),
            SensorValor("Sonda Lambda", "O2", 0.1, 0.9, 0, 0, 1, 5, "Volts")
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].atuadores = [
            Atuador(id='ACT001', fabricante='Chevrolet', modelo='Onix', motor='1.0 Turbo', ano_inicio=2020, ano_fim=2024, sistema='Combustível', nome='Bomba elétrica de combustível', tipo='Relé', alimentacao='12V', controle='ECU', localizacao='Dentro do tanque de combustível', resistencia_min=None, resistencia_max=None, tensao_min=11.5, tensao_max=14.5, pwm_min=None, pwm_max=None, frequencia_min=None, frequencia_max=None, descricao='Pressuriza a linha de combustível para os injetores.', sintomas=['Motor não liga', 'Perda de potência', 'Falhas em aceleração'], codigos_obd=['P0230', 'P0231']),
            Atuador(id='ACT003', fabricante='Chevrolet', modelo='Onix', motor='1.0 Turbo', ano_inicio=2020, ano_fim=2024, sistema='Injeção', nome='Injetor Cilindro 1', tipo='PWM', alimentacao='12V', controle='ECU', localizacao='Coletor de admissão, cilindro 1', resistencia_min=11.0, resistencia_max=16.0, tensao_min=None, tensao_max=None, pwm_min=None, pwm_max=None, frequencia_min=None, frequencia_max=None, descricao='Pulveriza combustível no cilindro 1.', sintomas=['Falha de ignição (misfire)', 'Marcha lenta irregular', 'Perda de potência'], codigos_obd=['P0201', 'P0301']),
            Atuador(id='ACT020', fabricante='Chevrolet', modelo='Onix', motor='1.0 Turbo', ano_inicio=2020, ano_fim=2024, sistema='Ignição', nome='Bobina Cilindro 1', tipo='Digital', alimentacao='12V', controle='ECU', localizacao='Sobre a vela do cilindro 1', resistencia_min=0.4, resistencia_max=0.8, tensao_min=None, tensao_max=None, pwm_min=None, pwm_max=None, frequencia_min=None, frequencia_max=None, descricao='Gera alta tensão para a vela de ignição do cilindro 1.', sintomas=['Falha de ignição (misfire)', 'Motor tremendo', 'Perda de potência'], codigos_obd=['P0351', 'P0301']),
            Atuador(id='ACT040', fabricante='Chevrolet', modelo='Onix', motor='1.0 Turbo', ano_inicio=2020, ano_fim=2024, sistema='Admissão', nome='Corpo de borboleta eletrônico', tipo='Motor DC', alimentacao='5V/12V', controle='ECU', localizacao='Entre o filtro de ar e o coletor de admissão', resistencia_min=None, resistencia_max=None, tensao_min=None, tensao_max=None, pwm_min=None, pwm_max=None, frequencia_min=None, frequencia_max=None, descricao='Controla a quantidade de ar que entra no motor.', sintomas=['Aceleração irregular', 'Marcha lenta oscilante', 'Luz da injeção (EPC) acesa'], codigos_obd=['P2135', 'P2101']),
            Atuador(id='ACT101', fabricante='Chevrolet', modelo='Onix', motor='1.0 Turbo', ano_inicio=2020, ano_fim=2024, sistema='Arrefecimento', nome='Eletroventilador velocidade alta', tipo='Relé', alimentacao='12V', controle='ECU', localizacao='Atrás do radiador', resistencia_min=None, resistencia_max=None, tensao_min=11.5, tensao_max=14.5, pwm_min=None, pwm_max=None, frequencia_min=None, frequencia_max=None, descricao='Força a passagem de ar pelo radiador para arrefecer o motor.', sintomas=['Superaquecimento em trânsito', 'Ar condicionado desarma'], codigos_obd=['P0481']),
            Atuador(id='ACT121', fabricante='Chevrolet', modelo='Onix', motor='1.0 Turbo', ano_inicio=2020, ano_fim=2024, sistema='EVAP', nome='Válvula Canister', tipo='PWM', alimentacao='12V', controle='ECU', localizacao='Próximo ao coletor de admissão', resistencia_min=20.0, resistencia_max=30.0, tensao_min=None, tensao_max=None, pwm_min=None, pwm_max=None, frequencia_min=None, frequencia_max=None, descricao='Controla o fluxo de vapores de combustível do canister para o motor.', sintomas=['Cheiro de combustível', 'Marcha lenta irregular após abastecer', 'Luz da injeção acesa'], codigos_obd=['P0443', 'P0441'])
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].procedimentos_reaprendizado = [
            Reaprendizado(
                "Corpo de Borboleta",
                [
                    "Desligar ignição",
                    "Ligar ignição por 30 segundos",
                    "Desligar por 30 segundos",
                    "Ligar motor",
                    "Deixar marcha lenta 5 minutos"
                ]
            ),
            Reaprendizado(
                "Marcha Lenta",
                [
                    "Apagar códigos",
                    "Desligar bateria",
                    "Ligar motor",
                    "Esperar ventoinha acionar"
                ]
            )]
        self.base_dados["modelos"]["ONIX_2023_10T"].procedimentos = [
            Procedimento(id="CHEV_001", fabricante="Chevrolet", modelo="Onix", motor="1.0 Turbo", categoria="Reaprendizado", nome="Corpo de Borboleta", scanner_obrigatorio=False, passos=["Ligar ignição", "Aguardar 30 segundos", "Desligar ignição", "Aguardar 30 segundos", "Ligar motor", "Esperar estabilizar"], tempo_estimado=5, observacoes="Não acelerar durante o procedimento."),
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].procedimentos_reset = [
            ResetServico("Troca de Óleo", ["Ligar ignição", "Acessar menu", "Selecionar Manutenção", "Reset", "Confirmar"]),
            ResetServico("Inspeção", ["Segurar botão Trip", "Ligar ignição", "Aguardar", "Reset confirmado"])
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].sincronismo = Sincronismo(
            fabricante="Chevrolet",
            modelo="Onix",
            motor="1.0 Turbo",
            ano=2023,
            tipo_distribuicao="Correia",
            ordem_ignicao="1-3-4-2",
            procedimento="Alinhar marcas de referência no PMS do cilindro 1.",
            folga_admissao="0.20 mm",
            folga_escape="0.30 mm",
            correia="Marcas alinhadas PMS",
            corrente="Elo dourado alinhado",
            observacoes="Virabrequim no PMS cilindro 1",
            torques=[
                Torque(componente="Polia Virabrequim", torque_nm=120, angulo="+45°")
            ],
            ferramentas=[]
        )
        # NOVOS CAMPOS: ECUs e Sensores Avançados
        self.base_dados["modelos"]["ONIX_2023_10T"].ecus_motor = [
            ECU(id="ECM001", fabricante="GM", modelo="E80", sistema="Motor", funcao="Controle do motor", localizacao="Compartimento do motor", diagnostico_comum=["Falha de ignição", "Problemas de injeção"], codigos_falha_comuns=["P0300", "P0171"])
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].tcu_modules = [
            ECU(id="TCM001", fabricante="GM", modelo="6T30", sistema="Transmissão", funcao="Controle da transmissão automática", localizacao="Próximo à transmissão", diagnostico_comum=["Trocas bruscas", "Patinação"], codigos_falha_comuns=["P0700", "P0740"])
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].abs_esp_modules = [
            ECU(id="ABS001", fabricante="Bosch", modelo="9.0", sistema="Freios", funcao="Controle ABS e ESP", localizacao="Compartimento do motor", diagnostico_comum=["Luz ABS acesa", "Pedal duro"], codigos_falha_comuns=["C0035", "C0040"])
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].bcm_modules = [
            BCM(id="BCM001", fabricante="GM", modelo="B80", sistema="Carroceria", funcao="Controle de funções da carroceria", localizacao="Atrás do painel", funcoes_controladas=["Vidros elétricos", "Travas", "Iluminação interna"])
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].bms_modules = [
            BMS(id="BMS001", fabricante="GM", modelo="Gen2", sistema="Bateria", funcao="Gerenciamento de bateria", localizacao="Próximo à bateria", tipo_bateria="AGM", capacidade_kwh=None, tensao_nominal=12.0, monitora_celulas=False)
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].airbag_modules = [
            AirbagModule(id="SRS001", fabricante="Autoliv", modelo="ACU", sistema="Segurança", funcao="Controle de airbags", localizacao="Console central", sensores_colisao=4, airbags_instalados=6, diagnostico_comum=["Luz airbag acesa"], codigos_falha_comuns=["B0001"])
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].electric_steering_modules = [
            ElectricSteeringModule(id="EPS001", fabricante="ZF", modelo="EPS", sistema="Direção", funcao="Assistência elétrica da direção", localizacao="Coluna de direção", tipo_assistencia="EPS")
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].hvac_modules = [
            HVACModule(id="HVAC001", fabricante="Denso", modelo="Auto", sistema="Climatização", funcao="Controle de temperatura e ventilação", localizacao="Painel", sensores_temperatura_interna=2, atuadores_dutos=5, funcoes=["Ar condicionado", "Aquecimento", "Desembaçamento"])
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].adas_modules = [
            ADASModule(id="ADAS001", fabricante="Bosch", modelo="ADAS_Gen1", sistema="ADAS", funcao="Assistência ao motorista", localizacao="Atrás do retrovisor", funcoes_adas=["Alerta de colisão", "Assistente de faixa"], sensores_integrados=["Câmera frontal", "Radar frontal"])
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].infotainment_modules = [
            InfotainmentModule(id="INFOT001", fabricante="LG", modelo="MyLink", sistema="Multimídia", funcao="Entretenimento e navegação", localizacao="Painel", funcoes_multimidia=["Rádio", "Bluetooth", "GPS"], conectividade=["USB", "Bluetooth", "Apple CarPlay", "Android Auto"])
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].telematics_modules = [
            TelematicsModule(id="TEL001", fabricante="OnStar", modelo="Gen3", sistema="Telemática", funcao="Serviços conectados", localizacao="Teto", funcoes_telematica=["Localização", "Chamada de emergência"], conectividade=["4G", "GPS"])
        ]
        self.base_dados["modelos"]["ONIX_2023_10T"].ultimas_leituras_sensores = {
            "temperatura_cabine": SensorReading(nome="Temperatura Cabine", valor=22.5, unidade="°C", limite_min=18.0, limite_max=28.0),
            "tensao_bateria_aux": SensorReading(nome="Tensão Bateria Auxiliar", valor=12.8, unidade="V", limite_min=12.0, limite_max=14.5),
            "corrente_bateria_aux": SensorReading(nome="Corrente Bateria Auxiliar", valor=5.2, unidade="A", limite_min=0.5, limite_max=10.0),
            "distancia_ultrassom_frente": SensorReading(nome="Distância Ultrassom Frente", valor=1.5, unidade="m", limite_min=0.1, limite_max=3.0),
            "aceleracao_x": SensorReading(nome="Aceleração Eixo X", valor=0.1, unidade="G", limite_min=-1.0, limite_max=1.0),
            "radar_distancia_min": SensorReading(nome="Radar Distância Mínima", valor=10.0, unidade="m", limite_min=0.5, limite_max=100.0),
            "camera_deteccao_faixa": SensorReading(nome="Câmera Detecção Faixa", valor=1.0, unidade="bool", status="Normal"), # 1.0 for OK, 0.0 for issue
        )

        # Estrutura antiga mantida para exemplos de defeitos comuns.
        # O ideal seria unificar tudo sob a nova estrutura.
        self.base_dados["modelos"]["Gol 1.6 G6"] = {
            "marca": "Volkswagen",
            "motores": ["EA111", "MSI"],
            "defeitos_comuns": {
                "luz_epc_acesa": {
                    "causa": "Desgaste nas trilhas do Corpo de Borboleta (TBI) ou chicote oxidado.",
                    "codigos_obd2": ["P0121", "P0221"],
                    "valores_referencia_live": {
                        "posicao_borboleta_marcha_lenta": "3% a 5%",
                        "tensao_sinal_pino": "Estável próximo a 5V"
                    },
                    "teste_recomendado": "Medir resistência nos pinos do TBI movendo a borboleta manualmente buscando saltos bruscos."
                }
            }
        }

        # 2. MÓDULO DE ESQUEMAS ELÉTRICOS E PINOUTS (Exemplo)
        self.base_dados["esquemas_eletricos"]["ECU Magneti Marelli 4GV"] = {
            "aplicacao": "Gol/Fox 1.6 EA111",
            "pinout": {
                "pino_15": "Alimentação pós-chave (+15)",
                "pino_30": "Alimentação direta da bateria (+30)",
                "pino_32": "Sinal de referência 5V para Sensor de Fase (CMP)",
                "pino_64": "Sinal de controle do relé da bomba de combustível"
            }
        }

        # 3. MÓDULO DE SINTOMAS VISUAIS E AUDITIVOS (Exemplo)
        self.base_dados["sintomas_visuais"] = {
            "fumaça_azulada": "Óleo lubrificante sendo queimado na câmara de combustão (Prováveis anéis de pistão gastos ou retentores de válvula danificados).",
            "fumaça_branca_densa": "Líquido de arrefecimento (água) entrando nos cilindros (Provável junta do cabeçote queimada).",
            "oleo_cafe_com_leite": "Mistura crítica de água no óleo. Verificar trocador de calor do câmbio/óleo ou junta de cabeçote imediatamente."
        }

        # NOVO: Base de Códigos OBD-II
        self.base_dados["codigos_obd2"]["P0171"] = {
            "codigo": "P0171",
            "titulo": "Mistura pobre Banco 1",
            "gravidade": "Média",
            "descricao": "O motor está recebendo excesso de ar ou pouca gasolina no banco 1 de cilindros.",
            "causas": ["Entrada falsa de ar (mangueiras de vácuo, coletor)", "Bomba de combustível fraca", "Filtro de combustível entupido", "Bicos injetores sujos", "Sensor MAF defeituoso"],
            "sintomas": ["Consumo elevado", "Motor fraco ou hesitante", "Marcha lenta irregular", "Luz de injeção acesa"],
            "teste": ["Verificar pressão da linha de combustível com manômetro", "Testar o sensor MAF com multímetro ou scanner", "Realizar teste de fumaça para encontrar entradas de ar"],
            "reparo": ["Trocar filtro de combustível", "Limpar sensor MAF com produto específico", "Substituir bomba de combustível se a pressão estiver baixa", "Limpar bicos injetores"]
        }
        self.base_dados["codigos_obd2"]["P0300"] = {
            "codigo": "P0300",
            "titulo": "Falha de ignição em cilindros múltiplos/aleatórios",
            "gravidade": "Alta",
            "descricao": "A ECU detectou falhas de combustão em mais de um cilindro de forma não específica.",
            "causas": ["Velas de ignição gastas", "Bobinas de ignição defeituosas", "Cabos de vela danificados", "Combustível de baixa qualidade", "Baixa compressão do motor"],
            "sintomas": ["Motor tremendo (principalmente em marcha lenta)", "Perda significativa de potência", "Luz de injeção piscando (indica falha grave)"],
            "teste": ["Verificar o estado das velas", "Testar a resistência e o sinal das bobinas", "Medir a compressão dos cilindros"],
            "reparo": ["Substituir o jogo de velas", "Trocar bobinas ou cabos defeituosos", "Verificar o sistema de combustível"]
        }
        self.base_dados["codigos_obd2"]["P0420"] = {
            "codigo": "P0420",
            "titulo": "Eficiência do catalisador abaixo do limite (Banco 1)",
            "gravidade": "Baixa",
            "descricao": "O catalisador não está mais convertendo os gases nocivos com a eficiência esperada.",
            "causas": ["Catalisador envelhecido ou danificado", "Falhas de ignição (P0300) que danificaram o catalisador", "Sensor de oxigênio (sonda lambda) pós-catalisador defeituoso", "Vazamento no sistema de escape"],
            "sintomas": ["Luz de injeção acesa", "Pode não haver sintoma de dirigibilidade", "Cheiro de enxofre no escapamento"],
            "teste": ["Analisar o gráfico da sonda lambda 2 no scanner (deve ser uma linha estável, não oscilante como a sonda 1)", "Medir a temperatura de entrada e saída do catalisador"],
            "reparo": ["Substituir o catalisador (peça cara, confirmar diagnóstico antes)", "Trocar a sonda lambda 2 se estiver defeituosa", "Corrigir qualquer falha de motor antes de trocar o catalisador"]
        }
        self.base_dados["codigos_obd2"]["C0035"] = {
            "codigo": "C0035",
            "titulo": "Falha no sensor de velocidade da roda dianteira esquerda",
            "gravidade": "Alta",
            "descricao": "O módulo do ABS não está recebendo um sinal válido do sensor da roda dianteira esquerda.",
            "causas": ["Sensor ABS defeituoso", "Cabo do sensor rompido ou com mau contato", "Anel fônico (reluctor) do cubo da roda quebrado ou sujo", "Módulo ABS com falha"],
            "sintomas": ["Luz do ABS acesa", "Luz do controle de tração (ESP/ESC) acesa", "Sistema ABS e controle de estabilidade desativados"],
            "teste": ["Verificar o sinal do sensor com um osciloscópio ou scanner em tempo real", "Medir a resistência do sensor", "Inspecionar visualmente o cabo e o anel fônico"],
            "reparo": ["Substituir o sensor de velocidade da roda", "Limpar o anel fônico", "Reparar o chicote elétrico"]
        }
        self.base_dados["codigos_obd2"]["U0100"] = {
            "codigo": "U0100",
            "titulo": "Perda de comunicação com a ECU/PCM",
            "gravidade": "Crítica",
            "descricao": "A comunicação entre o módulo de controle do motor (ECU) e outros módulos do veículo foi perdida.",
            "causas": ["Falha na alimentação ou aterramento da ECU", "Problema no barramento de dados (Rede CAN)", "ECU defeituosa", "Conector da ECU oxidado ou solto"],
            "sintomas": ["Veículo não liga", "Múltiplas luzes de advertência no painel", "Scanner não consegue se comunicar com o motor"],
            "teste": ["Verificar fusíveis e relés da ECU", "Medir a tensão de alimentação e a qualidade do aterramento nos pinos da ECU", "Verificar a integridade da rede CAN com osciloscópio"],
            "reparo": ["Reparar chicote elétrico", "Limpar conectores", "Substituir a ECU (requer programação)"]
        }

    def analisar_dados_vivos(self, modelo, defeito_chave, valor_atual_sensor):
        """Compara os dados atuais do scanner do usuário com o padrão ideal de fábrica."""
        if modelo in self.base_dados["modelos"] and isinstance(self.base_dados["modelos"][modelo], dict):
            defeitos = self.base_dados["modelos"][modelo]["defeitos_comuns"]
            if defeito_chave in defeitos:
                ref = defeitos[defeito_chave]["valores_referencia_live"]
                return {
                    "Status": "Análise Concluída",
                    "Valores de Referência Esperados": ref,
                    "Valor Fornecido pelo Usuário": valor_atual_sensor,
                    "Ação Recomendada": defeitos[defeito_chave].get("teste_recomendado", "Teste recomendado não disponível")
                }
        return {"Erro": "Modelo ou sintoma não mapeado na base de dados vivos."}

    def diagnostico_guiado(self, localizacao, tipo_ruido):
        """Árvore de decisão do diagnóstico guiado.

        Antes usava input() no terminal — agora recebe as respostas como
        parâmetros, para poder ser chamado de uma API.

        Args:
            localizacao: "dianteira" ou "traseira"
            tipo_ruido: depende da localizacao — ver mapeamento abaixo
        """
        localizacao = localizacao.lower().strip()
        tipo_ruido = tipo_ruido.lower().strip()

        if localizacao == "dianteira":
            if tipo_ruido == "lombada":
                return "Diagnóstico: Alta probabilidade de desgaste nas Bieletas ou Buchas da Barra Estabilizadora."
            elif tipo_ruido == "esterçar":
                return "Diagnóstico: Verificar Rolamento do Coxim do Amortecedor ou falta de óleo na bomba de direção."
        elif localizacao == "traseira":
            if tipo_ruido == "estalo":
                return "Diagnóstico: Verificar buchas dos braços tensores traseiros."
            elif tipo_ruido == "zumbido":
                return "Diagnóstico: Forte indício de Rolamento de Roda traseiro danificado."

        return "Sintoma não catalogado na árvore de decisão básica. Verifique os parâmetros enviados."

    def consultar_pinout(self, central, pino):
        """Retorna a função exata de um fio no chicote elétrico da injeção"""
        if central in self.base_dados["esquemas_eletricos"]:
            mapeamento = self.base_dados["esquemas_eletricos"][central]["pinout"]
            pino_busca = f"pino_{pino}"
            if pino_busca in mapeamento:
                return f"Central {central} -> {pino_busca.upper()}: {mapeamento[pino_busca]}"
            return f"Pino {pino} não encontrado na central {central}."
        return "Central elétrica/ECU não cadastrada."

    def analisar_sintoma_visual(self, termo_chave):
        """Interpreta termos leigos como cores de fumaça e texturas de fluidos."""
        termo_ajustado = termo_chave.lower().replace(" ", "_")
        if termo_ajustado in self.base_dados["sintomas_visuais"]:
            return f"Análise Sensorial: {self.base_dados['sintomas_visuais'][termo_ajustado]}"
        return "Sintoma visual não reconhecido. Tente termos como: 'fumaça azulada', 'fumaça branca densa' ou 'oleo cafe com leite'."


class AnalisadorDeTendencias:
    """
    NOVO MÓDULO PARA MANUTENÇÃO PREDITIVA DE FROTAS.
    Analisa séries temporais de dados de telemetria para prever falhas.
    """

    def calcular_score_saude_veiculo(self, dados_telemetria_historicos: List[Dict]) -> Dict:
        """
        Calcula um "Score de Saúde" para o veículo com base na tendência dos sensores.

        Args:
            dados_telemetria_historicos: Uma lista de leituras de telemetria ao longo do tempo.
                                         Ex: [{"timestamp": "...", "ltft": 0.5, "rpm": 800}, ...]

        Returns:
            Um dicionário com o score geral e scores por sistema.
        """
        if not dados_telemetria_historicos or len(dados_telemetria_historicos) < 10:
            return {"erro": "Dados históricos insuficientes para análise de tendência (mínimo 10 registros)."}

        scores = {
            "motor": 100,
            "combustivel": 100,
            "emissoes": 100,
            "geral": 100
        }
        alertas = []

        # Exemplo de análise de tendência para o Long Term Fuel Trim (LTFT)
        ltft_series = [d.get("ltft_b1", 0) for d in dados_telemetria_historicos]
        if ltft_series:
            # Se o LTFT está consistentemente subindo e se aproximando do limite (+10%)
            media_recente = sum(ltft_series[-5:]) / 5
            if media_recente > 8.0:
                # Penaliza o score de combustível e motor
                penalidade = (media_recente - 8.0) * 5 # Penalidade aumenta com a gravidade
                scores["combustivel"] -= penalidade
                scores["motor"] -= penalidade / 2 # Impacto secundário no motor
                alertas.append({
                    "alerta": "Preditivo - Risco de Falha no Sistema de Combustível",
                    "detalhe": f"A correção de combustível de longo prazo (LTFT) está consistentemente alta ({media_recente:.2f}%), indicando uma possível entrada de ar falsa em desenvolvimento ou falha iminente de um sensor (MAF/O2).",
                    "acao_recomendada": "Agendar inspeção do sistema de admissão (teste de fumaça) e sensores de O2/MAF."
                })

        # Exemplo de análise de temperatura do motor
        ect_series = [d.get("ect", 90) for d in dados_telemetria_historicos]
        if ect_series:
            media_temperatura = sum(ect_series) / len(ect_series)
            if media_temperatura > 105: # Se a média geral está acima do normal
                scores["motor"] -= 20
                alertas.append({
                    "alerta": "Preditivo - Risco de Superaquecimento",
                    "detalhe": f"A temperatura média de operação do motor está elevada ({media_temperatura:.1f}°C). Pode indicar problema no termostato, radiador ou ventoinha.",
                    "acao_recomendada": "Verificar sistema de arrefecimento com urgência."
                })

        # Calcula o score geral como a média ponderada dos scores de sistema
        scores["geral"] = round( (scores["motor"] * 0.5) + (scores["combustivel"] * 0.3) + (scores["emissoes"] * 0.2) )

        # Garante que os scores não fiquem negativos
        for k in scores:
            scores[k] = max(0, round(scores[k]))

        return {
            "scores_saude": scores,
            "alertas_preditivos": alertas
        }

    def gerar_relatorio_frota(self, scores_veiculos: Dict[str, Dict]) -> str:
        """
        Gera um resumo executivo para um gestor de frota.

        Args:
            scores_veiculos: Dicionário onde a chave é a placa e o valor é o resultado de `calcular_score_saude_veiculo`.
                             Ex: {"ABC1234": {"scores_saude": {...}, "alertas_preditivos": [...]}}

        Returns:
            Um texto formatado com o status da frota.
        """
        relatorio = ["--- Relatório Executivo da Frota ---"]
        veiculos_criticos = []

        for placa, dados in scores_veiculos.items():
            score_geral = dados.get("scores_saude", {}).get("geral", 100)
            if score_geral < 70:
                veiculos_criticos.append((placa, score_geral, dados.get("alertas_preditivos", [])))

        if not veiculos_criticos:
            relatorio.append("\n✅ Todos os veículos da frota estão operando em condições normais.")
            return "\n".join(relatorio)

        relatorio.append(f"\n⚠️ ATENÇÃO: {len(veiculos_criticos)} veículo(s) requerem manutenção preditiva:\n")
        veiculos_criticos.sort(key=lambda x: x[1]) # Ordena pelo score mais baixo

        for placa, score, alertas in veiculos_criticos:
            relatorio.append(f"  - Veículo: {placa} | Score de Saúde: {score}/100")
            for alerta in alertas:
                relatorio.append(f"    - Alerta: {alerta['detalhe']}")
                relatorio.append(f"    - Ação: {alerta['acao_recomendada']}")
            relatorio.append("")

        return "\n".join(relatorio)

def _serializavel(obj):
    """Função auxiliar para serializar objetos não-padrão para JSON."""
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    if isinstance(obj, dict):
        return {k: _serializavel(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serializavel(i) for i in obj]
    if isinstance(obj, (datetime, timedelta)):
        return obj.isoformat()
    return obj

class PadocAI:
    """Classe principal para diagnóstico automotivo com LLM local e memória por sessão.
    (Refatorada para simplificar consultas e centralizar acesso aos dados)

    IMPORTANTE: crie apenas UMA instância desta classe por processo do servidor
    (padrão singleton). Recriar a cada requisição recarrega o modelo GGUF do
    zero, o que pode levar dezenas de segundos e desperdiça memória.
    """

    def __init__(self, model_path=None):
        self.sistema_especialista = SistemaEspecialistaAutomotivo()
        self.base_conhecimento = BaseConhecimento() # NOVA INSTÂNCIA
        self.estimador_custo = EstimadorCustoReparo() # NOVO: Módulo de custos
        self.analisador_tendencias = AnalisadorDeTendencias() # NOVO: Módulo Preditivo        
        self.historico_veiculo = HistoricoVeiculo() # Melhoria: Instância única        
        # NEW: Initialize TelemetryAI
        # NOVO: Inicializa o analisador de desempenho
        try:
            from brain.performance_analyzer import get_performance_analyzer_instance
            self.performance_analyzer = get_performance_analyzer_instance()
        except ImportError:
            print("Aviso: Módulo PerformanceAnalyzer não encontrado. A consulta de desempenho não funcionará.")
            self.performance_analyzer = None
        try:
            from telemetry_ai import TelemetryAI
            self.telemetry_analyzer = TelemetryAI()
        except ImportError:
            print("Aviso: Módulo TelemetryAI não encontrado. A análise de telemetria avançada pode não funcionar.")
            self.telemetry_analyzer = None
        # NOVO: Inicializa o motor preditivo
        try:
            from predictive_vehicle_ai import PadocPredictiveAI
            self.predictive_analyzer = PadocPredictiveAI()
        except ImportError:
            print("Aviso: Módulo PadocPredictiveAI não encontrado. A análise preditiva não funcionará.")
            self.predictive_analyzer = None
        # NOVO: Inicializa o motor de estado do veículo
        try:
            from vehicle_state_engine import PadocVehicleBrain
            self.state_brain = PadocVehicleBrain()
        except ImportError:
            print("Aviso: Módulo PadocVehicleBrain não encontrado. A análise de estado não funcionará.")
            self.state_brain = None
        self.base = self.sistema_especialista.base_dados

        # Histórico agora é um dicionário: {usuario_id: [ {user, bot}, ... ]}
        # em vez de uma lista única compartilhada por todo mundo.
        self.historico_por_usuario = {}

        if model_path is None:
            env_path = os.environ.get("PADOC_MODEL_PATH")
            if env_path:
                model_path = env_path
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
                model_path = os.path.join(base_path, "models", "padoc-model.gguf")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo GGUF não encontrado em: {model_path}")

        from llama_cpp import Llama
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=8,
            verbose=False
        )

    def _get_historico(self, usuario_id):
        if usuario_id not in self.historico_por_usuario:
            self.historico_por_usuario[usuario_id] = []
        return self.historico_por_usuario[usuario_id]

    def _preparar_contexto(self, usuario_id, nova_pergunta):
        """Prepara o prompt incluindo a base de conhecimento e o histórico da conversa."""
        secao_base = {
            "historico_ordens_servico": self.base.get("historico_ordens_servico"),
            "sintomas_comuns": self.base.get("sintomas_visuais"),
            "defeitos_comuns_modelos": self.base.get("modelos"),
            "codigos_obd2_comuns": self.base.get("codigos_obd2")
        }
        json_base = json.dumps(_serializavel(secao_base), indent=2, ensure_ascii=False)[:3000]

        historico = self._get_historico(usuario_id)
        # Monta a memória da conversa para o LLM não se perder
        historico_formatado = ""
        for turno in historico[-4:]:
            historico_formatado += f"Usuário: {turno['user']}\nPADOC AI: {turno['bot']}\n"

        prompt = f"""Você é a PADOC AI, especialista em diagnóstico automotivo com 20 anos de experiência.
Responda de forma direta, clara e profissional como um mecânico experiente.

Base técnica de suporte:
{json_base}

Histórico da conversa atual:
{historico_formatado}
Usuário: {nova_pergunta}
PADOC AI:"""
        return prompt

    def diagnosticar(self, usuario_id, pergunta):
        """Gera resposta mantendo a memória do chat, isolada por usuário/sessão.

        Args:
            usuario_id: identificador único do usuário/sessão (ex: ID do app Android,
                token de sessão, ou número de série do dispositivo). ESSENCIAL para
                não misturar conversas de mecânicos diferentes.
            pergunta: texto da pergunta/sintoma do usuário.
        """
        try:
            prompt_final = self._preparar_contexto(usuario_id, pergunta)

            resposta = self.llm(
                prompt_final,
                max_tokens=300,
                temperature=0.5,
                top_p=0.9,
                stop=["Usuário:", "PADOC AI:"]
            )

            texto_resposta = resposta["choices"][0]["text"].strip()

            historico = self._get_historico(usuario_id)
            historico.append({"user": pergunta, "bot": texto_resposta})

            return texto_resposta

        except Exception as e:
            return f"Erro ao gerar diagnóstico: {e}"

    def diagnosticar_via_telemetria(self, dtcs, dados_vivos):
        """Recebe a telemetria real do OBD2 e gera um relatório técnico."""
        # Converte os dicionários e listas de telemetria em texto legível para o prompt
        telemetria_str = f"CÓDIGOS DE ERRO DETECTADOS (DTCs): {', '.join(dtcs) if dtcs else 'Nenhum'}\n"
        telemetria_str += "LEITURA DOS SENSORES EM TEMPO REAL:\n"
        for sensor, valor in dados_vivos.items():
            telemetria_str += f"- {sensor}: {valor}\n"

        prompt = f"""Você é a PADOC AI, especialista em diagnóstico automotivo avançado.
Você acabou de receber os dados de telemetria capturados via scanner OBD2 diretamente da ECU do veículo.

Dados de Telemetria Coletados:
{telemetria_str}

Com base na sua base técnica e nesses dados analise e relate o defeito estruturado assim:
1. DIAGNÓSTICO DOS CÓDIGOS DE ERRO: O que significam os códigos DTC encontrados?
2. ANÁLISE DE TELEMETRIA: Os valores dos sensores (dados vivos) estão normais ou alterados?
3. CORRELAÇÃO: Qual a relação entre os sensores alterados e as falhas apontadas?
4. PLANO DE AÇÃO: O que o mecânico deve consertar ou testar agora?
"""

        try:
            resposta = self.llm(
                prompt,
                max_tokens=600,
                temperature=0.3, # Temperatura baixa para o diagnóstico ser preciso e não inventar coisas
                top_p=0.9
            )
            return resposta["choices"][0]["text"].strip()
        except Exception as e:
            return f"Erro ao processar telemetria: {e}"

    def diagnostico_multimodal(self, caminho_foto=None, placa=None, codigo_obd=None, chave_reparo=None,
                               pdf_path=None, video_path=None, wiring_path=None,
                               telemetry_data: Optional[Dict[str, float]] = None, # All raw sensor data here
                               pdf_analyzer=None, video_analyzer=None, wiring_analyzer=None,
                               **kwargs):
        """Orquestra a análise de múltiplas fontes de dados (imagem, áudio, pdf, etc).

        Numa API, os "arquivos" (imagem, áudio, pdf) chegam como uploads do app
        Android e devem ser salvos em um caminho temporário ANTES de chamar esta
        função — passe o caminho do arquivo temporário aqui, não o nome original.
        """
        # Gerar resumos contextuais usando os módulos existentes e os novos
        resumo_imagem = get_analisador_instance().gerar_resumo_para_prompt(caminho_foto)
        resumo_historico = self.historico_veiculo.gerar_resumo_para_prompt(placa, codigo_obd) # Usa a instância única
        resumo_custo = self.estimador_custo.gerar_resumo_para_prompt(chave_reparo)

        # NOVO: Gerar resumos dos novos analisadores
        resumo_pdf = "[Nenhum PDF técnico fornecido.]"
        if pdf_path and pdf_analyzer:
            resultado_pdf = pdf_analyzer.analisar(pdf_path)
            resumo_pdf = f"Análise de PDF técnico: {resultado_pdf['tipo']} com {resultado_pdf['caracteres']} caracteres. Início do texto: '{resultado_pdf['texto']}'"

        resumo_video = "[Nenhum vídeo fornecido.]"
        if video_path and video_analyzer:
            resultado_video = video_analyzer.analisar(video_path)
            resumo_video = f"Análise de vídeo: {resultado_video['tipo']} com {resultado_video['frames']} frames. {resultado_video['diagnostico']}"

        resumo_esquema = "[Nenhum esquema elétrico fornecido.]"
        if wiring_path and wiring_analyzer:
            resultado_esquema = wiring_analyzer.analisar(wiring_path)
            resumo_esquema = f"Análise de esquema elétrico: {resultado_esquema['tipo']} '{resultado_esquema['arquivo']}'. {resultado_esquema['diagnostico']}"

        resumo_telemetria = "[Nenhum dado de telemetria fornecido.]"
        if telemetry_data and telemetry_analyzer:
            resultado_telemetria = telemetry_analyzer.analisar(telemetry_data)
            resumo_telemetria = f"Análise de telemetria: {resultado_telemetria['tipo']} com os seguintes sensores: {resultado_telemetria['sensores']}. {resultado_telemetria['diagnostico']}"

        # Monta o contexto multimodal para o prompt
        contexto_multimodal = f"""
--- CONTEXTO DO VEÍCULO E PROBLEMA ---
{resumo_historico}
--- ANÁLISE VISUAL ---
{resumo_imagem}
{resumo_video}
--- ANÁLISE DE DOCUMENTOS TÉCNICOS ---
{resumo_pdf}
{resumo_esquema}
{resumo_telemetria}
--- ESTIMATIVA DE CUSTO (se aplicável) ---
{resumo_custo}
"""

        prompt = f"""Você é a PADOC AI, a mais avançada IA de diagnóstico automotivo. Sua tarefa é atuar como um mestre diagnosticador, correlacionando todas as evidências de múltiplas fontes para encontrar a causa raiz de um problema. Seja técnico e preciso.

Abaixo estão os dados brutos e pré-analisados de várias fontes (sensores, imagens, áudios, manuais):

--- EVIDÊNCIAS COLETADAS ---
{contexto_multimodal}
--- FIM DAS EVIDÊNCIAS ---
 
Com base em TODAS as evidências acima, gere um laudo técnico completo e unificado, seguindo esta estrutura:
1.  **Resumo do Problema:** Descreva o cenário geral com base nos dados.
2.  **Correlação de Dados:** Explique como as diferentes evidências (ex: o ruído no áudio, o código OBD e o sinal do osciloscópio) se conectam.
3.  **Hipótese Principal:** Qual é a causa raiz mais provável do problema?
4.  **Diagnóstico Diferencial:** Quais outras possibilidades existem, mas são menos prováveis?
5.  **Plano de Ação Detalhado:** Liste os próximos passos exatos que o mecânico deve seguir para confirmar e reparar o defeito.
"""
        resposta = self.llm(prompt, max_tokens=700, temperature=0.4, top_p=0.9)
        return resposta["choices"][0]["text"].strip()

    # ------------------ WRAPPERS DO SISTEMA ESPECIALISTA ------------------
    def analisar_dados_vivos(self, modelo, defeito_chave, valor_atual_sensor):
        return self.sistema_especialista.analisar_dados_vivos(modelo, defeito_chave, valor_atual_sensor)

    def diagnostico_guiado(self, localizacao, tipo_ruido):
        return self.sistema_especialista.diagnostico_guiado(localizacao, tipo_ruido)

    def consultar_pinout(self, central, pino):
        return self.sistema_especialista.consultar_pinout(central, pino)

    def analisar_sintoma_visual(self, termo_chave):
        return self.sistema_especialista.analisar_sintoma_visual(termo_chave)

    # NOVO: Wrappers para o Estimador de Custos
    def estimar_custo_reparo(self, chave_reparo, urgencia="normal"):
        return self.estimador_custo.estimar(chave_reparo, urgencia)

    def gerar_resumo_custo(self, chave_reparo, urgencia="normal"):
        return self.estimador_custo.gerar_resumo_para_prompt(chave_reparo, urgencia)

    # NOVO: Wrapper para o Performance Analyzer
    def consultar_desempenho_veiculo(self, nome_veiculo: str):
        """
        Wrapper para o novo analisador de desempenho.
        Retorna um dicionário com os dados ou uma mensagem de erro.
        """
        if not self.performance_analyzer:
            return {"erro": "O módulo de análise de desempenho não está disponível."}
        
        resultado = self.performance_analyzer.consultar_desempenho(nome_veiculo)

        if resultado:
            return resultado
        
        return {"erro": f"Nenhum dado de desempenho encontrado para um veículo com o nome '{nome_veiculo}'."}

    # --- NOVOS MÉTODOS PARA MANUTENÇÃO PREDITIVA ---
    def analisar_saude_veiculo(self, dados_telemetria_historicos: List[Dict]):
        """Wrapper para o novo analisador de tendências."""
        return self.analisador_tendencias.calcular_score_saude_veiculo(dados_telemetria_historicos)

    def gerar_relatorio_para_frota(self, scores_por_veiculo: Dict[str, Dict]):
        """Wrapper para o novo gerador de relatórios de frota."""
        return self.analisador_tendencias.gerar_relatorio_frota(scores_por_veiculo)

    # --- NOVOS MÉTODOS DE CONSULTA TÉCNICA ---
    def consultar_especificacao(self, codigo_veiculo: str, especificacao: str):
        """
        NOVO MÉTODO GENÉRICO: Consulta qualquer especificação técnica de um veículo.
        Substitui os múltiplos métodos 'consultar_*' por um único ponto de acesso.

        Exemplos de 'especificacao': 'torque_componentes', 'oleo_motor', 'procedimentos', 'sincronismo'.
        """
        veiculo = self.base_conhecimento.get_dados_veiculo(codigo_veiculo)

        if not veiculo:
            return {"erro": f"Veículo com código '{codigo_veiculo}' não encontrado."}

        # O JSON carregado é um dicionário. Podemos buscar o atributo diretamente.
        valor = veiculo.get(especificacao)

        if valor is not None:
            return {especificacao: valor}
        
        return {"erro": f"Especificação '{especificacao}' não encontrada para o veículo '{codigo_veiculo}'."}

    def analisar_evento_veicular(self, tipo_evento, dados_evento):
        """
        NOVO MÉTODO: Analisa eventos de hardware como alertas de colisão, geofence, etc.

        Args:
            tipo_evento (str): 'colisao', 'geofence_entrada', 'geofence_saida', 'reboque'.
            dados_evento (dict): Dados contextuais do evento.
                                 Ex: {'latitude': -23.5, 'longitude': -46.6, 'aceleracao_g': 5.2}
        """
        if tipo_evento == "colisao":
            aceleracao = dados_evento.get("aceleracao_g", 0)
            if aceleracao > 8.0:
                nivel = "Grave"
            elif aceleracao > 4.0:
                nivel = "Moderada"
            else:
                nivel = "Leve"
            
            return {
                "alerta": f"Detectada colisão {nivel}",
                "detalhes": f"Pico de desaceleração de {aceleracao} G.",
                "acao_recomendada": "Contatar o motorista imediatamente. Enviar serviços de emergência se necessário.",
                "localizacao": f"https://www.google.com/maps?q={dados_evento.get('latitude')},{dados_evento.get('longitude')}"
            }

        if tipo_evento == "geofence_entrada":
            return {
                "alerta": "Veículo entrou em área restrita",
                "detalhes": f"Veículo entrou na geocerca '{dados_evento.get('nome_geocerca', 'N/A')}'.",
                "acao_recomendada": "Verificar se a entrada na área é autorizada."
            }

        if tipo_evento == "reboque":
            return {
                "alerta": "Alerta de Reboque/Movimentação Indevida",
                "detalhes": "Veículo foi movido com a ignição desligada.",
                "acao_recomendada": "Contatar o proprietário para verificar possível furto ou reboque."
            }

        return {"erro": f"Tipo de evento '{tipo_evento}' não reconhecido."}

# ------------------ PADRÃO SINGLETON PARA A API ------------------
# Importe _padoc_instance de outros arquivos (ex: api.py) em vez de criar
# uma nova instância de PadocAI() a cada requisição.
_padoc_instance = None


def get_padoc_instance():
    """Retorna a instância única (singleton) do PadocAI, criando-a na primeira chamada.

    Use esta função no seu api.py em vez de `PadocAI()` diretamente, assim o
    modelo GGUF é carregado uma única vez quando o servidor sobe.
    """
    global _padoc_instance
    if _padoc_instance is None:
        _padoc_instance = PadocAI()
    return _padoc_instance
