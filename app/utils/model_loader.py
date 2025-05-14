from transformers import AutoModelForCausalLM, AutoTokenizer
import os

def download_model(model_name: str, save_path: str):
    config_path = os.path.join(save_path, "config.json")
    if not os.path.exists(save_path) or not os.path.exists(config_path):
        print(f"Model not found at {save_path}. Downloading {model_name}...")
        os.makedirs(save_path, exist_ok=True)
        AutoModelForCausalLM.from_pretrained(model_name).save_pretrained(save_path)
        AutoTokenizer.from_pretrained(model_name).save_pretrained(save_path)
        print(f"Model downloaded and saved to {save_path}")
    else:
        print(f"Model already exists at {save_path}")