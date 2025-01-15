import re
import difflib
import os
import json
from openai import OpenAI 
import argparse

PLACEHOLDER_CATEGORIES = [
    "User Question",
    "Contextual Information",
    "Knowledge Input",
    "Metadata/Short Phrases",
    "Others"
]

def identify_placeholders(prompt_template, client, model):
    """
    Process a prompt template, detect placeholders, classify them, and get their relative word positions.
    """
    placeholder_list = detect_placeholder(prompt_template,)
    relative_positions = calculate_relative_word_positions(prompt_template, placeholder_list)
    classifications = []

    for placeholder, position in relative_positions:
        category = classify_placeholder_with_llm(placeholder, prompt_template, client, model)
        classifications.append({"placeholder": placeholder, "category": category, "position": position})

    return classifications

def detect_placeholder(prompt_template):
    """
    Detect placeholders
    """
    pattern = r"(\{\{[A-Za-z0-9_.$]*\}\}|\{[A-Za-z0-9_.$]*\}|PLACEHOLDER)"
    return re.findall(pattern, prompt_template)

def calculate_relative_word_positions(prompt_template, placeholders):
    """
    Calculate relative word positions for placeholders in the prompt template.
    """
    positions = []
    total_words = len(re.findall(r'\b\w+\b', prompt_template)) 

    for placeholder in placeholders:
        match = re.search(re.escape(placeholder), prompt_template)
        if match:
            char_start = match.start() 
            word_position = len(re.findall(r'\b\w+\b', prompt_template[:char_start])) 
            position = classify_relative_word_position(word_position, total_words)
            positions.append((placeholder, position))

    return positions

def classify_relative_word_position(word_position, total_words):
    """
    Classify the placeholder's relative word position: Beginning, Middle, End.
    """
    if word_position <= total_words / 3:
        return "Beginning"
    elif word_position >= total_words / 3 * 2:
        return "End"
    else:
        return "Middle"

def classify_placeholder_with_llm(placeholder, prompt_template, client, model):
    """
    Classify a placeholder using an LLM.
    """
    prompt = f"""Based on the following prompt template, classify the placeholder into one of these categories: User Question, Contextual Information, Knowledge Input, Metadata/Short Phrases.
    If none of the categories seem appropriate, return 'Others'. Only return one most appropriate category name or 'Others'. Do not return any extra explanation.

    ### Category:
    1. User Question: queries or questions provided by users. Examples: '{{question}}', '{{query}}'.
    2. Contextual Information: used for background or supplementary input that helps set the stage for the task but is not the primary focus. It includes data that gives additional context to the task or tracks conversational history, user preferences, or prior interactions. These placeholders provide supporting context but are not the main content being processed. Examples: '{{chat_history}}', '{{background_info}}', '{{previous_conversation}}'.
    3. Knowledge Input: represents the core content that the prompt directly processes or manipulates. It typically involves factual or knowledge-based information that needs to be analyzed, summarized, or transformed by the model. Examples: '{{document}}', '{{text}}', '{{code_snippet}}'.
    4. Metadata/Short Phrases: represents brief inputs or settings that define specific parameters or goals for the task. These placeholders are typically used to adjust or refine the task's instructions, such as setting output requirements, specifying constraints, or defining small details like names or locations. They are short in nature and often used to configure or customize the task’s execution, without being the core content or background context. Examples: '{{output_format}}', '{{name}}', '{{location}}', '{{task_type}}‘, '{{language}}', '{{timestamp}}', '{{number}}'.
    5. Others: any placeholder that does not fit into the above categories.

    ### Placeholder:
    '{placeholder}'

    ### Prompt template:
    '{prompt_template}'
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            temperature=0
        )
        response = chat_completion.choices[0].message.content.strip()
        best_match = difflib.get_close_matches(response,PLACEHOLDER_CATEGORIES, n=1, cutoff=0.6)
        
        if best_match:
            return best_match[0]
        else:
            return 'Others'
    except Exception as e:
        print(f"Error: {e}")
        return 'Others'
     
def main(prompt_template, model):
    """
    Main function to process a single prompt.
    """
    API_KEY = os.getenv("OPENAI_API_KEY")
    if not API_KEY:
        raise ValueError("Please set the OPENAI_API_KEY environment variable.")
    
    client = OpenAI(api_key=API_KEY)
    placeholders= identify_placeholders(prompt_template, client, model)
    print(f"Prompt template: {prompt_template}")
    print(json.dumps(placeholders, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Identify placeholders in a prompt template.")
    parser.add_argument("--prompt", type=str, required=True, help="A single prompt template to process.")
    parser.add_argument("--model", type=str, default="gpt-4o", help="LLM model to use.")
    args = parser.parse_args()
    main(args.prompt, args.model)