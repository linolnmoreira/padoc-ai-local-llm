from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class PadocLLM:
    def __init__(self):
        modelo = "mistralai/Mistral-7B-Instruct-v0.2"
        
        self.tokenizer = AutoTokenizer.from_pretrained(modelo)
        # Utiliza device_map="auto" para carregar partes do modelo na GPU se disponível
        self.model = AutoModelForCausalLM.from_pretrained(
            modelo,
            device_map="auto",
            torch_dtype=torch.float16 # Otimização de memória
        )

    def responder(self, contexto, pergunta):
        prompt = f"""
Você é PADOC AI.
Especialista em:
- mecânica
- elétrica automotiva
- diagnóstico
- OBD2
- manutenção preventiva

Conhecimento:
{contexto}

Pergunta:
{pergunta}

Resposta técnica:
"""
        entrada = self.tokenizer(
            prompt,
            return_tensors="pt"
        ).to(self.model.device)

        saida = self.model.generate(
            **entrada,
            max_new_tokens=400,
            temperature=0.7,
            do_sample=True
        )

        # Decodifica removendo o prompt inicial para retornar apenas a resposta
        resposta_completa = self.tokenizer.decode(saida[0], skip_special_tokens=True)
        resposta_limpa = resposta_completa.split("Resposta técnica:")[-1].strip()
        
        return resposta_limpa