import json
import re

unknown_activity = {
  "request": {
      "path": ".*",
      "method": ".*"
    },
    "response": {
      "status": 200
    },
    "activity_participants": [
      "caller",
      "callee"
      ],
    "activity_description": "caller calls callee",
    "activity_sequence": [
      {
        "start": "caller",
        "finish": "callee",
        "activity": "caller calls callee"
      },
      {
        "start": "callee",
        "finish": "caller",
        "activity": "callee responds to caller"
      }
    ]
}

class Ingestor:
    def __init__(self):
      # load policies.json
        self.policies = json.load(open("policies.json", "r"))
        self.policy_dict = {}
        # build dict from policies for faster lookup
        for i, policy in enumerate(self.policies):
          key = policy["request"]["method"] + " " + policy["request"]["path"]
          self.policy_dict[key] = policy

    def ingest(self, httplog):
        # parse the log
        # log = json.loads(httplog)
        log = httplog
        # check if the log matches any policy
        uri = log["request"]["uri"]
        method = log["request"]["method"]
        key = method + " " + uri
        activity = unknown_activity.copy()
        for pattern in self.policy_dict:
            match = re.match(pattern, key)
            if match:
                activity = self.policy_dict[pattern].copy()
                break
        
        activity["prompts"] = log
        return activity
              