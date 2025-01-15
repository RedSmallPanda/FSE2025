# FSE2025

## Components
**`code/component_identification.py`**: script for detecting and classifying components in a prompt template.

### **Usage**:

#### 1. Set the API Key directly in your terminal:
- **Linux/MacOS**:
  ```bash
  export GROQ_API_KEY=your_actual_api_key
  ```

- **Windows**:
  ```bash
  set GROQ_API_KEY=your_actual_api_key
  ```
  
Note: Way to get the API KEY see: [https://console.groq.com/docs/quickstart](https://console.groq.com/docs/quickstart)

#### 2. Run the script with your prompt template:

```bash
python component_identification.py --prompt "YOUR PROMPT TEMPLATE"
```
Optional: Specify a custom model with the --model argument, default is llama3-70b-8192:
```bash
python component_identification.py --prompt "YOUR PROMPT TEMPLATE" --model "llama3-70b-8192"
```

For a list of supported models, see the documentation: [https://console.groq.com/docs/models](https://console.groq.com/docs/models)


- Example:
```bash
python component_identification.py --prompt "You are a music recommendation system. You will reply with song recommendations that are perfect for {user_requirement}. Only reply with the JSON object, no need to send anything else. Don't make up things.Include title, artist, album, and year in the JSON response. Use the JSON format: {"songs":[{ "title": "Title of song 1", "artist": "Artist of Song 1","album": "Album of Song 1","year": "Year of release"}]}"
```
---

## Placeholder
**`code/placeholder_identification.py`**: script for detecting and classifying placeholder in a prompt template.

### **Usage**:

#### 1. Set the API Key directly in your terminal:
- **Linux/MacOS**:
  ```bash
  export OPENAI_API_KEY=your_actual_api_key
  ```

- **Windows**:
  ```bash
  set OPENAI_API_KEY=your_actual_api_key
  ```
  
Note: Way to get the API KEY see: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

#### 2. Run the script with your prompt template:

```bash
python placeholder_identification.py --prompt "YOUR PROMPT TEMPLATE"
```
Optional: Specify a custom model with the --model argument, default is gpt-4o:
```bash
python placeholder_identification.py --prompt "YOUR PROMPT TEMPLATE" --model "gpt-4o"
```

For a list of supported models, see the documentation: [https://platform.openai.com/docs/models/overview](https://platform.openai.com/docs/models/overview)

- Example:
```bash
python placeholder_identification.py --prompt "You are a music recommendation system. You will reply with {num_songs} song recommendations in a JSON format. Only reply with the JSON object, no need to send anything else. Don't make up things. Include title, artist, album, and year in the JSON response. Use the JSON format: {"songs":[{ "title": "Title of song 1", "artist": "Artist of Song 1","album": "Album of Song 1","year": "Year of release"}]}"
```