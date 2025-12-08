# RAG-Guard: Secure Retrieval-Augmented QA with Guardrails AI

In this project, we use Guardrails AI **[Guardrails AI](https://guardrailsai.com/)** 
 to enforce strict validation rules in a Retrieval-Augmented Generation (RAG) pipeline. The RAG application queries Singapore Airlines FAQ data, which has been converted into a vector database, ChormaDB for efficient retrieval. This setup is designed for AI engineers who want robust output control, ensuring responses are on-topic, factually correct, and compliant with domain rules.


## What This Project Does
This project builds a standalone Guardrails server designed to validate the RAG outputs in a secure and controlled manner.  This project provides a robust framework with four (4) custom guards to ensure AI-generated responses are safe, accurate, and compliant: 
| Guard | Input / Output | Purpose |
|-------|----------------|---------|
| **PII Detection** | Input & Output |    Prevents sensitive user data like names, phone numbers, or passports from being exposed. |
| **On-Topic Validation** | Input |  Keeps answers strictly within predefined domains, preventing irrelevant or off-topic outputs. |
| **Hallucination Detection** | Output | Compares generated answers with retrieved documents to reduce factual errors. |
| **Competitor Filtering** | Output | Protects brand by preventing competitor references |


## Architecture Diagram
```text
┌──────────────┐
│  User Input  │
└──────┬───────┘
       │
       ▼
┌────────────────────────────────────────────┐
│ Guard 1: Topic Restriction                 │
│ – Allows only domain-relevant queries      │
└──────┬─────────────────────────────────────┘
       │
       ▼
┌────────────────────────────────────────────┐
│ Guard 2: PII Detection & Masking           │
│ – Protects sensitive data                  │
└──────┬─────────────────────────────────────┘
       │
       ▼
┌───────────────────────────────────────────┐
│ RAG Pipeline                              │
│ – Retrieve relevant documents             │
│ – Generate answer using LLM               │
└──────┬────────────────────────────────────┘
       │
       ▼
┌────────────────────────────────────────────┐
│ Guard 3: Hallucination Detection           │
│ – Verifies answers against sources         │
└──────┬─────────────────────────────────────┘
       │
       ▼
┌────────────────────────────────────────────┐
│ Guard 4: Competitor Filtering              │
│ – Prevents brand harm                      │
└──────┬─────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│ Validated    │
│ Output       │
└──────────────┘
```



## Installation

### 1. Clone the Repositoy & Install Dependencies

```bash
git clone <your-repo-url>
cd guardrails_server
pip install -r requirements.txt
```
### 2. Create & activate a Conda virtual environment
1. Create a new Conda environment (example name: `rag-guard-env`) with Python 3.11:

```bash
conda create -n rag-guard-env python=3.11 
```
2. Activate the environment:
```bash
conda activate rag-guard-env
```
3. Deactivate the environment (when finished):
```bash
conda deactivate
```

### 3. Environment Setup  
1. Create a .env file:  
```bash
OPENAI_API_KEY=your_api_key_here
```

### 4. Start Guardrails Server
Prior to that you need to create a Guardrails account and set up an API key  

1. Visit **[Guardrails AI](https://guardrailsai.com/)** to create an account.  
      Obtain your Guardrails API key.  
   
2. Configure Guardrails with your API key

```bash
guardrails configure
```
Enter your API key when prompted. 

```bash
guardrails start --config config.py
```
This launches your guards at:
```bash
http://127.0.0.1:8000/guards
```
### 5. Run the RAG Application   
1. Run the guarded application 
```bash
python main.py
```



   
