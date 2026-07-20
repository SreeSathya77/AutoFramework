import json

def read_transcript():
    path = r'C:\Users\sysadmin\.gemini\antigravity\brain\7e0e9d8b-f153-4d05-abc7-bbd5fbcaf79b\.system_generated\logs\transcript.jsonl'
    with open(path, 'r', encoding='utf-8') as f:
        lines = [json.loads(line) for line in f]
    
    for i in range(len(lines) - 1):
        if lines[i].get('type') == 'USER_INPUT':
            user_content = lines[i].get('content', '')
            if 'how many times' in user_content.lower():
                print("--- USER REQUEST ---")
                print(user_content[:300])
                print("--- MODEL RESPONSE ---")
                # find the first PLANNER_RESPONSE following it
                for j in range(i+1, len(lines)):
                    if lines[j].get('type') == 'PLANNER_RESPONSE':
                        print(lines[j].get('content', '')[:1000])
                        break

if __name__ == '__main__':
    read_transcript()
