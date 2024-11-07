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

from qdartagent import QdrantAgent
from llmagent import LLMAgent

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
  "llm_chat_model": "dragonfly/microsoft.phi-3.5-mini-instruct",
  "llm_embedding_model": "mxbai-embed-large-v1"
}

ingestQueue = queue.Queue()

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
  app.logger.info('logs from kong : %s', json.dumps(data))
  # kongReq = request.form.get('request')
  # kongResp = request.form.get('response')
  # if kongReq is None or kongResp is None:
  #   app.logger.info('Invalid request')
  #   return jsonify({'error': 'Invalid request'}), 400
  
  # app.logger.info('%s', data)
  # ingestQueue.put(data)
  resp = make_response('OK', 200)
  return resp

@app.route('/api/v1/activitygpt/embedding', methods=['POST'])
def embedding():
  data = request.json
  app.logger.info('embedding data : %s', json.dumps(data))
  embedding = llmagent.get_embedding(data)
  app.logger.info(f"embedding from data : {embedding}")
  return jsonify(embedding)

@app.route('/chat', methods=['POST'])
@app.route('/api/v1/activitygpt/chat', methods=['POST'])
def chat():
    # user_message = request.json.get('message')
    # response = chat_engine.stream_chat(user_message)
    # buffer = []
    # buffer_size = 3

    # def generate():
    #     for token in response.response_gen:
    #         buffer.append(token)
    #         if len(buffer) >= buffer_size:
    #             yield ''.join(buffer)
    #             buffer.clear()
    #     if buffer:
    #         yield ''.join(buffer)

    # return Response(stream_with_context(generate()), content_type='text/plain')

    samples = list()
    d1 = """
sequenceDiagram
    autonumber
    Alice->>John: Hello John, how are you?
    loop HealthCheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts!
    John-->>Alice: Great!
    John->>Bob: How about you?
    Bob-->>John: Jolly good!
""";
    samples.append(d1)

    # js_string = f"{samples[0]}"
    # return Response(stream_with_context(js_string), content_type='text/plain')
    return Response(samples[0], content_type='text/plain')


def background_task():
    while True:
        if not ingestQueue.empty():
            data = ingestQueue.get()
            # call LLM embedding to get vector
            embedding = llmagent.get_embedding(data)
            app.logger.info(f"embedding from data : {embedding}")
            # store vector in qdrant
            vector = embedding['data'][0]['embedding']
            qdartagent.store(data,vector)
            time.sleep(1)
    app.logger.info("background task completed")

if __name__ == '__main__':
   thread = threading.Thread(target=background_task)
   thread.daemon = True  # This ensures the thread will exit when the main program exits
   thread.start()
    
   app.run('0.0.0.0', 5001)
 
