from openai import OpenAI
import json
import streamlit as st
from config import MODEL_NAME

# Set OpenAI API key
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

def generate_llm_response(prompt, system_message=None, temperature=0.7, max_tokens=1000):
    """Generate a response from the LLM"""
    messages = []
    
    if system_message:
        messages.append({"role": "system", "content": system_message})
    
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in LLM call: {e}")
        return None

def process_structured_output(prompt, system_message, output_structure, temperature=0.2):
    """Generate structured output from LLM"""
    system_prompt = f"{system_message}\n\nPlease respond with a JSON object following this structure: {json.dumps(output_structure, indent=2)}"
    
    try:
        response = generate_llm_response(prompt, system_prompt, temperature)
        # Extract JSON from response
        try:
            json_start = response.find('{')
            json_end = response.rfind('}')
            if json_start >= 0 and json_end >= 0:
                json_str = response[json_start:json_end+1]
                return json.loads(json_str)
            else:
                return json.loads(response)
        except json.JSONDecodeError:
            print("Failed to parse JSON from LLM response")
            return None
    except Exception as e:
        print(f"Error in structured LLM call: {e}")
        return None
