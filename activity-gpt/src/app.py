from flask import Flask
from flask import render_template
from flask import request, jsonify
from flask import Response, stream_with_context
from flask import send_from_directory
from flask import make_response
import logging
import queue
import threading
import json
import time
import os

from qdartagent import QdrantAgent
from llmagent import LLMAgent
from ingestor import Ingestor

my_var = os.environ.get("MY_VAR") 

# Create an instance of the Flask class that is the WSGI application.
# The first argument is the name of the application module or package,
# typically __name__ when using a single module.
app = Flask(__name__, static_url_path='/static')
logging.basicConfig(level=logging.INFO)
app_config = {
  "qdrant_url" : "http://hackathon-qdrant.hack.svc.cluster.local:6333",
  "qdrant_collection" : "my_collection",
  "llm_api_url" : "https://openai.centriq-aiops.dragonfly-dev.com/v1", 
  "llm_api_token": "r0LDSgb1Pk2CzRPFIj5XDYn4eLPzIAaXG2UsMbVI3ns84iDSLT7pqwpLwWpGVvwT",
  # "llm_chat_model": "dragonfly/microsoft.phi-3.5-mini-instruct",
  "llm_chat_model": "bedrock/llama3-8B",
  "llm_embedding_model": "mxbai-embed-large-v1"
}

ingestQueue = queue.Queue()
ingestor = Ingestor()
qdartagent = QdrantAgent (ingestQueue, app_config)
llmagent = LLMAgent(app_config)

# Flask route decorators map / and /hello to the hello function.
# To add other resources, create functions that generate the page contents
# and add decorators to define the appropriate resource locators for them.
@app.route('/')
@app.route('/api/v1/activitygpt/')
def index():
   # Render the page
   return render_template("index.html")

@app.route('/api/v1/activitygpt/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# qdart api wrapper
# /api/v1/qdrant/
@app.route('/api/v1/qdrant/', methods=['GET'])
def qdrant_index():
  return jsonify({'message': 'Welcome to Qdrant API'})


# kong http-logs host api
@app.route('/api/v1/activitygpt/logs', methods=['POST'])
def http_logs():
  data = request.json
  # with open("/tmp/httplogs/logs.txt", 'a+') as f:
  #   f.write(json.dumps(data)+'\n')
  # logging.info('logs from kong : %s', json.dumps(data))
  activity = ingestor.ingest(data)
  # logging.info('activity from log : %s', json.dumps(activity))
  ingestQueue.put(activity)
  resp = make_response('OK', 200)
  return resp

@app.route('/api/v1/activitygpt/embedding', methods=['POST'])
def embedding():
  data = request.json
  activity = ingestor.ingest(data)
  logging.info('embedding data : %s', json.dumps(activity))
  embedding = llmagent.get_embedding(activity)
  logging.info(f"embedding from data : {embedding}")
  return jsonify(embedding)

@app.route('/api/v1/activitygpt/debug', methods=['POST'])
def debug():
  data = request.json
  # logging.info('add data to queue: %s', json.dumps(data))
  # ingestQueue.put(data)
  activity = ingestor.ingest(data)
  logging.info('add data to queue: %s', json.dumps(activity))
  # ingestQueue.put(activity)
  embedding = llmagent.get_embedding(activity)
  logging.info(f"embedding from data : {embedding}")
  # find similar vectors
  similars=qdartagent.search(embedding['data'][0]['embedding'])
  logging.info(f"similar vectors : %s", json.dumps(similars))
  return make_response('OK', 200)



@app.route('/api/v1/activitygpt/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    logging.info(f"chat with user message : %s", user_message)
    
    #   message.append({
    #     "role": "system",
    #     "content": data_system
    #   })
    
   
    #   message.append({
    #     "role": "assistant",
    #     "content": data_assistant
    #   })
    
    
    #   message.append({
    #     "role": "user",
    #     "content": data_user
    #   })
    messages = [
        {
            "role": "user",
            "content": user_message
        }
    ]
    response = llmagent.chat(messages)
    logging.info(f"chat response : %s", response)
    buffer = []
    buffer_size = 3

    def generate():
        for token in response["choices"]:
            message = token["message"]["content"]
            buffer.append(message)
            if len(buffer) >= buffer_size:
                yield ''.join(buffer)
                buffer.clear()
        if buffer:
            yield ''.join(buffer)

    return Response(stream_with_context(generate()), content_type='text/plain')


@app.route('/api/v1/activitygpt/chatdiagram', methods=['POST'])
def chatdiagram():
    message = request.json.get('message')
    samples = list()
    d1 = """
flowchart LR
    subgraph G1["CDNA"]
      A[kong] -->|logs| B(activity gpt agent)
      B -->|vectors| C[(Qdrant DB)]
      D[UI] -->|question| B
    end
    U[user] -->|question| D
    subgraph G2["AWS"]
      E[Bedrock LLM]
    end
    
    B -->|chat| E
""";

    if not message:
      samples.append(d1)
    else:
      samples.append(message)

    return Response(samples[0], content_type='text/plain')

def embedding_log(data, llm, qdart):
    embedding = llm.get_embedding(data)
    logging.info(f"embedding from data : %s", json.dumps(embedding))
    # qdart.store(data,embedding)

def background_task(dataQueue, llmagent, qdartagent):
    logging.info("background task started")
    while True:
        if not dataQueue.empty():
            data = dataQueue.get()
            logging.info(f"data from queue : {data}")
           
            td = threading.Thread(target=embedding_log, args=(data, llmagent, qdartagent, ))
            td.start()
            time.sleep(0.5)
    logging.info("background task completed")

if __name__ == '__main__':
   thread = threading.Thread(target=background_task, args=(ingestQueue, llmagent, qdartagent, ))
   thread.daemon = True  # This ensures the thread will exit when the main program exits
   thread.start()
  
  #  qdartagent.create_collection()

   app.run('0.0.0.0', 5001)
 
