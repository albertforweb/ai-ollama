import logging
import json
from config import app_config
from llmagent import LLMAgent

logging.basicConfig(level=logging.DEBUG)
logging.info("loading config :  %s" % app_config)
llmagent = LLMAgent(app_config)

data=json.loads(open('training.json').read())
logging.info("training is started")
for i in range(len(data)):
  sample = data[i]["messages"]
  response = llmagent.chat(sample)
  logging.info(f"response : {response}")
  logging.info("\n")

logging.info("training is done")

logging.info("validation is started")
prompt = "distance between Moon and Earth"
logging.info(f"validate prompt : {prompt}")
messages = [
  {
    "role": "user",
    "content": prompt   
  }
]
response = llmagent.chat(messages)
logging.info(f"validate response : {response}")