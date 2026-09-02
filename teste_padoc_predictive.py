from datetime import datetime, timedelta

from predictive_vehicle_ai import (
    PadocPredictiveAI,
    VehicleReading
)


ai = PadocPredictiveAI()


vehicle_id = "PADOC-001"


# ============================================================
# SIMULA HISTÓRICO
# ============================================================

for i in range(20):

    reading = VehicleReading(

        timestamp=datetime.utcnow()
        - timedelta(hours=20 - i),

        rpm=850 + i * 2,

        coolant_temp=92 + i * 0.8,

        battery_voltage=12.7 - i * 0.025,

        fuel_trim_short=3 + i * 0.3,

        fuel_trim_long=2 + i * 0.4,

        vehicle_speed=60,

        engine_load=35,

        dtcs=[]
    )

    ai.add_reading(
        vehicle_id,
        reading
    )


# ============================================================
# ÚLTIMA LEITURA
# ============================================================

ai.add_reading(

    vehicle_id,

    VehicleReading(

        timestamp=datetime.utcnow(),

        rpm=920,

        coolant_temp=108,

        battery_voltage=12.05,

        fuel_trim_short=12,

        fuel_trim_long=13,

        vehicle_speed=60,

        engine_load=42,

        dtcs=[
            "P0171"
        ]
    )
)


# ============================================================
# ANÁLISE
# ============================================================

result = ai.analyze(
    vehicle_id
)


print()
print("==============================")
print("      PADOC VEHICLE AI")
print("==============================")

print(
    f"Veículo: {result.vehicle_id}"
)

print(
    f"Saúde global: "
    f"{result.global_health}%"
)

print(
    f"Risco global: "
    f"{result.global_risk}%"
)

print(
    f"Nível: "
    f"{result.risk_level}"
)


print()
print("COMPONENTES")
print("------------------------------")


for name, component in result.components.items():

    print()

    print(
        f"{name}: "
        f"{component.health_score}%"
    )

    print(
        f"Risco 7 dias: "
        f"{component.failure_probability_7d}%"
    )

    print(
        f"Risco 30 dias: "
        f"{component.failure_probability_30d}%"
    )

    print(
        f"Risco 90 dias: "
        f"{component.failure_probability_90d}%"
    )

    print(
        f"Tendência: "
        f"{component.trend}"
    )


print()
print("ALERTAS")
print("------------------------------")

for alert in result.alerts:

    print(
        "⚠️",
        alert
    )


print()
print("RECOMENDAÇÕES")
print("------------------------------")

for recommendation in result.recommendations:

    print(
        "🔧",
        recommendation
    )