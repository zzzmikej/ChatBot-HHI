import uvicorn
from fastapi import FastAPI, Depends
from config import settings
from services.download_html import download_main

async def startup_event():
    print("Starting up the application...")
    print("Downloading html...")
    download_main()

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
