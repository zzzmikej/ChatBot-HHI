from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from app.models.sql_processor_model import SQLProcessor
from app.views.schemas import (
    SQLGenerateRequest, SQLGenerateResponse,
    SQLAlterRequest, SQLAlterResponse,
    SQLValidateRequest, SQLValidateResponse
)
from app.utils.dependencies import get_sql_processor

router = APIRouter(prefix="/sql", tags=["SQL"])

@router.post("/generate", response_model=SQLGenerateResponse)
async def generate_sql(request: SQLGenerateRequest, sql_processor: SQLProcessor = Depends(get_sql_processor)):
    try:
        response = await sql_processor.generate_sql(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar SQL: {str(e)}")

@router.post("/alter", response_model=SQLAlterResponse)
async def alter_sql(request: SQLAlterRequest, sql_processor: SQLProcessor = Depends(get_sql_processor)):
    try:
        response = await sql_processor.alter_sql(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao alterar SQL: {str(e)}")

@router.post("/validate", response_model=SQLValidateResponse)
async def validate_sql(request: SQLValidateRequest, sql_processor: SQLProcessor = Depends(get_sql_processor)):
    try:
        response = await sql_processor.validate_sql(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao validar SQL: {str(e)}")