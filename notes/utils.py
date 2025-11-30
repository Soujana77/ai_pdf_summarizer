import PyPDF2
import os
import requests
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")


# -----------------------------
#   FUNCTION 1: Extract PDF Text
# -----------------------------
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


# -----------------------------
#   FUNCTION 2: Generate Summary
# -----------------------------
def generate_summary(text):
    url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": text}

    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        # Expected result format:
        # [{ "summary_text": "..." }]
        if isinstance(result, list) and "summary_text" in result[0]:
            return result[0]["summary_text"]
        else:
            return "AI could not generate summary."

    except Exception as e:
        return f"Summary generation failed. Error: {str(e)}"
