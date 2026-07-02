from ultralytics import YOLO
import os

# Ensure the dataset directory exists
os.makedirs("vision/dataset/images/train", exist_ok=True)
os.makedirs("vision/dataset/images/val", exist_ok=True)
os.makedirs("vision/dataset/labels/train", exist_ok=True)
os.makedirs("vision/dataset/labels/val", exist_ok=True)

modelo = YOLO(
"yolov8n.pt" # Modelo pré-treinado YOLOv8 nano
)

# Para treinar, você precisaria de imagens e anotações reais no diretório 'vision/dataset'
# modelo.train(
# data="vision/dataset.yaml",
# epochs=50,
# imgsz=640
# )
print("Script de treinamento YOLO pronto. Para treinar, descomente as linhas 'modelo.train()' e forneça um dataset válido.")