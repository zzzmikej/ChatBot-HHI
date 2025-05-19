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

