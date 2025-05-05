import os
import nltk
import Stemmer

from typing import List

from llama_index.core import (
    QueryBundle,
    StorageContext,
    VectorStoreIndex,
    SimpleKeywordTableIndex,
    get_response_synthesizer, load_index_from_storage,
)

from llama_index.core.retrievers import (
    BaseRetriever,
    VectorIndexRetriever,
    KeywordTableSimpleRetriever,
)

from llama_index.core.schema import NodeWithScore
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore

from llama_index.retrievers.bm25 import BM25Retriever

from retriever.utils import Timer


class CustomRetriever(BaseRetriever):
    """Custom retriever that performs both semantic search and hybrid search."""

    def __init__(
        self,
        vector_retriever: VectorIndexRetriever,
        keyword_retriever: KeywordTableSimpleRetriever,
        mode: str = "AND",
        node_postprocessors: LLMRerank = None,
    ) -> None:
        """Init params."""

        self._vector_retriever = vector_retriever
        self._keyword_retriever = keyword_retriever
        self.node_postprocessors = node_postprocessors
        if mode not in ("AND", "OR"):
            raise ValueError("Invalid mode.")
        self._mode = mode
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve nodes given query."""
        with Timer("Vector retrieval"):
            vector_nodes = self._vector_retriever.retrieve(query_bundle)
        with Timer("Keyword retrieval"):
            keyword_nodes = self._keyword_retriever.retrieve(query_bundle)

        vector_ids = {n.node.node_id for n in vector_nodes}
        keyword_ids = {n.node.node_id for n in keyword_nodes}

        combined_dict = {n.node.node_id: n for n in vector_nodes}
        combined_dict.update({n.node.node_id: n for n in keyword_nodes})

        if self._mode == "AND":
            retrieve_ids = vector_ids.intersection(keyword_ids)
        else:
            retrieve_ids = vector_ids.union(keyword_ids)

        retrieve_nodes = [combined_dict[rid] for rid in retrieve_ids]
        with Timer("Rerank"):
            for node_postprocessor in self.node_postprocessors:
                retrieve_nodes = node_postprocessor.postprocess_nodes(retrieve_nodes, query_bundle)
        return retrieve_nodes

def get_retriever(args, nodes, top_n = 10, rerank = True):
    if rerank:
        print("[STORAGE] Reranking...")
        node_postprocessors=[
            LLMRerank(
                choice_batch_size=top_n*2,
                top_n=top_n,
            )
        ]
    else:
        print("[STORAGE] Reranking diabled")
        node_postprocessors = []

    out_docs_path = "/data/shared/data/projects/hackathon"
    storage_context_path = f"{out_docs_path}/storage/nodes_OpenAI"
    if (not os.path.exists(storage_context_path)) or args.regenerate:
        print("[STORAGE] Generating...")
        vector_index = VectorStoreIndex(nodes)
        vector_index.storage_context.persist(storage_context_path)

    storage_context = StorageContext.from_defaults(
        docstore=SimpleDocumentStore.from_persist_dir(persist_dir=storage_context_path),
        vector_store=SimpleVectorStore.from_persist_dir(
            persist_dir=storage_context_path
        ),
        index_store=SimpleIndexStore.from_persist_dir(persist_dir=storage_context_path),
    )
    vector_index = load_index_from_storage(storage_context)
    sparse_retriever = BM25Retriever.from_defaults(
        docstore=SimpleDocumentStore.from_persist_dir(persist_dir=storage_context_path),
        similarity_top_k=5,
        # Optional: We can pass in the stemmer and set the language for stopwords
        # This is important for removing stopwords and stemming the query + text
        # The default is english for both
        stemmer = Stemmer.Stemmer("hungarian"),
        language = nltk.corpus.stopwords.words('hungarian'),
    )

    # define custom retriever
    vector_retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=top_n)
    custom_retriever = CustomRetriever(vector_retriever, sparse_retriever, mode="OR", node_postprocessors=node_postprocessors)

    return custom_retriever