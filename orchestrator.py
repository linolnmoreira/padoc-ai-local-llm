from image_ai import ImageAI # Corrigido: Caminho de importação
from video_ai import VideoAI # Corrigido: Caminho de importação
from audio_ai import AudioAI # Corrigido: Caminho de importação
from obd_ai import OBDAI # Corrigido: Caminho de importação
from telemetry_ai import TelemetryAI # Corrigido: Caminho de importação
from pdf_ai import PDFAI # Corrigido: Caminho de importação
from wiring_ai import WiringAI # Corrigido: Caminho de importação
from oscilloscope_ai import OscilloscopeAI # Corrigido: Caminho de importação
from symptom_classifier import classify_symptom

class PadocMultimodal:

    def __init__(self):

        self.image=ImageAI()

        self.video=VideoAI()

        self.audio=AudioAI()

        self.obd=OBDAI()

        self.telemetry=TelemetryAI()

        self.pdf=PDFAI()

        self.wiring=WiringAI()

        self.scope=OscilloscopeAI()

    def analisar(

        self,

        imagem=None,

        video=None,

        audio=None,

        obd=None,

        telemetria=None,

        pdf=None,

        esquema=None,

        osciloscopio=None

    ):

        resultado={}

        if imagem:
            resultado["imagem"]=self.image.analisar(imagem)

        if video:
            resultado["video"]=self.video.analisar(video)

        if audio:
            resultado["audio"]=self.audio.analisar(audio)

        if obd:
            resultado["obd"]=self.obd.analisar(obd)

        if telemetria:
            resultado["telemetria"]=self.telemetry.analisar(telemetria)

        if pdf:
            resultado["pdf"]=self.pdf.analisar(pdf)

        if esquema:
            resultado["esquema"]=self.wiring.analisar(esquema)

        if osciloscopio:
            resultado["osciloscopio"]=self.scope.analisar(osciloscopio)

        # Integrate symptom classification if audio or OBD data is available
        if "audio" in resultado or "obd" in resultado:
            audio_features = resultado.get("audio", {})
            obd_data = resultado.get("obd", {})
            classification_result = classify_symptom(audio_features, obd_data)
            resultado["diagnostico"] = classification_result