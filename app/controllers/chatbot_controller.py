from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from views.schemas import Question
from models.chatbot_model import ChatBot
from utils.dependencies import get_chatbot
import re
from fastapi.concurrency import run_in_threadpool

router = APIRouter()

@router.post("/ask")
async def ask_question(question_data: Question, chatbot: ChatBot = Depends(get_chatbot)):
    try:
        answer = await run_in_threadpool(chatbot.ask, question_data.question)
        clean_answer = re.sub(r'file_path:.*', '', answer, flags=re.DOTALL)
        return {"answer": clean_answer.strip()}
    except Exception as e:
        print(f"Error during ask_question: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/ping") 
async def ping_router():
    return {"message": "Chatbot controller is active."}