from llama_index.core import VectorStoreIndex

class QueryEngine:
    def __init__(self, index: VectorStoreIndex, llm=None): # Added default llm=None for now
        self.index = index
        self.llm = llm

    def query(self, user_input: str) -> str:
        # llm parameter might be passed from config or ChatBot initialization
        query_engine = self.index.as_query_engine(llm=self.llm, similarity_top_k=2) # similarity_top_k could be configurable
        response = query_engine.query(user_input)
        return str(response)

