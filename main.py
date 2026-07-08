from multimodal.orchestrator import PadocMultimodal
import json

ia = PadocMultimodal()

resultado = ia.analisar(

    imagem="motor.jpg",

    video="motor.mp4",

    audio="ruido.wav",

    obd=["P0300","P0171"],

    telemetria={

        "RPM":850,

        "MAP":32,

        "TPS":4.5

    },

    pdf="manual.pdf",

    esquema="esquema.pdf",

    osciloscopio="sinal.csv"

)

print(json.dumps(resultado, indent=4, ensure_ascii=False))