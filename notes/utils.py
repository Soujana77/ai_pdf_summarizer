import PyPDF2
import os
import requests
import json
import re
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")


# ---------------------------------------------------
# FUNCTION 1: Extract text from PDF
# ---------------------------------------------------
def extract_text(file_path):
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        return f"Could not extract text from this PDF. Error: {str(e)}"


# ---------------------------------------------------
# FUNCTION 2: Generate Summary using HF Router API
# ---------------------------------------------------
def generate_summary(text):
    url = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": text,
        "parameters": {
            "max_length": 150,
            "min_length": 40
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        # debug print
        print("RAW RESPONSE:", response.text)

        result = response.json()

        # New HF Router format
        if "generated_text" in result:
            return result["generated_text"]

        # Old format (fallback)
        if isinstance(result, list) and "summary_text" in result[0]:
            return result[0]["summary_text"]

        return "AI could not generate summary."

    except Exception as e:
        return f"Summary generation failed. Error: {str(e)}"
    
    # -----------------------------
#   EXTRA AI TOOLS
# -----------------------------

def generate_keywords(text):
    prompt = f"Extract 8-15 important keywords from the following text:\n\n{text}"
    return generic_ai_call(prompt)


def generate_bullets(text):
    prompt = f"Convert the following text into clean bullet point notes:\n\n{text}"
    return generic_ai_call(prompt)


def explain_like_5(text):
    prompt = f"Explain this text in the simplest way possible, like explaining to a 5-year-old:\n\n{text}"
    return generic_ai_call(prompt)


def simplify_text(text):
    prompt = f"Simplify the following text and make it easy for students:\n\n{text}"
    return generic_ai_call(prompt)


def translate_text(text, language):
    prompt = f"Translate this text to {language}:\n\n{text}"
    return generic_ai_call(prompt)


# -----------------------------
#   Generic function used by all tools
# -----------------------------
def generic_ai_call(prompt):
    url = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {"inputs": prompt}

    try:
        response = requests.post(url, headers=headers, json=payload)
        print("RAW RESPONSE:", response.text)
        result = response.json()

        # Modern HF format
        if "generated_text" in result:
            return result["generated_text"]

        # Older format (some models still return this)
        if isinstance(result, list) and "summary_text" in result[0]:
            return result[0]["summary_text"]

        if "error" in result:
            return f"AI Error: {result['error']}"

        return "AI could not generate a response."

    except Exception as e:
        return f"AI request failed: {str(e)}"


# -----------------------------
#   NEW INSTRUCT AI CALL
# -----------------------------
def instruct_ai_call(prompt):
    url = "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.2"

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    # Format the prompt for Mistral Instruct
    formatted_prompt = f"<s>[INST] {prompt} [/INST]"

    payload = {
        "inputs": formatted_prompt,
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.3,
            "return_full_text": False
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        print("RAW INSTRUCT RESPONSE:", response.text)
        result = response.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        
        if "generated_text" in result:
            return result["generated_text"]

        if "error" in result:
            return f"AI Error: {result['error']}"

        return ""
    except Exception as e:
        print(f"Instruct AI Request Failed: {str(e)}")
        return ""

# -----------------------------
#   FEATURE 1: FLASHCARDS
# -----------------------------
def generate_flashcards(text):
    prompt = f"""
You are a helpful study assistant. Extract 5 key concepts from the following text and create flashcards.
Return ONLY a valid JSON array of objects, where each object has exactly two text fields: "question" and "answer". Do not include any other text or markdown.

Example format:
[
  {{"question": "What is Python?", "answer": "A programming language."}}
]

Text:
{text}
"""
    response_text = instruct_ai_call(prompt)
    
    # Try parsing JSON
    try:
        # Find JSON array using regex if surrounded by other text
        match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        return json.loads(response_text)
    except Exception as e:
        print("Failed to parse flashcards JSON:", e)
        # Fallback to empty list or basic regex
        return [
            {"question": "Error generating flashcards.", "answer": "Please try again with a shorter text."}
        ]

# -----------------------------
#   FEATURE 2: KEYWORDS
# -----------------------------
def extract_keywords(text):
    prompt = f"""
Extract the top 10-15 most important keywords or short phrases from the following text.
Return ONLY a valid JSON array of strings. Do not include any other text or markdown.

Example format:
["machine learning", "dataset", "neural networks"]

Text:
{text}
"""
    response_text = instruct_ai_call(prompt)
    
    try:
        match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        return json.loads(response_text)
    except Exception as e:
        print("Failed to parse keywords JSON:", e)
        # Fallback processing if JSON fails: split by commas or newlines
        words = re.split(r'[,\n]', response_text)
        cleaned = [w.strip(" -*\"'") for w in words if len(w.strip()) > 2]
        if cleaned:
            return cleaned[:15]
        return ["Error extracting keywords"]

# -----------------------------
#   FEATURE 3: QUIZ
# -----------------------------
def generate_quiz(text):
    prompt = f"""
You are a helpful study assistant. Generate exactly 3 multiple-choice questions based on the text.
Return ONLY a valid JSON array of objects. Each object must have:
- "question" (string)
- "options" (array of exactly 4 strings, e.g., ["A) ...", "B) ...", "C) ...", "D) ..."])
- "answer" (string, the exact text of the correct option from the options array)
Do not include any other text or markdown.

Example format:
[
  {{"question": "What is 2+2?", "options": ["A) 1", "B) 2", "C) 3", "D) 4"], "answer": "D) 4"}}
]

Text:
{text}
"""
    response_text = instruct_ai_call(prompt)
    
    try:
        match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        return json.loads(response_text)
    except Exception as e:
        print("Failed to parse quiz JSON:", e)
        return []

