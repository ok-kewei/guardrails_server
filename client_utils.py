# client_utils.py
import requests

GUARDRAILS_BASE = "http://127.0.0.1:8000/guards"

def validate_on_topic(query):
    try:
        resp = requests.post(
            f"{GUARDRAILS_BASE}/topic_guard/openai/v1/chat/completions",
            json={"model": "gpt-3.5-turbo", "messages":[{"role": "user","content": query}]},
            timeout=60
        )
        print(f"Topic Guard Status: {resp.status_code}")
        # print(f"Response: {resp.json()}")
        resp.raise_for_status()
        data = resp.json()
        print("Topic guard:", data)

        if not data.get("guardrails", {}).get("validation_passed", False):
            raise ValueError("[BLOCKED] Query off-topic.")
        return True

    except requests.exceptions.HTTPError as e:
        # Catch server error and show to user
        try:
            error_data = e.response.json()
            error_msg = error_data.get("detail", "Unknown error")
            raise ValueError(f" {error_msg}")
        except:
            raise ValueError(" I can only answer questions about Singapore Airlines.")

def validate_hallucination(answer, sources):
    # print("doc for doc: ", [doc for doc, _ in sources])
    source_texts = [doc for doc, _ in sources]
    # print(f"Sources type: {type(sources)}")
    # print(f"Source texts: {source_texts}")
    payload = {
        "llmOutput": answer,
        "metadata": {
            "sources": source_texts
        }
    }
    # payload = {"llmOutput": answer,
    #            "metadata": {"sources": [doc for doc, _ in sources]}}
    # print(f"Payload: {payload}")

    resp = requests.post(
        f"{GUARDRAILS_BASE}/hallucination_guard/validate",
        json=payload,
        timeout=120
    )
    data = resp.json()
    print("Hallucination Guard: ", data)

    if not data.get("validationPassed", False):
        print(f"Hallucination detected: {data}")
        raise ValueError("Output blocked by hallucination guard")
    return True


def validate_pii(text):
    # payload = {"text": text}
    payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": text}
            ]
        }
    resp = requests.post(
        f"{GUARDRAILS_BASE}/pii_guard/validate", json=payload, timeout=10)

    resp.raise_for_status()
    data = resp.json()
    print("PII Guard: ", data)
    # masked_text = data.get("message", {}).get("content", text)
    masked_text = data.get("validatedOutput", text)
    print(f"Original: {text}")
    print(f"Masked: {masked_text}")
    if not data.get("validationPassed", False):
        raise ValueError("Output blocked by PII guard")
    return masked_text

def validate_competitor(text):
    # payload = {"text": text}
    payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": text}
            ]
        }
    resp = requests.post(
        f"{GUARDRAILS_BASE}/competitor_guard/openai/v1/chat/completions",
        json=payload,
        timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    print("Competitor Guard: ", data)
    if not data.get("validation_passed", False):
        # raise ValueError("Output blocked by competitor guard")
        print("Sorry, I cannot provide information about competitor airlines. I’m here to help with Singapore Airlines questions only.")
    return True

    # except requests.exceptions.HTTPError as e:
    #     # Catch the 400 error from server
    #     try:
    #         error_data = e.response.json()
    #         error_msg = error_data.get("detail", "")
    #
    #         if "competitors" in error_msg.lower():
    #             raise ValueError(
    #                 " I cannot provide information about competitors. I'm here to help with Singapore Airlines questions only.")
    #         else:
    #             raise ValueError(f" {error_msg}")
    #     except:
    #         raise ValueError(
    #             "I cannot provide information about competitors. I'm here to help with Singapore Airlines questions only.")