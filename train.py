from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments
)
import os

modelo = "mistralai/Mistral-7B-Instruct-v0.2"
tokenizer = AutoTokenizer.from_pretrained(modelo)
tokenizer.pad_token = tokenizer.eos_token # Mistral não tem pad_token por padrão

model = AutoModelForCausalLM.from_pretrained(modelo)

dataset = load_dataset(
    "text",
    data_files={"train": "brain/datasets/manuais/*.txt"}
)

def tokenizar(dados):
    return tokenizer(
        dados["text"],
        truncation=True,
        padding="max_length",
        max_length=512
    )

dataset = dataset.map(tokenizar, batched=True)

treino = TrainingArguments(
    output_dir="models/padoc",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    save_steps=100,
    logging_steps=10
)

trainer = Trainer(
    model=model,
    args=treino,
    train_dataset=dataset["train"]
)

if __name__ == "__main__":
    trainer.train()
    model.save_pretrained("models/padoc")
    tokenizer.save_pretrained("models/padoc")