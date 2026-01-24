import requests
import logging

def get_models():
    """Fetches the list of available models from the LM Studio server."""
    try:
        response = requests.get("http://localhost:1234/v1/models")
        response.raise_for_status()
        models = response.json()
        logging.info(f"Successfully fetched models: {models}")
        return models
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching models: {e}")
        raise e

def post_completion(prompt):
    """Sends a prompt to the server and gets a response."""
    try:
        response = requests.post("http://localhost:1234/v1/chat/completions",
                                 json={"messages": [{"role": "user", "content": prompt}]})
        response.raise_for_status()
        completion = response.json()
        logging.info(f"Successfully received completion: {completion}")
        return completion
    except requests.exceptions.RequestException as e:
        logging.error(f"Error posting completion: {e}")
        raise e
