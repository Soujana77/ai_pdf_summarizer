import PyPDF2
import os
import requests
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

