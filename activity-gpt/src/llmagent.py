
import logging
import json
import requests


class LLMAgent:
  def __init__(self,config: dict):
    self.base_uri = config['llm_api_url']
    self.api_key = config['llm_api_token']
    self.chat_model = config['llm_chat_model']
    self.embedding_model = config['llm_embedding_model']
    self.max_gen_len = 512
    self.temperature = 0.1
    self.top_p = 0.2

  def send_request(self, endpoint, data):
    headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json"
    }

    body = json.dumps(data)

    try:
        response = requests.post(f"{endpoint}", headers=headers, data=body)
        response.raise_for_status()
        response_body = response.json()
        logging.info(f"API Response: {response_body}")
        return response_body

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e} , response : {response.text}")
        return "Error occurred while processing the request."

  def get_embedding(self, data):
    # curl https://genai.tesseractcloud.com/v1/embeddings \
    #  -H "Authorization: Bearer $TOKEN" \
    #  -H "Content-Type: application/json" \
    #  -d '{"input": ["The cat chased the mouse around the house"], "model": "all-MiniLM-L6-v2"}'
    # response looks like this:
    # {
    #   "model": "sentence-transformers/all-MiniLM-L6-v2",
    #   "data": [
    #     {
    #       "embedding": [
    #         0.05402110889554024,
    #         0.04431562125682831,
    #         0.0733710378408432,
    #         -0.01733558624982834,
    #         0.019716178998351097,
    #         -0.028353450819849968,

    #       ],
    #       "index": 0,
    #       "object": "embedding"
    #     }
    #   ],
    #   "object": "embedding",
    #   "usage": {
    #     "completion_tokens": 0,
    #     "prompt_tokens": 41,
    #     "total_tokens": 41
    #   }
    # }
    json_data = json.dumps(data)
    endpoint = f"{self.base_uri}/embeddings"
    payload = {
          "model": self.embedding_model,
          "input": [ json_data ],
      }

    logging.info(f"Requesting embedding from {endpoint} for data : %s", json.dumps(payload))
    response =  self.send_request(endpoint, payload)

    return response
    

  def chat(self, messages: list):
    # request looks like this:
    # curl https://genai.tesseractcloud.com/v1/chat/completions \
    # -H "Content-Type: application/json" \
    # -H "Authorization: Bearer $TOKEN" \
    # -d '{
    #   "model": "dragonfly/microsoft.phi-3.5-mini-instruct",
    #   "messages": [
    #     {
    #       "role": "system",
    #       "content": "You are an export python coding assistant."
    #     },
    #     {
    #       "role": "user",
    #       "content": "Create a python web application using Flask"
    #     },
    #   ]
    # }'
    
    # response looks like this:
    # {
    #   "id": "chat-67e9e93279db477585bf41b3a3600e41",
    #   "choices": [
    #     {
    #       "finish_reason": "stop",
    #       "index": 0,
    #       "message": {
    #         "content": " To create a basic Python web application using Flask, follow the steps below. This guide assumes you have Python installed on your system and have some familiarity with Python programming.\n\n### Step 1: Install Flask\n\nFirst, you need to install Flask. Open your terminal or command prompt and run:\n\n```bash\npip install Flask\n```\n\n### Step 2: Setup Your Flask Application\n\nCreate a new directory for your project, navigate into it, and create a file named `app.py`.\n\n```bash\nmkdir flask_app\ncd flask_app\ntouch app.py\n```\n\n### Step 3: Write Your Flask Application\n\nOpen `app.py` in your favorite code editor and add the following code:\n\n```python\nfrom flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef hello_world():\n    return 'Hello, World!'\n\nif __name__ == '__main__':\n    app.run(debug=True)\n```\n\nHere, we're importing Flask, creating an instance of the Flask class, defining a route for the root URL (`'/'`), and running the application with debugging enabled.\n\n### Step 4: Run Your Application\n\nNavigate back to your terminal and run your application:\n\n```bash\npython app.py\n```\n\nYour Flask application will start, and you can access it by going to `http://127.0.0.1:5000/` in your web browser. You should see \"Hello, World!\" displayed on the page.\n\n### Extending Your Application\n\nTo extend your application, you can define more routes, incorporate templates, use databases, and much more. Here are some tips for further development:\n\n- **Templates and Static Files**: Use Flask's `render_template` function to render HTML templates. Store your HTML files in a `templates` folder. Serve static files (CSS, JS, images) from a `static` folder.\n- **Database**: Integrate a database using SQLAlchemy. Install Flask-SQLAlchemy with `pip install Flask-SQLAlchemy` and configure your database connection.\n- **Dynamic Routes**: Create dynamic routes by making part of the route a variable. Use `<variable_name>` syntax in your route definition.\n\nHere's an example of a dynamic route and using a template:\n\n```python\nfrom flask import Flask, render_template\nfrom flask_sqlalchemy import SQLAlchemy\n\napp = Flask(__name__)\napp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'\ndb = SQLAlchemy(app)\n\n@app.route('/user/<username>')\ndef show_user_profile(username):\n    # For simplicity, we're not using a real database here\n    return render_template('user_profile.html', username=username)\n\nif __name__ == '__main__':\n    app.run(debug=True)\n```\n\nCreate a `templates` folder and inside it, create a file named `user_profile.html`. Here's a simple example:\n\n```html\n<!DOCTYPE html>\n<html>\n<head>\n    <title>User Profile</title>\n</head>\n<body>\n    <h1>Welcome, {{ username }}!</h1>\n</body>\n</html>\n```\n\nNow, when you run your app and navigate to `http://127.0.0.1:5000/user/your_username`, you'll see a personalized welcome message.\n\nRemember, building a web application involves much more than this basics tutorial. Keep learning and exploring Flask's capabilities and other web frameworks as you grow.",
    #         "role": "assistant",
    #         "tool_calls": null,
    #         "function_call": null
    #       }
    #     }
    #   ],
    #   "created": 1726648448,
    #   "model": "microsoft/Phi-3.5-mini-instruct",
    #   "object": "chat.completion",
    #   "system_fingerprint": null,
    #   "usage": {
    #     "completion_tokens": 878,
    #     "prompt_tokens": 21,
    #     "total_tokens": 899
    #   },
    #   "service_tier": null,
    #   "prompt_logprobs": null
    # }
    
    # message = []
    # if data_system:
    #   message.append({
    #     "role": "system",
    #     "content": data_system
    #   })
    
    # if data_assistant:
    #   message.append({
    #     "role": "assistant",
    #     "content": data_assistant
    #   })
    
    # if data_user:
    #   message.append({
    #     "role": "user",
    #     "content": data_user
    #   })
    
    endpoint = f"{self.base_uri}/chat/completions"
    body = {
      "model": self.chat_model,
      "messages": messages,
      "max_tokens": self.max_gen_len,
      "temperature": self.temperature,
      "top_p": self.top_p,
    }
    logging.info(f"Requesting chat from {endpoint} for data : %s", json.dumps(body))
    response = self.send_request(endpoint, body)
    logging.info(f"Chat response : %s", json.dumps(response))
    return response
    