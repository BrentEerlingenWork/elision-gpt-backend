import os

import chromadb
import numpy as np
import openai
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Load OpenAI API key
with open('secret.txt', 'r') as file:
    openai.api_key = file.read().strip()

# Load saved embeddings
chroma_client = chromadb.HttpClient(host='localhost', port=8000)
chroma_collection = chroma_client.get_collection(name="elision-gpt-embeddings")

# Extract embeddings and filenames from the loaded data
# filenames = chroma_collection.get(include=["documents"])['documents']


def find_most_similar(query_embedding, top_k=1):
    similarities = chroma_collection.query(
        query_embedding,
        n_results=top_k,
    )

    return similarities['documents'][0]


def generate_embedding(client, text):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return np.array(response.data[0].embedding)


def process_query(query, history):
    client = openai.OpenAI(api_key=openai.api_key)
    query_embedding = generate_embedding(client, query)
    top_k = 60

    filenames = find_most_similar(
        query_embedding, top_k=top_k)

    context = []
    for idx in filenames:
        chunk_path = f"chunks/{idx}"
        with open(chunk_path, "r") as file:
            chunk_content = file.read()
            context.append(chunk_content)

    combined_context = "\n".join(context)
    
    print(combined_context)

    prompt = f"""
            Use the users previous messages for better context:
            {history}

            Answer the question
            {query}
            """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Add a new line before and after all triple backticks in the response."},
            {"role": "user", "content": f"Based on the following information:\n\n{
                combined_context}\n\n{prompt}"}
        ],
        max_tokens=5000,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "Welcome to the OpenAI Query API",
        "usage": "Send a POST request to /query with a JSON body containing a 'query' field"
    })


@app.route('/query', methods=['POST'])
def query():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400

    query = data['query']
    history = data['history']
    try:
        result = process_query(query, history)
        return jsonify({"response": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
