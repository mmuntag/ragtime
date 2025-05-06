import os
import json
import yaml
import argparse
import pandas as pd
import hashlib

from llama_index.core import SimpleDirectoryReader, Document
from llama_index.core import Settings

import sys
sys.path.append(".")


from retriever.utils import base_prompt
from retriever.engine import get_retriever
from retriever.models import load_embedder, load_llm


def hash_text(text):
    h = hashlib.sha256()
    h.update(text.encode())
    return h.hexdigest()



key_path = 'keys.yaml'
cache_path = 'data/local'

if not os.path.exists(cache_path):
    os.makedirs(cache_path)
    os.makedirs(f"{cache_path}/questions", exist_ok=True)


def load_retriever():
    keys = yaml.safe_load(open(key_path))
    os.environ["OPENAI_API_KEY"] = keys['openai']

    embed_model = load_embedder("OPENAI|text-embedding-3-large")
    llm = load_llm("OPENAI|gpt-4o-mini", base_prompt=base_prompt)
    Settings.embed_model = embed_model
    Settings.llm = llm

    args = argparse.Namespace(
        rerank=False,
        regenerate=False
    )

    df = pd.read_csv(f"{cache_path}/hun_sum_portfolio.csv")

    documents = [
        Document(
            description="Egy portfolio.hu cikket tartalmaz a következő dokumentum, mely gazdasági híreket közvetít.",
            text=f"{row['title']}\n\n{row['lead']}\n\n{row["article"]}",
            doc_id=row['uuid'],
            metadata={
                'title': row['title'],
                'url': row['url'],
                'domain': row['domain'],
                'date_of_creation': row['date_of_creation'],
                'lead': row['lead'],
                'tags': row['tags'],
            }
        )
        for _, row in df.iterrows()
    ]
    documents = documents

    retriever = get_retriever(args, documents, top_n=10, rerank=args.rerank)
    return retriever


def get_results(prompt, retriever):
    assert prompt != ""
    prompt_id = hash_text(prompt)
    question_cache_path = f'{cache_path}/questions/{prompt_id}.json'

    if os.path.exists(question_cache_path):
        results = json.load(open(question_cache_path))
    else:
        if retriever is None:
            print("No retriever found, loading a new one.")
            retriever = load_retriever()
        results = [node.to_dict() for node in retriever.retrieve(prompt)]
        json.dump(results, open(question_cache_path, 'w'), indent=4)
    return results, retriever