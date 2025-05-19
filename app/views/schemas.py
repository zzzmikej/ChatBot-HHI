from pydantic import BaseModel
from typing import List, Optional

class Question(BaseModel):
    question: str

class SQLValidationDetail(BaseModel):
    type: str  # e.g., "syntax", "semantic"
    message: str

class SQLGenerateRequest(BaseModel):
    prompt: str
    dialect: str = "sqlserver"
    perform_semantic_validation: bool = True

class SQLGenerateResponse(BaseModel):
    success: bool
    message: str
    generated_sql: Optional[str] = None
    formatted_sql: Optional[str] = None
    validation_errors: List[SQLValidationDetail] = []

class SQLAlterRequest(BaseModel):
    original_sql: str
    alter_prompt: str
    dialect: str = "sqlserver"
    perform_semantic_validation: bool = True

class SQLAlterResponse(BaseModel):
    success: bool
    message: str
    generated_sql: Optional[str] = None
    formatted_sql: Optional[str] = None
    validation_errors: List[SQLValidationDetail] = []

class SQLValidateRequest(BaseModel):
    sql_script: str
    dialect: str = "sqlserver"
    perform_semantic_validation: bool = True

class SQLValidateResponse(BaseModel):
    is_syntactically_valid: bool
    syntax_error_message: Optional[str] = None
    is_semantically_valid: bool
    semantic_error_messages: List[str] = []
    formatted_sql: Optional[str] = None
