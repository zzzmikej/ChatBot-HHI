import uvicorn
from fastapi import FastAPI, Depends

from config import settings
from services.download_html import download_main
from services.document_processor import convert_html_to_markdown
from utils.model_loader import download_model



async def startup_event():
    print("Starting up the application...")
    print("Downloading html...")
    download_main()

    print(f"Checking for HTML to Markdown conversion...")
    convert_html_to_markdown(base_html_docs_path=settings.HTML_DOCS_PATH, output_base_path=settings.MARKDOWN_DOCS_PATH)

    print(f"Ensuring LLM model ({settings.LLM_MODEL_NAME}) is available at {settings.MODEL_SAVE_PATH}...")
    download_model(model_name=settings.LLM_MODEL_NAME, save_path=settings.MODEL_SAVE_PATH)
    
app = FastAPI(
    title=settings.API_TITLE,
    description="API para interação com o modelo Qwen-2.5, reestruturado em MVC e otimizado.",
    version=settings.API_VERSION,
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json"
)

app.add_event_handler("startup", startup_event)

# app.include_router(chatbot_router, prefix="/api/v1", tags=["Chatbot"])

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
