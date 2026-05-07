import os
from abc import ABC, abstractmethod
from groq import Groq
import google.generativeai as genai


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, system: str, user: str) -> str:
        pass


class GroqProvider(LLMProvider):
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    def complete(self, system: str, user: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ]
        )
        return response.choices[0].message.content


class GeminiProvider(LLMProvider):
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    def complete(self, system: str, user: str) -> str:
        model = genai.GenerativeModel(
            model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            system_instruction=system
        )
        response = model.generate_content(user)
        return response.text


def get_llm_provider() -> LLMProvider:
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    if provider == "groq":
        return GroqProvider()
    elif provider == "gemini":
        return GeminiProvider()
    else:
        raise ValueError(f"Unknown LLM provider: '{provider}'. Choose 'groq' or 'gemini'.")