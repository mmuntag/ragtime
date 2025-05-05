import os

from llama_index.embeddings.openai import OpenAIEmbedding
#from llama_index.embeddings.ollama import OllamaEmbedding
#from llama_index.embeddings.mistralai import MistralAIEmbedding

from llama_index.llms.openai import OpenAI
#from llama_index.llms.ollama import Ollama

def load_embedder(embed_model):
    service, model_name = embed_model.split("|")
    if service == "OLLAMA":
        return OllamaEmbedding(
            model_name=model_name,
            base_url=os.environ["LLAMAINDEX_OLLAMA_BASE_URL"],
        )
    elif service == "OPENAI":
        return OpenAIEmbedding(
            api_key=os.environ["OPENAI_API_KEY"],
            model=model_name,
            dimensions=1024
        )
    else:
        raise ValueError(f"Unknown embedding service: {service}")

def load_llm(llm, base_prompt):
    service, model_name = llm.split("|")
    if service == "OLLAMA":
        return Ollama(
            model=model_name,
            base_url=os.environ["LLAMAINDEX_OLLAMA_BASE_URL"],
            system_prompt=base_prompt,
            temperature=0.5,
            request_timeout=120,
            context_window=16384,
        )
    elif service == "OPENAI":
        return OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            model=model_name,
            messages=[
                {"role": "system", "content": base_prompt}
            ],
            temperature=0.5,
            timeout=120,
            max_tokens=4096
         )
    else:
        raise ValueError(f"Unknown llm: {service}")