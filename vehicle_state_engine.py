from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime


class RiskLevel(Enum):
    NORMAL = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ActionType(Enum):
    NONE = "none"
    ALERT = "alert"
    DIAGNOSTIC_TEST = "diagnostic_test"
    MAINTENANCE = "maintenance"
    SAFE_DEGRADATION = "safe_degradation"


@dataclass
class VehicleTelemetry:

    rpm: float = 0
    coolant_temp: float = 0
    battery_voltage: float = 0
    oil_pressure: Optional[float] = None

    vehicle_speed: float = 0
    throttle_position: float = 0

    fuel_trim_short: float = 0
    fuel_trim_long: float = 0

    dtcs: List[str] = field(default_factory=list)

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class VehicleState:

    engine_health: float = 100
    electrical_health: float = 100
    cooling_health: float = 100
    transmission_health: float = 100
    braking_health: float = 100

    global_health: float = 100

    risk: RiskLevel = RiskLevel.NORMAL

    anomalies: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class AIRecommendation:

    action: ActionType
    reason: str
    confidence: float
    risk: RiskLevel
    requires_human: bool = False


class VehicleStateEngine:

    def analyze(self, data: VehicleTelemetry) -> VehicleState:

        state = VehicleState()

        self._analyze_temperature(data, state)
        self._analyze_battery(data, state)
        self._analyze_fuel_trim(data, state)
        self._analyze_dtcs(data, state)

        self._calculate_global_health(state)
        self._calculate_risk(state)

        return state

    def _analyze_temperature(self, data, state):

        if data.coolant_temp >= 110:

            state.cooling_health -= 25

            state.anomalies.append(
                "Temperatura do líquido de arrefecimento elevada"
            )

            state.recommendations.append(
                "Verificar sistema de arrefecimento"
            )

        elif data.coolant_temp >= 100:

            state.cooling_health -= 10

    def _analyze_battery(self, data, state):

        if data.battery_voltage < 11.8:

            state.electrical_health -= 30

            state.anomalies.append(
                "Tensão da bateria abaixo do esperado"
            )

        elif data.battery_voltage < 12.2:

            state.electrical_health -= 10

    def _analyze_fuel_trim(self, data, state):

        trim = abs(
            data.fuel_trim_short +
            data.fuel_trim_long
        )

        if trim > 20:

            state.engine_health -= 20

            state.anomalies.append(
                "Correção de combustível elevada"
            )

            state.recommendations.append(
                "Investigar mistura, entrada de ar ou alimentação"
            )

    def _analyze_dtcs(self, data, state):

        if data.dtcs:

            state.engine_health -= min(
                len(data.dtcs) * 5,
                30
            )

            state.anomalies.append(
                f"DTCs detectados: {', '.join(data.dtcs)}"
            )

    def _calculate_global_health(self, state):

        values = [
            state.engine_health,
            state.electrical_health,
            state.cooling_health,
            state.transmission_health,
            state.braking_health
        ]

        state.global_health = max(
            0,
            min(100, sum(values) / len(values))
        )

    def _calculate_risk(self, state):

        if state.global_health >= 90:
            state.risk = RiskLevel.NORMAL

        elif state.global_health >= 75:
            state.risk = RiskLevel.LOW

        elif state.global_health >= 50:
            state.risk = RiskLevel.MEDIUM

        elif state.global_health >= 25:
            state.risk = RiskLevel.HIGH

        else:
            state.risk = RiskLevel.CRITICAL


class SafetyGate:

    CRITICAL_SYSTEMS = {
        "brakes",
        "steering",
        "airbag",
        "accelerator",
        "high_voltage_battery"
    }

    def authorize(
        self,
        system: str,
        action: str,
        recommendation: AIRecommendation
    ):

        if system in self.CRITICAL_SYSTEMS:
            return {
                "authorized": False,
                "reason": "Sistema crítico bloqueado para controle direto da IA."
            }

        if recommendation.confidence < 0.80:
            return {
                "authorized": False,
                "reason": "Confiança insuficiente para execução."
            }

        if recommendation.risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return {
                "authorized": False,
                "reason": "Ação requer validação adicional."
            }

        return {
            "authorized": True,
            "reason": "Ação permitida pelo Safety Gate."
        }


class PadocVehicleBrain:

    def __init__(self):
        self.state_engine = VehicleStateEngine()
        self.safety_gate = SafetyGate()

    def process(self, telemetry: VehicleTelemetry):
        state = self.state_engine.analyze(telemetry)
        recommendation = self._create_recommendation(state)
        return {
            "vehicle_state": state,
            "recommendation": recommendation
        }

    def _create_recommendation(self, state: VehicleState):
        if state.risk == RiskLevel.CRITICAL:
            return AIRecommendation(
                action=ActionType.ALERT,
                reason="Estado crítico detectado.",
                confidence=0.95,
                risk=RiskLevel.CRITICAL,
                requires_human=True
            )
        if state.risk == RiskLevel.HIGH:
            return AIRecommendation(
                action=ActionType.MAINTENANCE,
                reason="Manutenção prioritária recomendada.",
                confidence=0.90,
                risk=RiskLevel.HIGH,
                requires_human=True
            )
        if state.risk == RiskLevel.MEDIUM:
            return AIRecommendation(
                action=ActionType.DIAGNOSTIC_TEST,
                reason="Executar testes adicionais.",
                confidence=0.85,
                risk=RiskLevel.MEDIUM
            )
        return AIRecommendation(
            action=ActionType.NONE,
            reason="Nenhuma intervenção necessária.",
            confidence=0.95,
            risk=RiskLevel.NORMAL
        )