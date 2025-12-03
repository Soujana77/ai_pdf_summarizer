# test_api.py
import os
import requests
from dotenv import load_dotenv
import argparse
import textwrap
import sys
import json

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

if not HF_API_KEY:
    print("ERROR: HF_API_KEY not found in .env. Add HF_API_KEY=hf_xxx to your .env at project root.")
    sys.exit(1)

# Model to test
MODEL = "mistralai/Mixtral-8x7B-Instruct"
ROUTER_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL}"


def summarize_text(text, max_new_tokens=300, temperature=0.2):
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json",
    }

    # Instruction-style prompt for Mixtral
    prompt = (
        "You are a helpful assistant. Summarize the following text clearly and in detail. "
        "Produce a structured summary with headings and bullet points when appropriate.\n\n"
        f"{text}"
    )

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
        }
    }

    try:
        resp = requests.post(ROUTER_URL, headers=headers, json=payload, timeout=120)
    except Exception as e:
        print("Request failed:", e)
        return None, None

    print("\n--- HTTP STATUS ---")
    print(resp.status_code)
    print("\n--- RAW RESPONSE TEXT (first 4000 chars) ---")
    print(resp.text[:4000])

    # Try parse JSON safely
    try:
        result = resp.json()
    except Exception as e:
        print("\nCould not parse JSON response:", e)
        return resp.text, None

    # Pretty-print JSON (truncated)
    print("\n--- JSON (pretty, truncated) ---")
    try:
        print(json.dumps(result, indent=2)[:4000])
    except Exception:
        print(result)

    # Common possible response shapes:
    # 1) {"generated_text": "..."}
    # 2) [{"generated_text": "..."}]
    # 3) [{"summary_text": "..."}]
    # 4) {"error": "..."}  -> handle gracefully
    summary = None

    # case: dict with generated_text
    if isinstance(result, dict):
        if "generated_text" in result and isinstance(result["generated_text"], str):
            summary = result["generated_text"]
        elif "error" in result:
            print("\nMODEL ERROR:", result.get("error"))
        # sometimes router returns nested outputs
        elif "outputs" in result and isinstance(result["outputs"], list):
            # try to extract text from outputs
            for item in result["outputs"]:
                if isinstance(item, dict):
                    for k in ("generated_text", "text", "summary_text"):
                        if k in item and isinstance(item[k], str):
                            summary = item[k]
                            break
                if summary:
                    break

    # case: list
    if summary is None and isinstance(result, list) and len(result) > 0:
        first = result[0]
        if isinstance(first, dict):
            for k in ("generated_text", "summary_text", "text"):
                if k in first and isinstance(first[k], str):
                    summary = first[k]
                    break
        # if elements are plain strings
        if summary is None:
            for elem in result:
                if isinstance(elem, str) and len(elem) > 20:
                    summary = elem
                    break

    return resp.text, summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Mixtral summarizer on HF Router.")
    parser.add_argument("--file", "-f", help="Path to a .txt file to summarize", default=None)
    parser.add_argument("--max", type=int, default=400, help="max_new_tokens for summary")
    parser.add_argument("--temp", type=float, default=0.2, help="sampling temperature")
    args = parser.parse_args()

    if args.file:
        if not os.path.exists(args.file):
            print("File not found:", args.file)
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as fh:
            text = fh.read()
    else:
        # sample long-ish text (replace or use your own file)
        text = textwrap.dedent("""
        Photosynthesis is a process used by plants and other organisms to convert light energy into chemical
        energy that can later be released to fuel the organisms' activities. This chemical energy is stored in
        carbohydrate molecules, such as sugars, which are synthesized from carbon dioxide and water – hence the
        name photosynthesis, from the Greek phōs (light) and synthesis (putting together). Photosynthesis in plants
        generally involves the green pigment chlorophyll and generates oxygen as a byproduct. The process can be
        divided into two stages: the light-dependent reactions and the light-independent reactions (Calvin cycle).
        In the light-dependent reactions, which occur in the thylakoid membranes, light energy is used to split water
        molecules, releasing oxygen and transferring energy to ATP and NADPH. In the Calvin cycle, which occurs in the
        stroma of chloroplasts, ATP and NADPH are used to convert carbon dioxide into glucose through a series of
        enzyme-driven steps. Photosynthesis is crucial for life on Earth as it provides the oxygen we breathe and
        forms the base of the food chain.
        """) * 6

    print("\n=== Sending text (length {} chars) to model: {} ===\n".format(len(text), MODEL))

    raw, summary = summarize_text(text, max_new_tokens=args.max, temperature=args.temp)

    if summary:
        print("\n=== SUMMARY ===\n")
        print(summary.strip())
    else:
        print("\nNo usable summary returned. See RAW RESPONSE and JSON above for details.")
