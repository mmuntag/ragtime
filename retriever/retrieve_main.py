import os
import json
import yaml
import argparse
import pandas as pd

from llama_index.core import SimpleDirectoryReader, Document
from llama_index.core import Settings

import sys
sys.path.append(".")


from retriever.utils import base_prompt
from retriever.engine import get_retriever
from retriever.models import load_embedder, load_llm

# python retriever/retrieve_main.py
if __name__ == "__main__":
    # === Init OpenAI API key ===
    with open("keys.yaml") as f:
        keys = yaml.load(f, Loader=yaml.FullLoader)
    os.environ["OPENAI_API_KEY"] = keys['openai']

    # === Argparser ===
    # 1.Parse if storeage must be regenerated:
    parser = argparse.ArgumentParser(description="Parse arguments for the retriever.")
    parser.add_argument("--regenerate", action="store_true", help="Regenerate the storage.", default=False)
    parser.add_argument("--rerank", action="store_true", help="Apply LLM rerank", default=False)
    args = parser.parse_args()

    # === Load models ===
    embed_model = load_embedder("OPENAI|text-embedding-3-large")
    llm = load_llm("OPENAI|gpt-4o-mini", base_prompt=base_prompt)
    Settings.embed_model = embed_model
    Settings.llm = llm

    df = pd.read_csv("data/local/hun_sum_portfolio.csv")
    print("Len portfolio", len(df))
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

    retriever = get_retriever(args, documents, top_n=200, rerank=args.rerank)

    query = {
        "id": "nagy_marton_1",
        #"text": "Nagy Márton nemzetgazdasági miniszter bejelentést tesz",
        "text": "Nagy Márton nemzetgazdasági miniszter bejelentést tesz, vagy a kormányzat gazdaságpolitikai változásáról beszél",
    }

    results = retriever.retrieve(query["text"])
    print("Retrieved nodes:", len(results))
    for node in results:
        print(f"Node ID: {node.node.node_id}, Score: {node.score}")
        print(f"Node text: <<{node.metadata['title']}>> {node.metadata['lead']}\n{node.metadata['tags']}")
        #print(f"Node text: {node['title']} {node['lead']} {node.text}")
        print("-" * 20)

    # Save the retrieved nodes to a JSON file
    output_file = f"data/local/questions/{query['id']}.json"
    with open(output_file, "w") as f:
        json.dump([node.to_dict() for node in results], f, indent=4)