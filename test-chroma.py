import chromadb
import numpy as np

print('initializing ChromaDB')

# Initialize Chroma client
client = chromadb.HttpClient(host='localhost', port=8000)
print('connected to ChromaDB')

embeddings = np.load('embeddings/embeddings.npy', allow_pickle=True)
print('got embeddings')
# print(embeddings.tolist())

embedding_vectors = np.array([np.array(data['embedding'])
                              for data in embeddings])
print('created embedding vectors')
filenames = [data['filename'] for data in embeddings]
print('created filenames')
# print(len(filenames))

# Create or retrieve a collection
collection = client.get_collection(name="elision-gpt-embeddings")
print('got collection')
print(collection.count())
