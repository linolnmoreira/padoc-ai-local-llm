from multimodal.image_ai import ImageAI
from multimodal.video_ai import VideoAI
from multimodal.audio_ai import AudioAI
from multimodal.obd_ai import OBDAI
from multimodal.telemetry_ai import TelemetryAI
from multimodal.pdf_ai import PDFAI
from multimodal.wiring_ai import WiringAI
from multimodal.oscilloscope_ai import OscilloscopeAI

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

        return resultado