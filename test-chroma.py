import json

import chromadb
import numpy as np
import pandas as pd

# print('initializing ChromaDB')

# Initialize Chroma client
# client = chromadb.HttpClient(host='54.216.187.225', port=8000)
# print('connected to ChromaDB')

# client.heartbeat()

embeddings = np.load('embeddings/embeddings.npy', allow_pickle=True)
print('got embeddings')
# print(embeddings.tolist())

# Check the structure
print(f"Data loaded: {embeddings}")
print(f"Data type: {type(embeddings)}")  # Typically numpy array or similar


def partition(lst, n):
    division = len(lst) / n
    return [lst[round(division * i):round(division * (i + 1))] for i in range(n)]


# **Save to JSON**
# Convert array to list if necessary
if isinstance(embeddings, np.ndarray):
    partitioned_embeddings = partition(embeddings.tolist(), 30)

    for iter in range(1, 31):
        data = partitioned_embeddings[iter - 1]
        # Write to JSON file
        with open(f'output{iter}.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

print("CSV and JSON files have been created.")

# embedding_vectors = np.array([np.array(data['embedding'])
#                               for data in embeddings])
# print('created embedding vectors')
# filenames = [data['filename'] for data in embeddings]
# print('created filenames')
# # print(len(filenames))

# # Create or retrieve a collection
# collection = client.get_collection(name="elision-gpt-embeddings")
# print('got collection')
# print(collection.count())
