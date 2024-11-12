import json
import logging

logging.basicConfig(level=logging.INFO)

def get_training_data():
  # data=[]
  # with open('logs.txt') as f:
  #   for line in f:
  #     json_data = json.loads(line)
  #     data.append(json_data)
  data = json.loads(open('logs.json').read())
  return data

# logging.info(f"training data: %s", json.dumps(get_training_data()))

from langchain.text_splitter import RecursiveCharacterTextSplitter

def get_data_chunks(doc):
  text_splitter = RecursiveCharacterTextSplitter(
      # Set a really small chunk size, just to show.
      chunk_size = 1000,
      chunk_overlap  = 100,
    )
  chunks = text_splitter.split_text(json.dumps(doc))
  return chunks
  
# logging.info(f"chunks: %s", json.dumps(get_data_chunks(get_training_data()[0])))

import requests

def get_embeddings(data):
    model="mxbai-embed-large-v1"
    endpoint = "https://openai.centriq-aiops.dragonfly-dev.com/v1/embeddings"
    apikey = "r0LDSgb1Pk2CzRPFIj5XDYn4eLPzIAaXG2UsMbVI3ns84iDSLT7pqwpLwWpGVvwT"

    headers = {
      "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }
    payload = {
      "model": model,
        "input": [ data ],
    }
    
    response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    response_body = response.json()
    return response_body

# logging.info(f"embedding : %s", json.dumps(get_embeddings(get_data_chunks(get_training_data()[0])[0])))

def test_embeddings():
  data = get_training_data()
  for input in data:
    chunks = get_data_chunks(input)
    for chunk in chunks:
      logging.info(f"embedding : %s", json.dumps(get_embeddings(chunk)))
  
# test_embeddings()
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Batch
from qdrant_client.models import VectorParams, Distance
collection = "training"

def get_qdrant_client():
  endpoint = "http://localhost:6333"
  return QdrantClient(endpoint)

def create_collection(collection):
    client = get_qdrant_client()
    if client.collection_exists(collection):
      client.delete_collection(collection)
    
    # vector size is 1024 from model mxbai-embed-large-v1
    client.create_collection(
        collection_name=collection,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )

# create_collection(collection)

def store_vectors(collection, message, vectors):
    client = get_qdrant_client()
    id = str(uuid.uuid4())
    result = client.upsert(
      collection_name=collection,
      points=Batch(
        ids=[id],
        vectors=[vectors],
        payloads=[{"message": str(message)}],
      )
    )
    return result
  
def test_store_vectors():
  data = get_training_data()
  for input in data:
    chunks = get_data_chunks(input)
    for chunk in chunks:
      embedding = get_embeddings(chunk)
      result = store_vectors(collection, chunk, embedding["data"][0]["embedding"])
      
  return result
  
# logging.info(f"store vectors : %s", test_store_vectors())

def get_similar_vectors(collection, query_vector):
    client = get_qdrant_client()
    hits = client.search(
      collection_name=collection,
      query_vector=query_vector,
      limit=5  # Return 5 closest points
    )
    return hits
  
def test_search_vectors():
  data = get_training_data()[0]
  chunk = get_data_chunks(data)[0]
  embedding = get_embeddings(chunk)
  result = get_similar_vectors(collection, embedding["data"][0]["embedding"])
  if result and len(result) > 0:
    similars = []
    for hit in result:
      obj =  {
      "id":hit.id,
      "score":hit.score,
      "message" : hit.payload['message']
    }
    similars.append(obj)
    return similars
  return None

# logging.info(f"similar vectors : %s", json.dumps(test_search_vectors()))

def send_chat(messages):
    endpoint = "https://openai.centriq-aiops.dragonfly-dev.com/v1/chat/completions"
    apikey = "r0LDSgb1Pk2CzRPFIj5XDYn4eLPzIAaXG2UsMbVI3ns84iDSLT7pqwpLwWpGVvwT"

    headers = {
      "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }
    payload = {
      "model": "bedrock/llama3-8B",
      "messages": messages
    }
    
    response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    response_body = response.json()
    return response_body
  
def test_chat():
  data = get_training_data()[0]
  messages = [
    {
      "role": "system",
      "content": "you are an kong and nginx expert"
    },
    {
      "role": "user",
      # "content": "summarize this kong log \n\n" + json.dumps(data)
      "content": "api log example of ui login \n\n" + json.dumps(data)
    },
    {
      "role": "assistant",
      "content": "it is harbor ui api for showing user the login page, user can input credentials and login"
    },
    {
      "role": "user",
      "content": "generate mermaid sequence diagram for this kong log \n\n" + json.dumps(data)
    },
  ]
  response = send_chat(messages)
  #  choices -> [ message -> content ]
  choices = response["choices"]
  answer = []
  for choice in choices:
    answer.append(choice["message"]["content"])
  return '\n'.join(answer)

# logging.info(f"chat response : %s", test_chat())

from ingestor import Ingestor

def activity_training():
  ingest = Ingestor()
  data = get_training_data()
  for sample in data:
      activity = ingest.ingest(sample)
      chunks = get_data_chunks(activity)
      for chunk in chunks:
        embedding = get_embeddings(chunk)
        store_vectors(collection, chunk, embedding["data"][0]["embedding"])

# activity_training()

def get_prompt(question, context):
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": f"""Answer the following Question based on the Context only. Only answer from the Context. If you don't know the answer, say 'I don't know'.
    Question: {question}\n\n
    Context: {context}\n\n
    Answer:\n""",
        },
    ]

def format_key(key):
    return key.replace(".*", "id").replace(":", "").replace("/", "_").replace(" ", "_").replace("<>", "id")

def chat_with_context(question):
    kb = json.loads(open('knowledge.json').read())
    key = format_key("GET /idm/api/v1/im/tenants/.*/roles")
    # key = format_key("POST /api/idm/v1/local/authorize/ui/login")
    data = kb[key]
    question = f"mermaid sequence diagram for api request\n{key}"
    
    # embed = get_embeddings(question)
    # print("embed from question : \n%s", json.dumps(embed))
    # similar = get_similar_vectors(collection, embed["data"][0]["embedding"])
    # print("similars from question : \n%s", json.dumps(similar))
    
    
    prompt = get_prompt(question, data["context"])
    # prompt = get_prompt(question, data["context"])
    
    response = send_chat(prompt)
    choices = response["choices"]
    answer = []
    for choice in choices:
        answer.append(choice["message"]["content"])
    return '\n'.join(answer)
  
logging.info(f"chat with context response : %s", chat_with_context("what is the api log example of ui login?"))

