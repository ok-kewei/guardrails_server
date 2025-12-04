# guardrails start --config config.py
# Import Guard and Validator
from typing import Any, Dict
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY not loaded!"
# Initialize OpenAI client
openai_client = OpenAI()

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# OPENAI_KEY = os.environ.get("OPENAI_API_KEY") # Guardrails read env itself, so no need to set
from guardrails import AsyncGuard, OnFailAction, install
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)

try:
    from guardrails.hub import ProvenanceLLM, DetectPII, RestrictToTopic, CompetitorCheck

except ImportError:
    # NOTE: These install commands can be replaced by the cli command
    #  ```
    #   guardrails hub install hub://guardrails/provenance_llm \
    #   hub://guardrails/detect_pii hub://tryolabs/restricttotopic \
    #   hub://guardrails/competitor_check;
    # ```
    install("hub://guardrails/provenance_llm", False)
    # TODO install("hub://guardrails/provenance_nli", True)
    install("hub://guardrails/detect_pii", False)
    install("hub://tryolabs/restricttotopic", False)
    install("hub://guardrails/competitor_check", False)

    from guardrails.hub import ProvenanceLLM, DetectPII, RestrictToTopic, CompetitorCheck

import re
from typing import Any, Dict, List, Optional
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)


@register_validator(name="custom_topic_guard", data_type="string")
class CustomTopicGuard(Validator):
    """
    Custom topic guard that classifies text against valid/invalid topics
    using keyword matching and optional LLM classification
    """

    def __init__(
            self,
            valid_topics: List[str],
            invalid_topics: List[str],
            use_llm: bool = False,
            llm_callable=None,
            **kwargs
    ):
        """
        Args:
            valid_topics: List of allowed topics
            invalid_topics: List of forbidden topics
            use_llm: Whether to use LLM for classification
            llm_callable: Function to call LLM (if use_llm=True)
        """
        self.valid_topics = valid_topics
        self.invalid_topics = invalid_topics
        self.use_llm = use_llm
        self.llm_callable = llm_callable

        # Create lowercase versions for case-insensitive matching
        self.valid_topics_lower = [t.lower() for t in valid_topics]
        self.invalid_topics_lower = [t.lower() for t in invalid_topics]

        super().__init__(**kwargs)

    def keyword_match(self, text: str) -> Optional[str]:
        """
        Match text against topics using keywords
        Returns the matched topic or None
        """
        text_lower = text.lower()

        # Check for invalid topics first (highest priority)
        for topic in self.invalid_topics_lower:
            # Use word boundaries for whole word matching
            if re.search(r'\b' + re.escape(topic) + r'\b', text_lower):
                return topic

        # Check for valid topics
        for topic in self.valid_topics_lower:
            if re.search(r'\b' + re.escape(topic) + r'\b', text_lower):
                return topic

        return None

    def llm_classification(self, text: str) -> Optional[str]:
        """
        Use LLM to classify the text
        Returns the classified topic or None
        """
        if not self.llm_callable:
            return None

        try:
            all_topics = self.valid_topics + self.invalid_topics
            result = self.llm_callable(text, all_topics)

            # Normalize result
            result_lower = result.lower().strip()

            # Check if result matches any topic
            for topic in all_topics:
                if result_lower == topic.lower():
                    return topic

            return None
        except Exception as e:
            print(f"LLM classification error: {e}")
            return None

    def _validate(
            self,
            value: str,
            metadata: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Main validation method
        """
        # Step 1: Try keyword matching first (fast)
        matched_topic = self.keyword_match(value)
        print("Matched Topic: ",matched_topic )

        # Step 2: If no match, try LLM classification (if enabled)
        if not matched_topic and self.use_llm:
            matched_topic = self.llm_classification(value)
            print("LLM Classified Topic: ", matched_topic)

        # Step 3: Check if matched topic is invalid
        if matched_topic and matched_topic.lower() in self.invalid_topics_lower:
            return FailResult(
                error_message=f"Topic '{matched_topic}' is not allowed. Please ask about Singapore Airlines services instead."
            )

        # Step 4: If no valid topic matched
        if not matched_topic:
            return FailResult(
                error_message="Your question doesn't match any supported Singapore Airlines topics. Please ask about: flight booking, baggage, refunds, check-in, etc."
            )

        # Step 5: Valid topic found
        print("Valid topic verified: ", matched_topic)
        return PassResult(message=f"Topic verified: {matched_topic}")

# hallucination_guard = AsyncGuard(name="hallucination_guard").use(ProvenanceLLM, validation_method="full", llm_callable='gpt-4o-mini', on_fail=OnFailAction.EXCEPTION)
hallucination_guard = AsyncGuard(name="hallucination_guard").use(
    ProvenanceLLM, validation_method="sentence", llm_callable='gpt-4o-mini', on_fail=OnFailAction.EXCEPTION)


pii_guard = AsyncGuard(name="pii_guard").use(
    DetectPII(
        pii_entities=['PERSON', 'PHONE_NUMBER',],
        # on_fail="exception" #on_fail="refrain"
        # on_fail=OnFailAction.EXCEPTION
        on_fail=OnFailAction.FIX
    ),
    on="messages"
).use(
    DetectPII(
        pii_entities=['PERSON', 'PHONE_NUMBER'],
        on_fail="fix"
    ),
    on="output"
)


def llm_callable(text: str, topics: list) -> str:
    """LLM callable for custom topic guard"""
    topics_str = ", ".join(topics)

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Classify the user message to one of: {topics_str}\nRespond with ONLY the topic name or 'none'."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.1
    )

    return response.choices[0].message.content.strip()

# def llm_callable(text: str, topics: list) -> str:
#
#     valid_topics_str = ", ".join(VALID_TOPICS_LIST)
#     # topics_str = ", ".join(topics)
#     # print("topics_str: ",topics_str)
#     system_prompt = f"""You are a topic classifier for a Singapore Airlines chatbot.
# Your job is to identify the MAIN topic of the user's message.
#
# Valid topics you should classify as:
# {valid_topics_str}
#
# Instructions:
# 1. Read the user's message carefully
# 2. Identify the MAIN topic that best matches
# 3. If the message is about Singapore Airlines services (flights, baggage, check-in, etc), classify it to the most specific matching topic
# 4. If the message doesn't match any topic, respond with exactly: "none"
# 5. Respond with ONLY the topic name or "none" - nothing else
#
# Examples:
# - "How much luggage can I take?" → "baggage allowance"
# - "What time should I arrive?" → "check in"
# - "Tell me about your airlines" → "singapore airlines"
# - "What is 2+2?" → "none"
# """
#
#     response = openai_client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {
#                 "role": "system",
#                 "content": system_prompt
#             },
#             {
#                 "role": "user",
#                 "content": f"Classify this message: {text}"
#             }
#         ],
#         temperature=0.1  # Low temperature for consistent classification
#     )
#
#     result = response.choices[0].message.content.strip()
#     result= result.lower()
#     print("RESULT", result)
#     # Normalize: match against valid topics
#     valid_topics_lower = [t.lower() for t in VALID_TOPICS_LIST]
#     print("valid_topics_lower", valid_topics_lower)
#     if result in valid_topics_lower:
#         print("yes!")
#         # Return the exact topic from the list
#         idx = valid_topics_lower.index(result)
#         print("valid_topics_lower.index(result)", valid_topics_lower.index(result))
#         print("idx", idx)
#         print("topics[idx]", VALID_TOPICS_LIST[idx])
#         return VALID_TOPICS_LIST[idx]
#
#     # Debug logging
#     print(f"Query: {text[:100]}...")
#     print(f"LLM Response: '{result}'")
#     print(f"Valid topics: {valid_topics_lower}")
#
#     return result


topic_guard = AsyncGuard(
    name="topic_guard",
   ).use(
    # RestrictToTopic(
    CustomTopicGuard(
        valid_topics=[
            "singapore airlines",
            "flight booking",
            "baggage allowance",
            "check in",
            "boarding pass",
            "cabin classes",
            "ticket change",
            "refund",
            "seat selection",
            "inflight meals",
            "krisflyer",
            "carry on baggage",
            "hand carry",
            "checked baggage",
            "excess baggage",
            "luggage",
            "travel requirements",
            "transit",
            "lost baggage"
        ],
        invalid_topics=[
            "politics",
            "religion",
            "school homework",
            "coding",
            "automobiles",
            "healthcare",
            "legal advice",
            "geography",
            "history"
        ],
        llm_callable=llm_callable,
        # llm_model="gpt-3.5-turbo",
        # disable_classifier=False,
        # disable_llm=True,
        disable_classifier=True,
        disable_llm=False,
        on_fail=OnFailAction.EXCEPTION
    ),
    on="messages"
)


competitor_guard = AsyncGuard(name="competitor_guard").use(CompetitorCheck(
    competitors=["Emirates"],
    on_fail=OnFailAction.FILTER
    )
)

