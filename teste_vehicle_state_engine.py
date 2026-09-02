from vehicle_state_engine import PadocVehicleBrain, VehicleTelemetry
from dataclasses import asdict
import json

# Função auxiliar para converter o resultado para um formato JSON legível
def to_serializable(val):
    if hasattr(val, '__dict__'):
        return asdict(val)
    if isinstance(val, list):
        return [to_serializable(v) for v in val]
    if isinstance(val, dict):
        return {k: to_serializable(v) for k, v in val.items()}
    if hasattr(val, 'name'): # Para Enums
        return val.name
    return val

# Exemplo de utilização com os dados fornecidos
telemetry = VehicleTelemetry(
    rpm=850,
    coolant_temp=108,
    battery_voltage=12.1,
    fuel_trim_short=8,
    fuel_trim_long=14,
    dtcs=["P0171"]
)

brain = PadocVehicleBrain()

result = brain.process(telemetry)

# Extrai o estado e a recomendação
state = result['vehicle_state']
recommendation = result['recommendation']

# Imprime o resultado formatado
print()
print("==============================")
print("    PADOC VEHICLE BRAIN")
print("==============================")

print(f"\nSaúde Global: {state.global_health:.2f}%")
print(f"Nível de Risco: {state.risk.name}")

print("\nSAÚDE DOS COMPONENTES")
print("------------------------------")
print(f"Motor:          {state.engine_health:.2f}%")
print(f"Elétrica:       {state.electrical_health:.2f}%")
print(f"Arrefecimento:  {state.cooling_health:.2f}%")
print(f"Transmissão:    {state.transmission_health:.2f}%")
print(f"Freios:         {state.braking_health:.2f}%")

if state.anomalies:
    print("\nANOMALIAS DETECTADAS")
    print("------------------------------")
    for anomaly in state.anomalies:
        print(f"- {anomaly}")

if state.recommendations:
    print("\nRECOMENDAÇÕES INICIAIS")
    print("------------------------------")
    for rec in state.recommendations:
        print(f"- {rec}")

print("\nRECOMENDAÇÃO DA IA")
print("------------------------------")
print(f"Ação Sugerida: {recommendation.action.name}")
print(f"Motivo: {recommendation.reason}")
print(f"Confiança: {recommendation.confidence * 100:.1f}%")

print("\n--- DADOS BRUTOS (JSON) ---")
serializable_result = to_serializable(result)
print(json.dumps(serializable_result, indent=2))


# Exemplo de como o SafetyGate seria usado
print("\n--- TESTE DO SAFETY GATE ---")
auth_result = brain.safety_gate.authorize("brakes", "apply_force", recommendation)
print(f"Tentativa de acionar freios: Autorizado? {auth_result['authorized']}. Motivo: {auth_result['reason']}")

auth_result_ok = brain.safety_gate.authorize("cooling_fan", "activate", recommendation)
print(f"Tentativa de ligar ventoinha: Autorizado? {auth_result_ok['authorized']}. Motivo: {auth_result_ok['reason']}")