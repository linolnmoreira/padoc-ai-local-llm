from ultralytics import YOLO
import os


class PadocVision:


    def __init__(self):
        print("Carregando modelo de visão YOLOv8n...")
        # Certifique-se de que 'yolov8n.pt' está disponível ou será baixado
        self.modelo = YOLO("yolov8n.pt")
        print("Modelo de visão carregado.")


    def analisar(
    self,
    imagem_path
    ):
        if not os.path.exists(imagem_path):
            return [f"Erro: Imagem não encontrada em {imagem_path}"]

        resultado = self.modelo(imagem_path)

        objetos = []
        for r in resultado:
            for box in r.boxes:
                nome = self.modelo.names[int(box.cls[0])]
                objetos.append(nome)
        return objetos