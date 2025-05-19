from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
from models.query_engine_model import QueryEngine

class ChatBot:
    def __init__(self, 
                 query_engine: QueryEngine,
                 model_path: str,
                 tokenizer_path: str,
                 device: str,
                 model_torch_dtype: torch.dtype,
                 max_new_tokens: int,
                 temperature: float):
        
        print(f"Initializing ChatBot model from: {model_path} on device: {device}")
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=model_torch_dtype,
            device_map=device if device != "cpu" else None,
        )
        if device == "cpu" and (not hasattr(self.model, 'hf_device_map') or not self.model.hf_device_map):
             self.model.to(torch.device("cpu"))

        self.query_engine = query_engine
        self.device = device
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        print(f"ChatBot initialized. Tokenizer: {tokenizer_path}, Model: {model_path}, Device: {self.model.device}")

    def ask(self, prompt: str) -> str:
        context = self.query_engine.query(prompt)
        final_prompt = (
            f"Você é um assistente prestativo. Use o seguinte contexto para responder à pergunta no final. "
            f"Se a resposta não estiver no contexto, diga que você não sabe, não tente inventar uma resposta.\n\n"
            f"Contexto Fornecido:\n{context}\n\n"
            f"Pergunta do Usuário:\n{prompt}\n\n"
            f"Resposta Assistente:"
        )
        
        inputs = self.tokenizer(final_prompt, return_tensors="pt", truncation=True, max_length=1024).to(self.model.device) # Use model.device
        
        self.model.eval()
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=True,
                temperature=self.temperature,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )

        answer = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return answer.strip()