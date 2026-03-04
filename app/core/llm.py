"""

Wraps the Groq LLM + prompt template + QA chain.
Chain is created once and reused across questions.
"""

from langchain_groq import ChatGroq
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.schema import Document as LCDocument
from app.config.config import settings
from app.core.exceptions import LLMError, ConfigurationError
from app.utils.logger import logger

_PROMPT_TEMPLATE = """
You are a helpful assistant that answers questions based strictly on the provided document context.

Rules:
- Answer as thoroughly as possible using ONLY the context below.
- If the answer is not contained in the context, respond with: "I don't have enough information in the document to answer this."
- Do not make up or infer information beyond the context.
- Be concise, clear, and well-structured.

Context:
{context}

Question:
{question}

Answer:
"""


class LLMChain:
    """
    Manages the LLM and QA chain lifecycle.

    Usage:
        chain = LLMChain()
        answer = chain.ask(question, docs)
    """

    def __init__(self) -> None:
        settings.llm.validate()
        self._chain = self._build_chain()

    # ── Public API ────────────────────────────────────────────────────────

    def ask(self, question: str, context_docs: list[LCDocument]) -> str:
        """
        Run the QA chain against a list of relevant documents.
        Returns the answer string.
        """
        if not question.strip():
            raise ValueError("Question cannot be empty.")
        if not context_docs:
            raise LLMError("No context documents provided.")

        try:
            logger.info(f"Querying LLM: '{question[:80]}…'")
            response = self._chain.invoke(
                {"input_documents": context_docs, "question": question},
                return_only_outputs=True,
            )
            answer = response.get("output_text", "").strip()
            logger.info("LLM response received.")
            return answer
        except Exception as exc:
            raise LLMError(str(exc)) from exc

    # ── Private helpers ───────────────────────────────────────────────────

    def _build_chain(self):
        logger.info(f"Initialising LLM '{settings.llm.model_name}'…")
        try:
            llm = ChatGroq(
                groq_api_key=settings.llm.api_key,
                model_name=settings.llm.model_name,
                temperature=settings.llm.temperature,
            )
            prompt = PromptTemplate(
                template=_PROMPT_TEMPLATE,
                input_variables=["context", "question"],
            )
            chain = load_qa_chain(llm=llm, chain_type="stuff", prompt=prompt)
            logger.info("LLM chain ready.")
            return chain
        except Exception as exc:
            raise ConfigurationError(f"Failed to build LLM chain: {exc}") from exc
