from __future__ import annotations

from models.chatbot_model import ChatBot
from models.query_engine_model import QueryEngine
from config import settings
from llama_index.core import VectorStoreIndex
import torch

_chatbot_instance: ChatBot | None = None
_query_engine_instance: QueryEngine | None = None
_vector_index_instance: VectorStoreIndex | None = None

def init_dependencies(vector_index: VectorStoreIndex, app_settings: type(settings)):
    global _query_engine_instance, _chatbot_instance, _vector_index_instance
    print("Initializing QueryEngine and ChatBot instances...")

    _vector_index_instance = vector_index

    _query_engine_instance = QueryEngine(index=_vector_index_instance, llm=None)
    print("QueryEngine instance initialized.")

    torch_dtype = torch.float16
    if app_settings.MODEL_TORCH_DTYPE == "torch.float32":
        torch_dtype = torch.float32

    _chatbot_instance = ChatBot(
        query_engine=_query_engine_instance,
        model_path=app_settings.MODEL_SAVE_PATH,
        device=app_settings.DEVICE,
        tokenizer_path=app_settings.MODEL_SAVE_PATH,
        model_torch_dtype=torch_dtype,
        max_new_tokens=app_settings.MAX_NEW_TOKENS,
        temperature=app_settings.TEMPERATURE
    )
    print("ChatBot instance initialized.")

def get_chatbot() -> ChatBot:
    if _chatbot_instance is None:
        raise RuntimeError("ChatBot instance has not been initialized. Ensure startup event is configured and ran successfully.")
    return _chatbot_instance

def get_query_engine() -> QueryEngine:
    if _query_engine_instance is None:
        raise RuntimeError("QueryEngine instance has not been initialized.")
    return _query_engine_instance

def get_vector_index() -> VectorStoreIndex:
    if _vector_index_instance is None:
        raise RuntimeError("VectorStoreIndex instance has not been initialized.")
    return _vector_index_instance


def get_chatbot_instance():
    return _chatbot_instance