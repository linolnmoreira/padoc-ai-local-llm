import os
import librosa
import numpy as np

class AudioAI:

    def __init__(self):
        self.modelo = None
        self.classes = [
            "motor_normal",
            "batida_biela",
            "tucho",
            "valvula",
            "correia",
            "rolamento",
            "detonacao",
            "escape",
            "desconhecido"
        ]

    def analisar(self, audio):

        if not os.path.exists(audio):
            return {
                "erro": "Arquivo não encontrado."
            }

        try:

            y, sr = librosa.load(audio, sr=22050, mono=True)

            duracao = float(librosa.get_duration(y=y, sr=sr))

            rms = float(np.mean(librosa.feature.rms(y=y)))

            zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))

            centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))

            bandwidth = float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))

            rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))

            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_media = float(np.mean(chroma))

            mel = librosa.feature.melspectrogram(y=y, sr=sr)
            mel_db = librosa.power_to_db(mel)

            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)

            mfcc_media = mfcc.mean(axis=1).tolist()

            diagnostico = self.diagnostico_regras(
                rms,
                centroid,
                bandwidth,
                zcr
            )

            return {

                                "tipo": "Áudio",

                "taxa_amostragem": sr,

                "duracao_segundos": round(duracao,2),

                "energia_rms": round(rms,5),

                "zero_crossing_rate": round(zcr,5),

                "spectral_centroid": round(centroid,2),

                "spectral_bandwidth": round(bandwidth,2),

                "spectral_rolloff": round(rolloff,2),

                "chroma_media": round(chroma_media,3),

                "mfcc": mfcc_media,

                "diagnostico": diagnostico,

                "frequency": round(centroid,2),

                "intensity": round(rms,5),

                "rpm": None,

                "load": None,

                "temperature": None,

                "engine_state": None,

                "operation_mode": None,

                "location": None

            }

        except Exception as e:

            return {

                "erro": str(e)

            }

    def diagnostico_regras(
        self,
        rms,
        centroid,
        bandwidth,
        zcr
    ):

        suspeitas = []

        if rms > 0.15:
            suspeitas.append("Ruído intenso.")

        if centroid > 3500:
            suspeitas.append("Possível correia ou rolamento.")

        if bandwidth > 2500:
            suspeitas.append("Ruído metálico.")

        if zcr > 0.18:
            suspeitas.append("Possível batida rápida.")

        if len(suspeitas) == 0:
            suspeitas.append("Nenhuma anomalia evidente.")

        return suspeitas