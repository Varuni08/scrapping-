# agent/llm.py
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def query_groq(system_prompt, user_content, json_mode=False):
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        kwargs = {
            "model": "llama-3.3-70b-versatile", # Ensure this model name is valid in your Groq tier, else use "llama3-70b-8192"
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 2048
        }
        
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            
        completion = client.chat.completions.create(**kwargs)
        return completion.choices[0].message.content
    except Exception as e:
        print(f"LLM Error: {e}")
        return "{}" if json_mode else "Error generating response."