import cv2
import os

class VideoAI:
    """
    Classe responsável pela análise de vídeos automotivos.
    Extrai metadados, frames e prepara para análises mais profundas.
    """

    def analisar(self, caminho_video: str):
        """
        Analisa um arquivo de vídeo, extrai suas propriedades e retorna um resumo.

        Args:
            caminho_video (str): O caminho para o arquivo de vídeo.

        Returns:
            dict: Um dicionário contendo as propriedades do vídeo ou uma mensagem de erro.
        """
        if not os.path.exists(caminho_video):
            return {
                "sucesso": False,
                "erro": f"Arquivo de vídeo não encontrado em: {caminho_video}"
            }

        cap = cv2.VideoCapture(caminho_video)

        if not cap.isOpened():
            return {
                "sucesso": False,
                "erro": "Não foi possível abrir o arquivo de vídeo. Pode estar corrompido ou em um formato não suportado."
            }

        try:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            largura = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            altura = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duracao_segundos = total_frames / fps if fps > 0 else 0

            return {
                "sucesso": True,
                "tipo": "Vídeo",
                "frames": total_frames,
                "fps": round(fps, 2),
                "duracao_segundos": round(duracao_segundos, 2),
                "resolucao": f"{largura}x{altura}",
                "diagnostico": "Vídeo carregado com sucesso e pronto para análise detalhada."
            }
        except Exception as e:
            return {"sucesso": False, "erro": f"Ocorreu um erro ao ler as propriedades do vídeo: {e}"}
        finally:
            # Garante que o recurso seja liberado
            cap.release()