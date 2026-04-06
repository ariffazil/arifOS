import requests
import json
import time

OLLAMA_URL = 'http://ollama_engine:11434/api/chat'
MODEL = 'llama3.2' # Standard high-performance small model

def call_ollama(messages, tools=None):
    payload = {
        'model': MODEL,
        'messages': messages,
        'stream': False
    }
    if tools:
        payload['tools'] = tools
    
    try:
        resp = requests.post(OLLAMA_URL, json=payload)
        return resp.json()
    except Exception as e:
        return {'error': str(e)}

def execute_tool(name, args):
    print(f'--- EXECUTING TOOL: {name} ---')
    # Example tool: list_incidents
    if name == 'list_incidents':
        # Mocking access to postgres / vault
        return 'Incident 001: Disk Crash Resolved. Incident 002: Memory Realigned.'
    return f'Tool {name} not found.'

def governed_loop(user_query):
    print(f'--- USER INTENT: {user_query} ---')
    
    # 1. Intake & Retrieval (Simulated)
    messages = [
        {'role': 'system', 'content': 'You are the ARIF servant agent under arifOS constitutional law (A-RIF).'},
        {'role': 'user', 'content': user_query}
    ]
    
    # 2. Define Tools
    tools = [{
        'type': 'function',
        'function': {
            'name': 'list_incidents',
            'description': 'Fetch last 5 incidents from arifOS Vault',
            'parameters': {'type': 'object', 'properties': {}}
        }
    }]
    
    # 3. First Inference pass
    response = call_ollama(messages, tools=tools)
    if 'error' in response:
        return f"Ollama Error: {response['error']}"
        
    message = response.get('message', {})
    
    # 4. Handle Tool Calls
    if 'tool_calls' in message:
        for tool_call in message['tool_calls']:
            name = tool_call['function']['name']
            args = tool_call['function']['arguments']
            result = execute_tool(name, args)
            
            # Feed result back to Ollama
            messages.append(message)
            messages.append({'role': 'tool', 'content': result})
        
        # 5. Final Synthesis
        final_resp = call_ollama(messages)
        return final_resp.get('message', {}).get('content', 'Synthesis Failed.')
    
    return message.get('content', 'No tool call needed.')

if __name__ == '__main__':
    # Test: Verify the agentic loop
    result = governed_loop('Scan the incidents DB and summarize the state of the city.')
    print(f'\n--- FINAL GOVERNED ANSWER ---\n{result}')
