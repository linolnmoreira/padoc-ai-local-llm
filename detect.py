from ultralytics import YOLO
import os

class PadocVision:

    def __init__(self):
        # Certifique-se de que 'padoc_model.pt' existe ou use um modelo pré-treinado
        model_path = "padoc_model.pt"
        if not os.path.exists(model_path):
            print(f"Aviso: Modelo '{model_path}' não encontrado. Usando 'yolov8n.pt' como fallback.")
            # Baixa o modelo nano se não encontrar o modelo treinado
            self.modelo = YOLO("yolov8n.pt")
        else:
            self.modelo = YOLO(model_path)

    def analisar(self, img_path):
        if not os.path.exists(img_path):
            return [f"Erro: Imagem não encontrada em {img_path}"]

        resultado = self.modelo(img_path)

        objetos = []
        for r in resultado:
            for box in r.boxes:
                classe = int(box.cls[0])
                objetos.append(
                    self.modelo.names[classe]
                )
        return objetos