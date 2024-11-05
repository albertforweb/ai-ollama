from flask import Flask
from flask import render_template
from flask import request, Response, stream_with_context
from flask import jsonify
from flask import send_from_directory
import logging

app = Flask(__name__)


@app.route('/api/v1/activity-gpt/')
def index():
	return render_template("index.html")

@app.route('/api/v1/activity-gpt/static/<path:path>')
def statics(path):
	return send_from_directory('static', path)

@app.route("/api/v1/activity-gpt/logs", methods=["POST"])
def logs():
    data = request.json
    app.logger.info("received : %s", jsonify(data))
    return "ok"

@app.route('/api/v1/activity-gpt/chat', methods=['POST'])
def chat():
	user_message = request.json.get('message')

	response = "sample chat response"

	return Response(stream_with_context(response), content_type='text/plain')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5001)

