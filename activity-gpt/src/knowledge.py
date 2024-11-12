import json

input = json.loads(open('/Users/hongwel2/git/demo-activity-gpt/activity-gpt/src/policies.json').read())
output = "/Users/hongwel2/git/demo-activity-gpt/activity-gpt/src/knowledge.json"


def format_key(key):
    return key.replace(".*", "id").replace(":", "").replace("/", "_").replace(" ", "_").replace("<>", "id")

def create_knowledge(input):
    knowledge = {}
    for policy in input:
        print(json.dumps(policy, indent=4))
        key =  format_key(policy["request"]["method"] + " " + policy["request"]["path"])
        des = policy["activity_description"]
        req = policy["request"]["method"] + " " + policy["request"]["path"]
        diag = "sequenceDiagram"
        for actor in policy["activity_participants"]:
            diag += f"\n\tparticipant {actor}"
        for activity in policy["activity_sequence"]:
            start = activity["start"]
            finish = activity["finish"]
            note = activity["activity"]
            diag += f"\n\t{start} ->> {finish}: {note}"
            
        question = f"mermaid sequence diagram for api request\n{req}"
        answer = f"{des}\n\n here is the sequence diagram for the activity\n```mermaid\n{diag}\n```"
        
        # knowledge.append({"question": question, "context": answer})
        knowledge[key] = {"question": question, "context": answer}
    # store into file
    
    with open(output, 'w') as f:
        json.dump(knowledge, f, indent=4)
        
create_knowledge(input)
    