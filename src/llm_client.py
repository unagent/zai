import os
import requests



def call_llm(messages, config):
    """Send a request to the LLM API using environment configuration"""
    api_key = config["OPENAI_API_KEY"]
    api_url = config["OPENAI_API_URL"]
    model = config["OPENAI_API_MODEL"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


    response = requests.post(
        api_url+'/chat/completions',
        json={
            "model": model,
            "messages": messages
        },
        headers=headers
    )
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']
