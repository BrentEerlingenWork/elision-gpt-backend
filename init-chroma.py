import chromadb
import numpy as np
from chromadb.config import Settings

# Load embeddings from .npy file
embeddings = np.load('embeddings/embeddings.npy', allow_pickle=True)

embedding_vectors = np.array([np.array(data['embedding'])
                              for data in embeddings])
filenames = [data['filename'] for data in embeddings]

# Initialize Chroma client
client = chromadb.HttpClient(
    host='localhost', port=8000)

# Create or retrieve a collection
collection = client.get_collection(name="elision-gpt-embeddings")
# collection = client.create_collection(name="elision-gpt-embeddings",
#                                       metadata={
#                                           "hnsw:space": "cosine"
#                                       })

# Prepare data (example IDs and metadata)
ids = [f"doc_{i}" for i in range(len(embeddings.tolist()))]
metadata = [{"info": f"Document {i}"} for i in range(len(embeddings.tolist()))]

# Add embeddings to collection

collection.add(documents=filenames, embeddings=embedding_vectors.tolist(),
               ids=ids, metadatas=metadata)
