# Chatbot HHI - Reestruturado e Otimizado

Este projeto implementa um chatbot utilizando FastAPI, modelos de linguagem da Hugging Face (Qwen2.5-1.5B), e LlamaIndex para busca em documentos. O projeto original foi reestruturado para uma arquitetura Model-View-Controller (MVC) e otimizado para melhor desempenho e manutenibilidade.

## Estrutura do Projeto MVC

O projeto está organizado da seguinte forma dentro do diretório `ChatBot-HHI/`:

```
ChatBot-HHI/
├── app/                     # Contém o código principal da aplicação
│   ├── controllers/         # Controladores FastAPI (endpoints da API)
│   │   └── chatbot_controller.py
│   ├── models/              # Lógica de negócio, modelos de ML, interação com LLM
│   │   ├── chatbot_model.py
│   │   └── query_engine_model.py
│   ├── services/            # Serviços (processamento de documentos, construção de vetores)
│   │   ├── document_processor.py
│   │   └── vector_service.py
│   ├── utils/               # Funções utilitárias e gerenciamento de dependências
│   │   ├── dependencies.py
│   │   └── model_loader.py
│   ├── views/               # Schemas Pydantic para requisições e respostas
│   │   └── schemas.py
│   ├── config.py            # Configurações da aplicação (paths, modelos, etc.)
│   └── main.py              # Ponto de entrada da aplicação FastAPI
├── data/
│   ├── vectorstore/         # Diretório onde o índice vetorial é persistido
│   └── markdown_docs/       # (Opcional) Onde os documentos markdown processados podem ser armazenados
├── models/                  # Diretório onde os modelos LLM baixados são armazenados
│   └── qwen-2.5/
├── logs/                    # Arquivos de log (se configurado)
│   └── app.log
├── requirements.txt         # Dependências Python do projeto
├── README.md                # Este arquivo
└── .env.example             # Arquivo de exemplo para variáveis de ambiente
```

**Observação:** O diretório `data/markdown_docs/` é populado pelo `document_processor.py` se você estiver convertendo HTML para Markdown. O `vector_service.py` utiliza o `settings.MARKDOWN_DOCS_PATH` (configurado em `app/config.py` e potencialmente via `.env`) como fonte para construir o `vectorstore`.
No projeto original, os documentos markdown estavam em `/home/ubuntu/chatbot_project/docling_output`. Certifique-se que `MARKDOWN_DOCS_PATH` em `app/config.py` ou no seu arquivo `.env` aponte para o local correto dos seus documentos fonte.

## Configuração

1.  **Variáveis de Ambiente (Opcional mas Recomendado):**
    Crie um arquivo `.env` na raiz do diretório `ChatBot-HHI/` (ao lado de `requirements.txt`) baseado no `.env.example` (que você precisará criar ou que eu posso fornecer um exemplo abaixo). Este arquivo permite sobrescrever as configurações padrão definidas em `app/config.py`.

    Exemplo de `.env.example`:
    ```env
    # Caminhos (ajuste conforme necessário)
    # MARKDOWN_DOCS_PATH="/caminho/para/seus/documentos/markdown"
    # VECTOR_STORE_PATH="/caminho/para/seu/vectorstore"
    # MODEL_SAVE_PATH="/caminho/para/salvar/modelos/llm"

    # Configuração do Modelo
    # LLM_MODEL_NAME="Qwen/Qwen2.5-1.5B"
    # EMBEDDING_MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
    DEVICE="cpu"  # Mude para "cuda" se tiver GPU compatível e configurada
    # MODEL_TORCH_DTYPE="torch.float16"

    # Parâmetros de Geração
    # MAX_NEW_TOKENS=150
    # TEMPERATURE=0.7
    # SIMILARITY_TOP_K=3

    # Configuração da API
    # API_HOST="0.0.0.0"
    # API_PORT=8000
    # RELOAD_UVICORN=True
    ```
    As configurações padrão em `app/config.py` já apontam para os diretórios dentro da estrutura do projeto (`/home/ubuntu/ChatBot-HHI/data/vectorstore` e `/home/ubuntu/ChatBot-HHI/models/qwen-2.5`). O `MARKDOWN_DOCS_PATH` está configurado para `/home/ubuntu/chatbot_project/docling_output` (do seu ZIP original).

2.  **Instalar Dependências:**
    Navegue até o diretório `ChatBot-HHI/` e instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Execução

1.  **Fonte de Documentos:**
    Certifique-se de que os documentos Markdown que você deseja que o chatbot use como base de conhecimento estejam no diretório especificado por `MARKDOWN_DOCS_PATH` em `app/config.py` (ou no seu `.env`). No seu caso, o padrão é `/home/ubuntu/chatbot_project/docling_output`.

2.  **Iniciar a Aplicação:**
    No diretório `ChatBot-HHI/`, execute o `main.py` que está dentro da pasta `app`:
    ```bash
    python -m app.main
    ```
    Ou, se você estiver no diretório `ChatBot-HHI/app/`:
    ```bash
    python main.py
    ```

    A aplicação FastAPI será iniciada. Durante a inicialização:
    *   O modelo LLM (Qwen2.5-1.5B) será baixado para `ChatBot-HHI/models/qwen-2.5` se ainda não existir.
    *   O índice vetorial (vector store) será construído a partir dos documentos em `MARKDOWN_DOCS_PATH` e salvo em `ChatBot-HHI/data/vectorstore/` se ainda não existir. Se já existir, será carregado.

3.  **Acessar a API:**
    *   **Saúde da API:** `http://localhost:8000/health` (ou o host/porta que você configurou)
    *   **Endpoint do Chatbot:** `POST http://localhost:8000/api/v1/ask`
        Corpo da requisição (JSON):
        ```json
        {
            "question": "Qual é a sua pergunta?"
        }
        ```
    *   **Documentação da API (Swagger UI):** `http://localhost:8000/api/1.1.0/openapi.json` (acesse via navegador para ver a interface Swagger ou use um cliente API).

## Principais Melhorias Implementadas

*   **Arquitetura MVC:** Código reorganizado para melhor separação de responsabilidades, facilitando a manutenção e escalabilidade.
    *   `Controllers`: Gerenciam as requisições HTTP e respostas.
    *   `Models`: Contêm a lógica de negócio principal, incluindo a interação com o modelo de linguagem e o motor de busca vetorial.
    *   `Views`: Definem os schemas de dados para as requisições e respostas da API (usando Pydantic).
    *   `Services`: Encapsulam lógicas específicas como processamento de documentos e gerenciamento do vector store.
    *   `Utils`: Funções auxiliares e gerenciamento de dependências.
    *   `Config`: Configuração centralizada e flexível (via `config.py` e `.env`).
*   **Otimização de Desempenho:**
    *   **Uso de GPU Configurável:** O dispositivo (`cpu` ou `cuda`) pode ser definido nas configurações. O modelo será carregado no dispositivo especificado.
    *   **Operações Assíncronas:** A inferência do modelo (operação mais pesada) é executada em um threadpool (`fastapi.concurrency.run_in_threadpool`) para não bloquear o loop de eventos principal da API, melhorando a concorrência.
    *   **Carregamento Eficiente:** Modelos e vector store são carregados/construídos na inicialização da aplicação para evitar atrasos na primeira requisição.
*   **Qualidade das Respostas:**
    *   **Prompt Engineering Revisado:** O prompt enviado ao modelo foi aprimorado para fornecer instruções mais claras e obter respostas mais precisas e contextuais.
    *   **Parâmetros de Geração Ajustáveis:** Parâmetros como `max_new_tokens`, `temperature`, `top_p` e `similarity_top_k` são configuráveis, permitindo um ajuste fino da qualidade e estilo das respostas.
*   **Manutenibilidade e Robustez:**
    *   **Configuração Centralizada:** Facilita a alteração de parâmetros importantes sem modificar o código.
    *   **Gerenciamento de Dependências:** Uso do sistema de injeção de dependências do FastAPI.
    *   **Tratamento de Erros:** Melhorias no tratamento de exceções nos endpoints.

## Considerações Adicionais

*   **Processamento de Documentos (`docling`):** A biblioteca `docling` mencionada no código original para converter HTML para Markdown não é uma biblioteca Python padrão. Se for uma ferramenta customizada ou interna, você precisará garantir que ela esteja disponível e funcional no ambiente para que `app/services/document_processor.py` funcione como esperado. A versão atual do `document_processor.py` inclui um mock dessa funcionalidade se a biblioteca não estiver presente. Se os seus documentos já estão em Markdown, você pode ignorar esta parte, garantindo que `MARKDOWN_DOCS_PATH` aponte para eles.
*   **Recursos:** Modelos de linguagem grandes como o Qwen2.5-1.5B consomem bastante memória RAM, mesmo em CPU. Se estiver usando GPU, certifique-se de ter VRAM suficiente.
*   **Primeira Execução:** A primeira execução pode ser mais demorada devido ao download do modelo e à construção do índice vetorial.