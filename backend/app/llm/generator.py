from typing import List, Dict
import os
from dotenv import load_dotenv
from groq import Groq
from app.llm.prompt import SYSTEM_PROMPT

load_dotenv()
class AnswerGenerator:
    """
    Generates grounded answers using Groq-hosted LLaMA models.
    """

    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY not found in environment")

        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def generate_answer(self, query: str, evidence: List[Dict]) -> str:
        """
        Generate an answer strictly grounded in provided evidence.
        """

        if not evidence:
            return self._refuse()

        context_text = self._build_context(evidence)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user","content": f"""
                Question:
                {query}
                Information:
                {context_text}
                """,
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.0,
            max_tokens=500,
        )

        answer = response.choices[0].message.content.strip()
        return answer

    def _build_context(self, evidence: List[Dict]) -> str:
        """
        Build a clean, readable evidence block.
        """
        blocks = []
        for idx, item in enumerate(evidence, start=1):
            meta = item["metadata"]
            blocks.append(
                f"[{idx}] {meta['text']}"
            )

        return "\n\n".join(blocks)

    def _refuse(self) -> str:
        return "The answer is not available in the provided documents."
