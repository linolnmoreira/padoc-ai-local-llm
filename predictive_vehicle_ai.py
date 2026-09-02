from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional
import math
import statistics


# ============================================================
# LEITURA DO VEÍCULO
# ============================================================

@dataclass
class VehicleReading:

    timestamp: datetime

    rpm: float
    coolant_temp: float
    battery_voltage: float

    fuel_trim_short: float
    fuel_trim_long: float

    vehicle_speed: float
    engine_load: float

    dtcs: List[str]


# ============================================================
# ESTADO DE UM COMPONENTE
# ============================================================

@dataclass
class ComponentHealth:

    name: str

    health_score: float = 100.0

    degradation_rate: float = 0.0

    failure_probability_7d: float = 0.0
    failure_probability_30d: float = 0.0
    failure_probability_90d: float = 0.0

    trend: str = "NORMAL"

    observations: Optional[List[str]] = None

    def __post_init__(self):

        if self.observations is None:
            self.observations = []


# ============================================================
# RESULTADO GLOBAL
# ============================================================

@dataclass
class VehiclePrediction:

    vehicle_id: str

    global_health: float

    global_risk: float

    risk_level: str

    components: Dict[str, ComponentHealth]

    alerts: List[str]

    recommendations: List[str]

    timestamp: datetime


# ============================================================
# MOTOR PREDITIVO PADOC
# ============================================================

class PadocPredictiveAI:

    def __init__(self):

        self.history: Dict[str, List[VehicleReading]] = {}

        self.components = [
            "ENGINE",
            "COOLING",
            "ELECTRICAL",
            "FUEL_SYSTEM",
            "BATTERY"
        ]

    # --------------------------------------------------------
    # RECEBER LEITURA
    # --------------------------------------------------------

    def add_reading(
        self,
        vehicle_id: str,
        reading: VehicleReading
    ):

        if vehicle_id not in self.history:

            self.history[vehicle_id] = []

        self.history[vehicle_id].append(reading)

        # Limita histórico em memória
        if len(self.history[vehicle_id]) > 1000:

            self.history[vehicle_id] = \
                self.history[vehicle_id][-1000:]

    # --------------------------------------------------------
    # ANALISAR VEÍCULO
    # --------------------------------------------------------

    def analyze(
        self,
        vehicle_id: str
    ) -> VehiclePrediction:

        if vehicle_id not in self.history:

            raise ValueError(
                "Nenhum histórico encontrado para o veículo."
            )

        history = self.history[vehicle_id]

        components = {}

        components["ENGINE"] = \
            self._analyze_engine(history)

        components["COOLING"] = \
            self._analyze_cooling(history)

        components["ELECTRICAL"] = \
            self._analyze_electrical(history)

        components["FUEL_SYSTEM"] = \
            self._analyze_fuel_system(history)

        components["BATTERY"] = \
            self._analyze_battery(history)

        global_health = self._calculate_global_health(
            components
        )

        global_risk = round(
            100 - global_health,
            2
        )

        risk_level = self._risk_level(
            global_risk
        )

        alerts = self._generate_alerts(
            components
        )

        recommendations = self._generate_recommendations(
            components
        )

        return VehiclePrediction(

            vehicle_id=vehicle_id,

            global_health=round(
                global_health,
                2
            ),

            global_risk=global_risk,

            risk_level=risk_level,

            components=components,

            alerts=alerts,

            recommendations=recommendations,

            timestamp=datetime.utcnow()
        )

    # ========================================================
    # MOTOR
    # ========================================================

    def _analyze_engine(
        self,
        history
    ):

        health = 100

        observations = []

        latest = history[-1]

        rpm_values = [
            x.rpm for x in history
        ]

        if len(rpm_values) >= 5:

            rpm_variation = statistics.pstdev(
                rpm_values[-20:]
            )

            if rpm_variation > 100:

                health -= 15

                observations.append(
                    "Variação anormal de RPM."
                )

        if latest.dtcs:

            engine_dtcs = [

                x for x in latest.dtcs
                if x.startswith("P03")
                or x.startswith("P01")
                or x.startswith("P02")
            ]

            if engine_dtcs:

                health -= min(
                    30,
                    len(engine_dtcs) * 10
                )

                observations.append(
                    "DTCs relacionados ao motor."
                )

        trend = self._calculate_trend(
            rpm_values
        )

        degradation = self._estimate_degradation(
            rpm_values
        )

        return self._build_component(

            "ENGINE",
            health,
            degradation,
            trend,
            observations
        )

    # ========================================================
    # ARREFECIMENTO
    # ========================================================

    def _analyze_cooling(
        self,
        history
    ):

        temperatures = [
            x.coolant_temp
            for x in history
        ]

        latest = temperatures[-1]

        health = 100

        observations = []

        if latest >= 105:

            health -= 15

            observations.append(
                "Temperatura elevada."
            )

        if latest >= 110:

            health -= 25

            observations.append(
                "Temperatura crítica."
            )

        degradation = self._estimate_degradation(
            temperatures
        )

        trend = self._calculate_trend(
            temperatures
        )

        return self._build_component(

            "COOLING",
            health,
            degradation,
            trend,
            observations
        )

    # ========================================================
    # SISTEMA ELÉTRICO
    # ========================================================

    def _analyze_electrical(
        self,
        history
    ):

        voltage = [
            x.battery_voltage
            for x in history
        ]

        latest = voltage[-1]

        health = 100

        observations = []

        if latest < 12.2:

            health -= 15

            observations.append(
                "Tensão abaixo do esperado."
            )

        if latest < 11.8:

            health -= 25

            observations.append(
                "Tensão muito baixa."
            )

        degradation = self._estimate_degradation(
            voltage
        )

        trend = self._calculate_trend(
            voltage
        )

        return self._build_component(

            "ELECTRICAL",
            health,
            degradation,
            trend,
            observations
        )

    # ========================================================
    # SISTEMA DE COMBUSTÍVEL
    # ========================================================

    def _analyze_fuel_system(
        self,
        history
    ):

        health = 100

        observations = []

        values = []

        for x in history:

            trim = (
                x.fuel_trim_short
                +
                x.fuel_trim_long
            )

            values.append(trim)

        latest = values[-1]

        if abs(latest) > 10:

            health -= 15

            observations.append(
                "Correção de combustível elevada."
            )

        if abs(latest) > 20:

            health -= 25

            observations.append(
                "Forte desvio de mistura."
            )

        degradation = self._estimate_degradation(
            values
        )

        trend = self._calculate_trend(
            values
        )

        return self._build_component(

            "FUEL_SYSTEM",
            health,
            degradation,
            trend,
            observations
        )

    # ========================================================
    # BATERIA
    # ========================================================

    def _analyze_battery(
        self,
        history
    ):

        values = [
            x.battery_voltage
            for x in history
        ]

        latest = values[-1]

        health = 100

        observations = []

        if latest < 12.4:

            health -= 10

            observations.append(
                "Bateria abaixo da tensão ideal."
            )

        if latest < 12.0:

            health -= 25

            observations.append(
                "Bateria com baixa tensão."
            )

        degradation = self._estimate_degradation(
            values
        )

        trend = self._calculate_trend(
            values
        )

        return self._build_component(

            "BATTERY",
            health,
            degradation,
            trend,
            observations
        )

    # ========================================================
    # CRIAR COMPONENTE
    # ========================================================

    def _build_component(
        self,
        name,
        health,
        degradation,
        trend,
        observations
    ):

        health = max(
            0,
            min(100, health)
        )

        # Converte degradação em risco
        risk = max(
            0,
            min(
                100,
                (100 - health)
                +
                abs(degradation) * 10
            )
        )

        probability_7 = self._probability(
            risk,
            7
        )

        probability_30 = self._probability(
            risk,
            30
        )

        probability_90 = self._probability(
            risk,
            90
        )

        return ComponentHealth(

            name=name,

            health_score=round(
                health,
                2
            ),

            degradation_rate=round(
                degradation,
                4
            ),

            failure_probability_7d=round(
                probability_7,
                2
            ),

            failure_probability_30d=round(
                probability_30,
                2
            ),

            failure_probability_90d=round(
                probability_90,
                2
            ),

            trend=trend,

            observations=observations
        )

    # ========================================================
    # TENDÊNCIA
    # ========================================================

    def _calculate_trend(
        self,
        values
    ):

        if len(values) < 5:

            return "INSUFICIENTE"

        recent = values[-5:]

        older = values[-10:-5]

        if len(older) < 5:

            return "INSUFICIENTE"

        recent_avg = statistics.mean(
            recent
        )

        older_avg = statistics.mean(
            older
        )

        difference = (
            recent_avg -
            older_avg
        )

        if abs(difference) < 0.5:

            return "ESTÁVEL"

        if difference > 0:

            return "SUBINDO"

        return "DESCENDO"

    # ========================================================
    # TAXA DE DEGRADAÇÃO
    # ========================================================

    def _estimate_degradation(
        self,
        values
    ):

        if len(values) < 10:

            return 0

        recent = statistics.mean(
            values[-5:]
        )

        previous = statistics.mean(
            values[-10:-5]
        )

        return recent - previous

    # ========================================================
    # PROBABILIDADE
    # ========================================================

    def _probability(
        self,
        risk,
        days
    ):

        # Modelo inicial simplificado.
        # Não representa probabilidade estatística
        # validada de falha real.

        time_factor = math.log1p(days)

        probability = (
            risk *
            (time_factor / 5)
        )

        return max(
            0,
            min(
                99,
                probability
            )
        )

    # ========================================================
    # SAÚDE GLOBAL
    # ========================================================

    def _calculate_global_health(
        self,
        components
    ):

        weights = {

            "ENGINE": 0.30,

            "COOLING": 0.20,

            "ELECTRICAL": 0.15,

            "FUEL_SYSTEM": 0.15,

            "BATTERY": 0.20
        }

        score = 0

        for name, component in components.items():

            score += (
                component.health_score
                *
                weights.get(
                    name,
                    0
                )
            )

        return score

    # ========================================================
    # NÍVEL DE RISCO
    # ========================================================

    def _risk_level(
        self,
        risk
    ):

        if risk < 10:

            return "NORMAL"

        if risk < 25:

            return "BAIXO"

        if risk < 50:

            return "MÉDIO"

        if risk < 75:

            return "ALTO"

        return "CRÍTICO"

    # ========================================================
    # ALERTAS
    # ========================================================

    def _generate_alerts(
        self,
        components
    ):

        alerts = []

        for component in components.values():

            if component.failure_probability_30d >= 60:

                alerts.append(

                    f"{component.name}: "
                    f"risco elevado nos próximos 30 dias."
                )

            if component.trend in [
                "SUBINDO",
                "DESCENDO"
            ]:

                alerts.append(

                    f"{component.name}: "
                    f"tendência {component.trend}."
                )

        return alerts

    # ========================================================
    # RECOMENDAÇÕES
    # ========================================================

    def _generate_recommendations(
        self,
        components
    ):

        recommendations = []

        for component in components.values():

            if component.health_score < 70:

                recommendations.append(

                    f"Inspecionar {component.name}."
                )

            if component.failure_probability_30d >= 60:

                recommendations.append(

                    f"Programar manutenção preventiva "
                    f"de {component.name}."
                )

        return recommendations

    # ========================================================
    # EXPORTAR JSON
    # ========================================================

    def to_dict(
        self,
        prediction
    ):
        return asdict(prediction)

    def processar_telemetria_json(self, vehicle_id: str, dados: dict) -> dict:
        """
        Recebe um dicionário de dados de telemetria (ex: vindo da API REST/WebSocket),
        registra no histórico e retorna a predição completa formatada.
        """
        reading = VehicleReading(
            timestamp=datetime.now(),
            rpm=float(dados.get("rpm", 850.0)),
            coolant_temp=float(dados.get("coolant_temp", dados.get("temperatura", 90.0))),
            battery_voltage=float(dados.get("battery_voltage", dados.get("voltagem", 13.8))),
            fuel_trim_short=float(dados.get("fuel_trim_short", dados.get("stft", 0.0))),
            fuel_trim_long=float(dados.get("fuel_trim_long", dados.get("ltft", 0.0))),
            vehicle_speed=float(dados.get("vehicle_speed", dados.get("velocidade", 0.0))),
            engine_load=float(dados.get("engine_load", dados.get("carga", 25.0))),
            dtcs=dados.get("dtcs", [])
        )
        self.add_reading(vehicle_id, reading)
        pred = self.analyze(vehicle_id)
        return self.to_dict(pred)

# Instância Singleton global do motor preditivo
predictive_engine = PadocPredictiveAI()