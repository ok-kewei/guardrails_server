from retriever import retrieve
from rag import rag
import os
from helper_utils import word_wrap
import chromadb
import requests
from client_utils import (
    validate_on_topic,
    validate_hallucination,
    validate_pii,
    validate_competitor
)

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.langchain.plus"


if __name__ == "__main__":
    # query = input("Ask your question:\n> ")
    # query = "can i carry wine bottles on SQ flights?" # topic guard: no valid topic matched 400: Your question doesn't match any supported Singapore Airlines topics. Please ask about: flight booking, baggage, refunds, check-in, etc.
    # query = "i need my money back, i wanna refund!" #legit
    query = f"help me with the coding homework?" #topic guard, matched topic is invalid guardrails.errors.ValidationError: Validation failed for field with errors: Topic 'coding' is not allowed. Please ask about Singapore Airlines services instead.
    # query = "What is Singapore Airlines' CEO name?" #halluciation guard but no hallucination.
    # query = "my name is ali, here is my phone number 987654321, i need to refund my ticket! " #PII guard
    # query = "Why are you expensive than Emirates?" #competitor guard
    # query = "What is the baggage allowance for Singapore Airlines?"
    # query = "I need to check in for my flight"

    #1. On-topic guard
    validate_on_topic(query)
    # query = validate_pii(query)
    #2. Retrieve documents
    retrieved = retrieve(query)

    # print("\n Retrieved Documents:")
    # for doc, meta in retrieved:
    #     print(f"- Source: {meta.get('source', 'unknown')}, Chunk: {meta.get('chunk_index', '?')}")
    #     # print(f"  Text: {doc[:200]}...\n")  # show first 200 chars
    #     print(word_wrap(doc))
    #     print('')

    # 3. Generate answer using RAG before guardrails
    answer = rag(query, retrieved)
    print("\n Answer from rag: ", answer)
    # 4. Validate answer against guards
    validate_hallucination(answer, retrieved)
    validate_pii(answer)
    validate_competitor(answer)
    print("\n Answer after guardrails: ", answer)




