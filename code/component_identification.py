import time
import json
from difflib import SequenceMatcher
import os
from groq import Groq
import argparse


EXPECTED_COMPONENTS= [
    "profile/role",
    "directive",
    "workflows",
    "context",
    "examples",
    "output format/style",
    "constraints",
    "others"
]

def detect_component_with_retry(prompt, client, model, max_retries=3):
    """
    Detect and classify components in the a single prompt using the LLM API with retry mechanism.

    Args:
        prompt (str): The input prompt/prompt templates to classify. 
        client (Groq): The initialized API client.
        model: model support by Groq.
        max_retries (int): Maximum number of retry attempts for API calls.

    Returns:
        dict: A dictionary of detected components.
    """
    retries = 0
    default_response = get_default_response() 
    while retries < max_retries:
        try:
            response = component_detection(prompt,client,model)
            components = json.loads(response)
            if response == default_response:
                print(f"Retry #{retries + 1}: Received default response.")
                retries += 1
            elif isinstance(components, dict):
                return components
            else:
                retries += 1
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Retry #{retries + 1}: Error decoding JSON - {str(e)}")
            retries += 1
        except Exception as e:
            print(f"Retry #{retries + 1}: Unexpected error - {str(e)}")
            retries += 1
    return json.loads(get_default_response())

def component_detection(prompt, client, model):
    """
    Detect and classify components in the given prompt using the LLM API.

    Args:
        prompt (str): The input prompt/prompt templates to classify. 
        client (Groq): The initialized API client.
        model: model support by Groq.
    
    Returns:
        str: JSON-formatted string of detected components.
    """
    prompt_text = f"""
    # Instruction:
    Please carefully analyze the provided prompt and assign each identifiable complete sentence to one of the components listed below. Avoid using phrases or single words unless they form a complete idea. Ensure that each part is distinctly categorized to prevent overlap. 
    Format the response as a JSON-like dictionary where each key represents a component and the value is the associated text or an empty string if nothing relevant is found. Only return the dictionary.

    ## Prompt:
    '''{prompt}'''

    ## Components Definitions:
    1. Profile/Role: Who or what the model is acting as.
    2. Directive: The core intent of the prompt, often in the form of an instruction or question.
    3. Workflows: Steps and processes the model should follow to complete the task.
    4. Context: Background information and context that the model needs to refer to.
    5. Examples: Examples of what the response should look like.
    6. Output Format/Style: The type, format, or style of the output.
    7. Constraints: Restrictions on what the model must adhere to when generating a response.
    8. Others: Any other components that do not fit into the above categories.

    ## Output Format:
    Please return the output in the following JSON structure without additional commentary or explanation, and ensure assign unique content to each category to avoid any overlaps:
    '''
    {{
        "profile/role": "",
        "directive": "",
        "workflows": "",
        "context": "",
        "examples": "",
        "output format/style": "",
        "constraints": "",
        "others": ""
    }}
    '''
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user", 
                    "content": prompt_text
                }
            ],
            model=model,
        )
        response = chat_completion.choices[0].message.content
        return validate_and_clean_response(response)
    except Exception as e:
        error_message = str(e)
        if "429" in error_message or "Rate limit reached" in error_message:
            try:
                wait_time = float(error_message.split('in ')[-1].split('s')[0])
                time.sleep(wait_time)
                return get_default_response()
            except (IndexError, ValueError):
                time.sleep(60)
                return component_detection(prompt)
        else:
            return get_default_response()
        
def validate_and_clean_response(response, similarity_threshold=0.7):
    """
    Validate and clean the response to ensure it matches the expected JSON structure.

    Args:
        response (str): The string returned by the LLM.
        similarity_threshold (float): Threshold for similarity matching to match component names.

    Returns:
        str: A JSON-formatted string with cleaned and validated components.
    """
    try:
        components = json.loads(response.lower())
        cleaned_response = {}
        for expected_component in EXPECTED_COMPONENTS:
            # Use similarity matching to determine if the response contains the pre-defined components
            best_match, best_ratio = find_best_match(components.keys(), expected_component)
            if best_match and best_ratio > similarity_threshold:  
                cleaned_response[expected_component] = components[best_match]
            else:
                cleaned_response[expected_component] = ""
        
        return json.dumps(cleaned_response)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return get_default_response()

def find_best_match(keys, expected_module):
    best_match = None
    best_ratio = 0.0
    for key in keys:
        ratio = SequenceMatcher(None, key, expected_module).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = key
    return best_match, best_ratio

def get_default_response():
    """
    Provide a default response structure for failed classifications.

    Returns:
        dict: A dictionary with empty values for all expected components.
    """

    return json.dumps({key: "" for key in EXPECTED_COMPONENTS})

def main(prompt, model):
    """
    Main function to identify components in a prompt/prompt template.
    """
    API_KEY = os.getenv("GROQ_API_KEY")
    if not API_KEY:
        raise ValueError("Please set the GROQ_API_KEY environment variable.")
    client = Groq(api_key=API_KEY)
    components = detect_component_with_retry(prompt, client,model)
    print("Detected Components:")
    print(json.dumps(components, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Identify components in a prompt/prompt template using LLM.")
    parser.add_argument("--prompt", type=str, required=True, help="The input prompt/prompt template to identify components.")
    parser.add_argument("--model", type=str, default="llama3-70b-8192", help="The name of model that supports by Groq.")
    args = parser.parse_args()
    main(args.prompt,args.model)