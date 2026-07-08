import librosa

class AudioAI:

    def analisar(self,audio):

        y,sr=librosa.load(audio)

        duracao=librosa.get_duration(y=y,sr=sr)

        return{
            "tipo":"Áudio",
            "duracao":duracao,
            "diagnostico":"Ruído carregado."
        }