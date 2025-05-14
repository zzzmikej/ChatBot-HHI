import os
from llama_index.core import (
    VectorStoreIndex, 
    SimpleDirectoryReader, 
    Settings, 
    StorageContext, 
    load_index_from_storage
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def build_or_load_vector_store(docs_base_dir: str, vector_store_persist_dir: str, embedding_model_name: str) -> VectorStoreIndex:

    print(f"Attempting to build/load vector store. Docs: {docs_base_dir}, Store: {vector_store_persist_dir}")

    embed_model = HuggingFaceEmbedding(model_name=embedding_model_name)
    Settings.llm = None
    Settings.embed_model = embed_model
    print(f"LlamaIndex Settings configured: LLM is {'None' if Settings.llm is None else 'Set'}, Embed Model is {Settings.embed_model.model_name}")

    if os.path.exists(vector_store_persist_dir) and os.listdir(vector_store_persist_dir):
        print(f"Loading existing vector store from: {vector_store_persist_dir}")
        try:
            storage_context = StorageContext.from_defaults(persist_dir=vector_store_persist_dir)
            index = load_index_from_storage(storage_context)
            print("Successfully loaded vector store from storage.")
            return index
        except Exception as e:
            print(f"Error loading from storage, will attempt to rebuild: {e}")

    print(f"No valid existing vector store found or error loading. Building new one from: {docs_base_dir}")
    space_keys = [
        "ags", "API", "CM", "CME", "CMSup", "CMSupE", "CRS", "CST",
        "EMS", "HE", "HEYC", "Hstays", "hpn", "MAN", "OMS", "OPA",
        "PDP", "PDOC", "PMS", "pneng", "pnsup", "POS", "WIKI", "WSS"
    ]

    all_documents = []
    for key in space_keys:
        input_dir = os.path.join(docs_base_dir, key)
        if not os.path.exists(input_dir):
            print(f"Document subdirectory not found, skipping: {input_dir}")
            continue
        
        print(f"Loading documents from: {input_dir}")
        if not any(os.path.isfile(os.path.join(input_dir, f)) for f in os.listdir(input_dir)):
            print(f"No files found in {input_dir}, skipping.")
            continue
            
        try:
            documents = SimpleDirectoryReader(input_dir).load_data()
            all_documents.extend(documents)
            print(f"Loaded {len(documents)} documents from {input_dir}.")
        except Exception as e:
            print(f"Error loading documents from {input_dir}: {e}")

    if not all_documents:
        raise ValueError(f"No documents found in any subdirectories of {docs_base_dir}. Cannot build vector store.")

    print(f"Total documents loaded: {len(all_documents)}. Building index...")

    index = VectorStoreIndex.from_documents(all_documents)

    print(f"Vector store index created. Persisting to: {vector_store_persist_dir}")
    if not os.path.exists(vector_store_persist_dir):
        os.makedirs(vector_store_persist_dir)
    index.storage_context.persist(persist_dir=vector_store_persist_dir)
    print("Vector store persisted successfully.")
    return index