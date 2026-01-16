from typing import List, Dict
import os
from dotenv import load_dotenv
from groq import Groq

from app.llm.prompt import SYSTEM_PROMPT
from app.llm.refusal import should_refuse, enforce_refusal

load_dotenv()


class AnswerGenerator:
    """
    Generates strictly grounded answers.
    """

    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY not found")

        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def generate_answer(self, query: str, evidence: List[Dict]) -> str:
        # -----------------------------
        # 1️⃣ PRE-GENERATION REFUSAL
        # -----------------------------
        if should_refuse(evidence):
            return self._refuse()

        # -----------------------------
        # 2️⃣ BUILD STRUCTURED INPUT
        # -----------------------------
        context_text = self._build_context(evidence)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
                Question:
                {query}
                
                Information:
                {context_text}
                """
            },
        ]

        # -----------------------------
        # 3️⃣ GENERATION
        # -----------------------------
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.0,
            max_tokens=500,
        )

        answer = response.choices[0].message.content.strip()

        # -----------------------------
        # 4️⃣ POST-GENERATION ENFORCEMENT
        # -----------------------------
        return enforce_refusal(answer)

    def _build_context(self, evidence: List[Dict], max_chars: int = 12000) -> str:
        semantic_blocks = []
        table_blocks = []
        total_chars = 0

        for item in evidence:
            text = item.get("text", "").strip()
            if not text:
                continue

            block_type = item.get("block_type", "text")

            # Metadata handling
            if "metadata" in item:
                meta = item["metadata"]
                source = meta.get("source", "unknown")
                page = meta.get("page", "unknown")
            else:
                source = item.get("source", "unknown")
                page = item.get("page", "unknown")

            block = f"[Source: {source}, Page: {page}]\n{text}\n"

            if total_chars + len(block) > max_chars:
                break

            if block_type == "table_row":
                table_blocks.append(block)
            else:
                semantic_blocks.append(block)

            total_chars += len(block)

        context = ""

        if semantic_blocks:
            context += "TEXT EXPLANATIONS:\n" + "\n".join(semantic_blocks) + "\n\n"

        if table_blocks:
            context += "TABLE FACTS:\n" + "\n".join(table_blocks)

        return context

    def _refuse(self) -> str:
        return "The answer is not available in the provided documents."

