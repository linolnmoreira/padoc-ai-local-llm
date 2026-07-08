import cv2

class VideoAI:

    def analisar(self, video):

        cap=cv2.VideoCapture(video)

        total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        cap.release()

        return{
            "tipo":"Vídeo",
            "frames":total,
            "diagnostico":"Vídeo recebido."
        }