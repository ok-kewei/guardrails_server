import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
import requests

# from dotenv import load_dotenv, find_dotenv
# _ = load_dotenv(find_dotenv()) # read local .env file

load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']
# OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
# api_key = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI()

def rag(query, retrieved_documents, model="gpt-3.5-turbo"):
    # information = "\n\n".join(retrieved_documents)
    information = "\n\n".join(
        f"[Source: {meta.get('source', 'unknown')}] {doc}"
        for doc, meta in retrieved_documents
    )

    messages = [
        {
            "role": "system",
            "content": f"""
                
                    Answer ONLY using verbatim information from the sources.
                    Do not rephrase.
                    Do not define.
                    Do not generalize.
                    List facts exactly as written.

                    """
        },
        {"role": "user", "content": f"Question: {query}. \n Information: {information}"}
    ]

    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
    )
    answer = response.choices[0].message.content
    # print("answer from rag:", answer)
    return answer
    # return content
    # return response