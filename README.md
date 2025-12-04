Instructions to install guardrails server
Run the following instructions from the command line in your environment:

First, install the required dependencies:
pip install -r requirements.txt
Next, install the spacy models (required for locally running NLI topic detection)
python -m spacy download en_core_web_trf
Create a guardrails account and setup an API key.
Install the models used in this course via the GuardrailsAI hub:
guardrails hub install hub://guardrails/provenance_llm --no-install-local-models;
guardrails hub install hub://guardrails/detect_pii;
guardrails hub install hub://tryolabs/restricttotopic --no-install-local-models;
guardrails hub install hub://guardrails/competitor_check --no-install-local-models;
Log in to guardrails - run the code below and then enter your API key (see step 3) when prompted:
guardrails configure
Create the guardrails config file to contain code for the hallucination detection guardrail. We've included the code in the config.py file in the folder for this lesson that you can use and modify to set up your own guards. You can access it through the File -> Open menu options above the notebook.
Make sure your OPENAI_API_KEY is setup as an environment variable, as well as your GUARDRAILS_API_KEY if you intend to run models remotely on the hub
Start up the server! Run the following code to set up the localhost:
guardrails start --config config.py