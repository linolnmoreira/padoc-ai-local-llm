from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM
)

class PadocLLM:

    def __init__(self):
        modelo = "mistralai/Mistral-7B-Instruct-v0.2"
        self.tokenizer = AutoTokenizer.from_pretrained(modelo)
        self.model = AutoModelForCausalLM.from_pretrained(
            modelo,
            device_map="auto"
        )

    def responder(
        self,
        conhecimento,
        pergunta
    ):
        prompt = f"""
Você é PADOC AI.
Especialista em:
- motores
- elétrica
- injeção
- transmissão
- diagnóstico OBD2
- manutenção

Base técnica:
{conhecimento}

Motorista:
{pergunta}

Resposta:
"""
        entrada = self.tokenizer(
            prompt,
            return_tensors="pt"
        ).to(self.model.device)

        saida = self.model.generate(
            **entrada,
            max_new_tokens=500
        )

        return self.tokenizer.decode(saida[0], skip_special_tokens=True)