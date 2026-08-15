import os
import json
import requests
import pandas as pd
from checker import run_checker
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'system_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def load_prompt_template():
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'diagnose_prompt.md')
    with open(prompt_path, 'r') as f:
        return f.read()

def call_mistral_api(system_prompt: str, user_prompt: str, model_name: str) -> dict:
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        return {
            "root_cause": "MISTRAL_API_KEY environment variable not set.",
            "osi_layer": "Unknown",
            "confidence": 0.0,
            "evidence": "API Key missing.",
            "next_command": None,
            "fix_steps": []
        }

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result_json = response.json()
        content = result_json['choices'][0]['message']['content']
        
        # Extract JSON if model adds markdown blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()

        return json.loads(content)
    except Exception as e:
        print(f"Error calling LLM: {e}")
        try:
             print(f"Raw response: {response.text}")
        except:
             pass
        return {
            "root_cause": "Failed to get a valid JSON response from the LLM. Manual review required.",
            "osi_layer": "Unknown",
            "confidence": 0.0,
            "evidence": f"Error: {str(e)}",
            "next_command": None,
            "fix_steps": []
        }

def diagnose_case(case_id: str, case_data: dict) -> dict:
    """
    Orchestrates the diagnosis process.
    First runs the deterministic checker, then falls back to LLM if needed.
    """
    config = load_config()
    show_outputs = case_data.get('show_outputs', '')
    
    # 1. Run Deterministic Checker
    checker_result = run_checker(show_outputs)
    
    if checker_result['status'] == "ERRORS_DETECTED":
        # Formulate response directly from checker without LLM
        details_str = " ".join(checker_result['details'])
        flags_str = ", ".join(checker_result['flags'])
        
        # Basic mapping of flags to OSI layer
        layer = "Layer 3" # Default
        if "ADMIN_DOWN" in flags_str: layer = "Layer 1"
        elif "PORT_SECURITY" in flags_str: layer = "Layer 2"
        elif "NAT" in flags_str: layer = "Layer 4"

        fix_steps = ["# Manual review required to formulate exact fix commands for: " + flags_str]
        
        if "ADMIN_DOWN" in flags_str:
            fix_steps = ["conf t", "interface <interface_name>", "no shutdown", "end"]
            
        return {
            "root_cause": f"Deterministic rule matched: {details_str}",
            "osi_layer": layer,
            "confidence": 1.0,
            "evidence": details_str,
            "next_command": "show run",
            "fix_steps": fix_steps,
            "source": "Rule-Based Checker"
        }

    # 2. Fallback to LLM if no deterministic errors found
    system_prompt = load_prompt_template()
    user_prompt = f"Symptom: {case_data.get('symptom')}\nTopology Note: {case_data.get('topology_note')}\nShow Outputs:\n{show_outputs}"
    
    llm_result = call_mistral_api(system_prompt, user_prompt, config['model_name'])
    llm_result['source'] = "AI Model"
    return llm_result

if __name__ == "__main__":
    # Small test
    print("Engine loaded.")
