import cv2

class ImageAI:

    def analisar(self, imagem):

        img = cv2.imread(imagem)

        if img is None:
            return {"erro":"Imagem não encontrada"}

        altura, largura = img.shape[:2]

        return {
            "tipo":"Imagem",
            "largura":largura,
            "altura":altura,
            "diagnostico":"Imagem carregada com sucesso."
        }