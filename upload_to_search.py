import json
import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration, SearchableField, SearchField,
    SearchFieldDataType, SearchIndex, SimpleField, VectorSearch,
    VectorSearchProfile,
)
from dotenv import load_dotenv

load_dotenv()
endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
cred = AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"])
index_name = os.environ["AZURE_SEARCH_INDEX"]

with open("index.json", encoding="utf-8") as f:
    records = json.load(f)
dims = len(records[0]["embedding"])

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
    SearchableField(name="text", type=SearchFieldDataType.String),
    SearchField(
        name="embedding",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=dims,
        vector_search_profile_name="vprofile",
    ),
]
vector_search = VectorSearch(
    algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
    profiles=[VectorSearchProfile(name="vprofile", algorithm_configuration_name="hnsw")],
)

SearchIndexClient(endpoint, cred).create_or_update_index(
    SearchIndex(name=index_name, fields=fields, vector_search=vector_search))
print("index ready:", index_name, "dimensions:", dims)

docs = [{
    "id": f"{r['source'].replace('.md', '')}-{r['chunk_id']}",
    "source": r["source"],
    "text": r["text"],
    "embedding": r["embedding"],
} for r in records]

result = SearchClient(endpoint, index_name, cred).upload_documents(documents=docs)
print("uploaded", sum(1 for x in result if x.succeeded), "of", len(docs))