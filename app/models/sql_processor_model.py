import sqlglot
from typing import List, Tuple, Optional, Any
from app.services.sql_service import (
    validate_syntax_sqlglot,
    validate_semantics,
    format_sql_sqlglot,
    extract_schema_from_markdown,
)
from app.views.schemas import (
    SQLGenerateRequest, SQLGenerateResponse,
    SQLAlterRequest, SQLAlterResponse,
    SQLValidateRequest, SQLValidateResponse,
    SQLValidationDetail
)
from app.config import settings
from app.models.chatbot_model import ChatBot

class LLMClient:
    def __init__(self, chatbot: ChatBot):
        self.chatbot = chatbot
        print(f"LLM Client Initialized with ChatBot model")

    def generate_sql_from_prompt(self, prompt: str, dialect: str, db_schema_context: str | None = None) -> str:
        context_info = ""
        if db_schema_context:
            context_info = f"\nEsquema do banco de dados:\n{db_schema_context}\n\n"
            
        final_prompt = (
            f"Você é um especialista em SQL. Gere um script SQL válido para o dialeto {dialect} "
            f"com base na seguinte descrição:\n\n{prompt}\n\n"
            f"{context_info}"
            f"Retorne apenas o código SQL sem explicações adicionais."
        )
        
        generated_sql = self.chatbot.ask(final_prompt)
        
        import re
        sql_code_pattern = r"```sql\s*([\s\S]*?)\s*```"
        sql_matches = re.findall(sql_code_pattern, generated_sql)
        
        if sql_matches:
            return sql_matches[0].strip()
        else:
            lines = generated_sql.split('\n')
            sql_lines = []
            for line in lines:
                if not line.startswith(('Aqui', 'Este', 'Esse', 'O script', 'Note', 'Obs', '#')) and line.strip():
                    sql_lines.append(line)
            
            return '\n'.join(sql_lines).strip()
        
    def alter_sql_from_prompt(self, original_sql: str, alter_prompt: str, dialect: str, db_schema_context: str | None = None) -> str:
        context_info = ""
        if db_schema_context:
            context_info = f"\nEsquema do banco de dados:\n{db_schema_context}\n\n"
            
        final_prompt = (
            f"Você é um especialista em SQL. Modifique o seguinte script SQL para o dialeto {dialect} "
            f"de acordo com as instruções fornecidas:\n\n"
            f"SQL Original:\n```sql\n{original_sql}\n```\n\n"
            f"Instruções para alteração:\n{alter_prompt}\n\n"
            f"{context_info}"
            f"Retorne apenas o código SQL alterado sem explicações adicionais."
        )
        
        altered_sql = self.chatbot.ask(final_prompt)
        
        import re
        sql_code_pattern = r"```sql\s*([\s\S]*?)\s*```"
        sql_matches = re.findall(sql_code_pattern, altered_sql)
        
        if sql_matches:
            return sql_matches[0].strip()
        else:
            lines = altered_sql.split('\n')
            sql_lines = []
            for line in lines:
                if not line.startswith(('Aqui', 'Este', 'Esse', 'O script', 'Note', 'Obs', '#')) and line.strip():
                    sql_lines.append(line)
            
            return '\n'.join(sql_lines).strip()
        
llm_client = None

class SQLProcessor:
    def __init__(self, chatbot: Optional[ChatBot] = None):
        self.db_schema = extract_schema_from_markdown(
            docs_base_dir=getattr(settings, "MARKDOWN_DOCS_PATH", "./data/markdown_docs")
        )
        
        global llm_client
        if chatbot:
            llm_client = LLMClient(chatbot)
        
        self.llm_client = llm_client

    async def generate_sql(self, request: SQLGenerateRequest) -> SQLGenerateResponse:
        try:
            if not self.llm_client:
                return SQLGenerateResponse(
                    success=False,
                    message="Erro: Cliente LLM não inicializado. Verifique a configuração do modelo de IA.",
                    generated_sql="",
                    formatted_sql=None,
                    validation_errors=[SQLValidationDetail(type="system", message="Cliente LLM não inicializado")]
                )
            
            schema_context_str = str(self.db_schema) if self.db_schema else None
            raw_sql = self.llm_client.generate_sql_from_prompt(request.prompt, request.dialect, schema_context_str)

            is_syntax_valid, parsed_expr, syntax_error = validate_syntax_sqlglot(raw_sql, request.dialect)
            
            validation_details = [SQLValidationDetail(type="syntax", message=syntax_error or "Sintaxe OK")]

            is_semantic_valid = True  # Assume verdadeiro se não for verificado
            semantic_errors_list: list[str] = []
            if is_syntax_valid and parsed_expr and request.perform_semantic_validation:
                is_semantic_valid, semantic_errors_list = validate_semantics(parsed_expr, self.db_schema, request.dialect)
                for err in semantic_errors_list:
                    validation_details.append(SQLValidationDetail(type="semantic", message=err))
            
            formatted_sql = None
            if is_syntax_valid:
                formatted_sql = format_sql_sqlglot(raw_sql, request.dialect, pretty=True)

            success = is_syntax_valid and is_semantic_valid
            message = "SQL gerado e validado com sucesso." if success else "SQL gerado com problemas de validação."
            if not is_syntax_valid: 
                message = f"Falha na validação de sintaxe do SQL gerado: {syntax_error}"

            return SQLGenerateResponse(
                success=success,
                message=message,
                generated_sql=raw_sql,
                formatted_sql=formatted_sql,
                validation_errors=validation_details if (not is_syntax_valid or semantic_errors_list) else []
            )
        except Exception as e:
            return SQLGenerateResponse(
                success=False, 
                message=f"Erro ao gerar SQL: {str(e)}",
                generated_sql="",
                formatted_sql=None,
                validation_errors=[SQLValidationDetail(type="system", message=f"Erro: {str(e)}")]
            )

    async def alter_sql(self, request: SQLAlterRequest) -> SQLAlterResponse:
        try:
            if not self.llm_client:
                return SQLAlterResponse(
                    success=False,
                    message="Erro: Cliente LLM não inicializado. Verifique a configuração do modelo de IA.",
                    generated_sql="",
                    formatted_sql=None,
                    validation_errors=[SQLValidationDetail(type="system", message="Cliente LLM não inicializado")]
                )
            
            schema_context_str = str(self.db_schema) if self.db_schema else None
            altered_sql = self.llm_client.alter_sql_from_prompt(
                request.original_sql, request.alter_prompt, request.dialect, schema_context_str
            )

            is_syntax_valid, parsed_expr, syntax_error = validate_syntax_sqlglot(altered_sql, request.dialect)
            validation_details = [SQLValidationDetail(type="syntax", message=syntax_error or "Sintaxe OK")]

            is_semantic_valid = True
            semantic_errors_list: list[str] = []
            if is_syntax_valid and parsed_expr and request.perform_semantic_validation:
                is_semantic_valid, semantic_errors_list = validate_semantics(parsed_expr, self.db_schema, request.dialect)
                for err in semantic_errors_list:
                    validation_details.append(SQLValidationDetail(type="semantic", message=err))

            formatted_sql = None
            if is_syntax_valid:
                formatted_sql = format_sql_sqlglot(altered_sql, request.dialect, pretty=True)
            
            success = is_syntax_valid and is_semantic_valid
            message = "SQL alterado e validado com sucesso." if success else "SQL alterado com problemas de validação."
            if not is_syntax_valid: 
                message = f"Falha na validação de sintaxe do SQL alterado: {syntax_error}"

            return SQLAlterResponse(
                success=success,
                message=message,
                generated_sql=altered_sql,
                formatted_sql=formatted_sql,
                validation_errors=validation_details if (not is_syntax_valid or semantic_errors_list) else []
            )
        except Exception as e:
            return SQLAlterResponse(
                success=False, 
                message=f"Erro ao alterar SQL: {str(e)}",
                generated_sql="",
                formatted_sql=None,
                validation_errors=[SQLValidationDetail(type="system", message=f"Erro: {str(e)}")]
            )

    async def validate_sql(self, request: SQLValidateRequest) -> SQLValidateResponse:
        try:
            is_syntax_valid, parsed_expr, syntax_error = validate_syntax_sqlglot(request.sql_script, request.dialect)

            is_semantic_valid = True  # Padrão para verdadeiro se não for realizado
            semantic_errors_list: list[str] = []
            if is_syntax_valid and parsed_expr and request.perform_semantic_validation:
                is_semantic_valid, semantic_errors_list = validate_semantics(parsed_expr, self.db_schema, request.dialect)
            
            formatted_sql = None
            if is_syntax_valid:
                formatted_sql = format_sql_sqlglot(request.sql_script, request.dialect, pretty=True)

            return SQLValidateResponse(
                is_syntactically_valid=is_syntax_valid,
                syntax_error_message=syntax_error,
                is_semantically_valid=is_semantic_valid,
                semantic_error_messages=semantic_errors_list,
                formatted_sql=formatted_sql
            )
        except Exception as e:
            return SQLValidateResponse(
                is_syntactically_valid=False,  # Marca como inválido se o processo falhar
                syntax_error_message=f"Erro durante o processo de validação: {str(e)}",
                is_semantically_valid=False,
                semantic_error_messages=[f"Erro durante o processo de validação: {str(e)}"]
            )