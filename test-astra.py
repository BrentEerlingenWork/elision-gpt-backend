import json

import numpy as np
from astrapy import DataAPIClient

# Load embeddings from .npy file
embeddings = np.load('embeddings/embeddings.npy', allow_pickle=True)

# Astra client
client = DataAPIClient(
    "AstraCS:iTBppMMgcDMaNNglttxkwRBE:0f15f5d299f20ea4c7a001fdcfc7462eb2d46c18c7551ffb9fca5daad373e563")
db = client.get_database_by_api_endpoint(
    "https://f2e7e6fe-b6e0-4c9d-9f4f-a4b8a0b9df4c-us-east-2.apps.astra.datastax.com"
)

print(f"Connected to Astra DB: {db.list_collection_names()}")


def partition(lst, n):
    division = len(lst) / n
    return [lst[round(division * i):round(division * (i + 1))] for i in range(n)]


collection = db.get_collection("elision_gpt_embeddings")

# **Save to JSON**
# Convert array to list if necessary
if isinstance(embeddings, np.ndarray):
    partitioned_embeddings = partition(embeddings.tolist(), 30)

    for iter in range(27, 31):
        data = partitioned_embeddings[iter - 1]
        transformed_array = [
            {"filename": item["filename"], "$vector": item["embedding"]}
            for item in data
        ]

        insertion_result = collection.insert_many(
            documents=transformed_array, concurrency=1, chunk_size=10)
        print(f"Batch {iter} of 30: Inserted {
              len(insertion_result.inserted_ids)} items.\n")

    print("DONE")

# insertion_result = collection.insert_many(embeddings)
# print(f"* Inserted {len(insertion_result.inserted_ids)} items.\n")
