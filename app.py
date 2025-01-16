import os

import boto3
import numpy as np
import openai
from astrapy import DataAPIClient
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
     r"/*": {"origins": ["http://localhost:3000", "https://elision-gpt-frontend.vercel.app"]}})

# Load OpenAI API key
openai.api_key = os.getenv('OPEN_AI_KEY', 'default_open_ai_key')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID', 'default_aws_access_key_id')
aws_secret_access_key = os.getenv(
    'AWS_SECRET_ACCESS_KEY', 'default_aws_secret_access_key')
aws_region = os.getenv('AWS_REGION', 'eu-central-1')
astra_client = os.getenv('ASTRA_CLIENT', 'default_astra_client')
astra_db_endpoint = os.getenv('ASTRA_DB_ENDPOINT', 'default_astra_db_endpoint')

# Initialize the client
db_client = DataAPIClient(
    astra_client)
db = db_client.get_database_by_api_endpoint(
    astra_db_endpoint
)

s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

print(f"Connected to Astra DB: {db.list_collection_names()}")


def find_most_similar(query_embedding, top_k=1):
    collection = db.get_collection("elision_gpt_embeddings")

    similarities = list(collection.find(
        projection={"filename": True},
        sort={"$vector": query_embedding},
        limit=top_k,
        include_sort_vector=True
    ))

    if len(similarities) > 0:
        filenames = [item['filename'] for item in similarities]
        return filenames

    return []


def generate_embedding(client, text):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return np.array(response.data[0].embedding)


def download_file_to_list(bucket_name, file_key) -> str:
    try:
        # Download the file's content into memory (without saving it locally)
        file_content = s3.get_object(Bucket=bucket_name,
                                     Key='chunks/' + file_key)[
            'Body'].read().decode('utf-8')

        return file_content

    except Exception as e:
        print('FAIL')
        print(f"Error: {e}")
        return []


def process_query(query, history):
    client = openai.OpenAI(api_key=openai.api_key)
    query_embedding = generate_embedding(
        client, query).astype(np.float64).tolist()

    top_k = 60

    filenames = find_most_similar(
        query_embedding, top_k=top_k)

    context = []
    for idx in filenames:
        chunk_content = download_file_to_list('rag-chunks', f'{idx}')
        context.append(chunk_content)

    combined_context = "\n".join(context)

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


@ app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "Welcome to the OpenAI Query API",
        "usage": "Send a POST request to /query with a JSON body containing a 'query' field"
    })


@ app.route('/query', methods=['POST'])
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
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
