import uvicorn
from fastapi import FastAPI, Depends
import torch

from config import settings
from services.download_html import download_main
from services.document_processor import convert_html_to_markdown
from services.vector_service import build_or_load_vector_store
from utils.model_loader import download_model
from controllers.sql_controller import router as sql_router
from utils.dependencies import get_chatbot_instance, init_dependencies
from controllers.chatbot_controller import router as chatbot_router


async def startup_event():
    # print("Starting up the application...")
    # print("Downloading html...")
    # download_main()

    # print(f"Checking for HTML to Markdown conversion...")
    # convert_html_to_markdown(base_html_docs_path=settings.HTML_DOCS_PATH, output_base_path=settings.MARKDOWN_DOCS_PATH)

    print(f"Building/Loading vector store from {settings.MARKDOWN_DOCS_PATH} to {settings.VECTOR_STORE_PATH}...")
    vector_index = build_or_load_vector_store(
        docs_base_dir=settings.MARKDOWN_DOCS_PATH,
        vector_store_persist_dir=settings.VECTOR_STORE_PATH,
        embedding_model_name=settings.EMBEDDING_MODEL_NAME
    )

    print(f"Ensuring LLM model ({settings.LLM_MODEL_NAME}) is available at {settings.MODEL_SAVE_PATH}...")
    download_model(model_name=settings.LLM_MODEL_NAME, save_path=settings.MODEL_SAVE_PATH)
    
    print("Initializing application dependencies (ChatBot, QueryEngine, SQLProcessor)...")
    init_dependencies(vector_index=vector_index, app_settings=settings)
    print("Application startup complete.")

app = FastAPI(
    title=settings.API_TITLE,
    description="API para interação com o modelo Qwen-2.5, reestruturado em MVC e otimizado.",
    version=settings.API_VERSION,
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json"
)

app.add_event_handler("startup", startup_event)

app.include_router(chatbot_router, prefix="/api/v1", tags=["Chatbot"])
app.include_router(sql_router, prefix="/api/v1", tags=["SQL"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "message": "Chatbot API is running."}

if __name__ == "__main__":
    print(f"Starting Uvicorn server on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        "main:app",
        host=settings.API_HOST, 
        port=settings.API_PORT, 
        reload=settings.RELOAD_UVICORN
    )