"""
PADOC AI - Wrapper para o Modelo de Linguagem Local (LLM)
"""
import os

class PadocLLM:
    """
    Classe que carrega e interage com o modelo de linguagem local (GGUF).
    """
    def __init__(self):
        """
        Inicializa e carrega o modelo LLM.
        """
        # Resolve o caminho do modelo dinamicamente
        base_path = os.path.dirname(os.path.abspath(__file__))
        # O modelo está em 'brain/models', então subimos dois níveis e entramos no caminho certo
        model_path = os.path.normpath(os.path.join(base_path, "..", "brain", "models", "padoc-model.gguf"))

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo GGUF não encontrado em: {model_path}. Verifique o caminho.")

        try:
            from llama_cpp import Llama
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError("llama_cpp não encontrado. Instale com: pip install llama-cpp-python") from e

        try:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=4096,      # Tamanho do contexto
                n_threads=8,     # Número de threads para usar
                verbose=False    # Suprime logs detalhados do llama.cpp
            )
        except Exception as e:
            raise RuntimeError(f"Erro ao inicializar o motor LLM: {e}") from e

    def responder(self, contexto: str, pergunta: str) -> str:
        """
        Gera uma resposta do LLM com base em um contexto e uma pergunta.

        Args:
            contexto: O contexto de fundo para a IA (histórico, dados OBD, etc.).
            pergunta: A pergunta específica do usuário.

        Returns:
            A resposta gerada pelo modelo.
        """
        prompt_completo = f"""
        {contexto}

        Com base no contexto acima, responda à seguinte pergunta como um mecânico especialista.
        
        Pergunta: {pergunta}

        Resposta:
        """

        try:
            resposta = self.llm(
                prompt_completo,
                max_tokens=500,
                temperature=0.6,
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["Pergunta:", "\n\n"] # Impede que o modelo continue a conversa sozinho
            )

            texto = resposta["choices"][0]["text"].strip()
            return texto
        except Exception as e:
            return f"Erro ao gerar resposta do LLM: {e}"