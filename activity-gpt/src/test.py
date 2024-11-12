import json 
import requests


logs = json.loads(open('logs.json').read())
headers = {
  "content-type": "application/json",
}
for log in logs:
    print(log)
    response = requests.post("http://127.0.0.1:5001/api/v1/activitygpt/embedding", headers=headers, data=json.dumps(log))
    print(response.text)