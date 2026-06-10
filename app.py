import os

import gradio as gr
from dotenv import load_dotenv
from groq import Groq

from retrieval_pipeline import build_vector_store, retrieve_chunks


MODEL_NAME = "llama-3.3-70b-versatile"

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY is missing. Add it to your .env file."
    )

groq_client = Groq(api_key=api_key)

# Build the ChromaDB collection once when the app starts.
vector_store, embedding_model = build_vector_store()


def format_context(results: list[dict]) -> str:
    """
    Format the retrieved chunks so the Groq model can use them
    as evidence when answering the user's question.
    """
    context_sections = []

    for rank, result in enumerate(results, start=1):
        metadata = result.get("metadata", {})

        title = metadata.get("title", "No title provided")
        source = metadata.get("source", "Unknown source")
        source_type = metadata.get("source_type", "Unknown source type")

        context_sections.append(
            f"""
SOURCE {rank}
Title: {title}
Source: {source}
Source Type: {source_type}
Retrieved Distance: {result["distance"]:.4f}

Content:
{result["text"]}
""".strip()
        )

    return "\n\n---\n\n".join(context_sections)


def answer_question(question: str) -> str:
    """
    Retrieve relevant dining documents and generate a grounded answer.
    """
    if not question or not question.strip():
        return "Please enter a UCSD dining question."

    retrieved_results = retrieve_chunks(
        question,
        vector_store,
        embedding_model,
    )

    context = format_context(retrieved_results)

    system_prompt = """
You are an unofficial UCSD campus dining guide.

Answer the user's question using only the retrieved source excerpts.
Do not invent facts or rely on outside knowledge.

Clearly distinguish between:
- official UCSD information
- student opinions from Reddit discussions

If the retrieved sources do not contain enough information to answer
the question, say that the collected sources do not provide enough
information.

At the end of the answer, include a short Sources section listing the
source filenames or URLs used.
""".strip()

    user_prompt = f"""
USER QUESTION:
{question}

RETRIEVED SOURCES:
{context}
""".strip()

    completion = groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.2,
    )

    return completion.choices[0].message.content


demo = gr.Interface(
    fn=answer_question,
    inputs=gr.Textbox(
        label="Ask a UCSD Dining Question",
        placeholder="Example: Where can I get deep-dish pizza?",
        lines=2,
    ),
    outputs=gr.Textbox(
        label="Unofficial UCSD Dining Guide Answer",
        lines=12,
    ),
    title="Unofficial UCSD Dining Guide",
    description=(
        "Ask a question about UCSD dining plans, campus food, "
        "Dining Dollars, Triton Cash, or student recommendations."
    ),
    examples=[
        ["Is UCSD's residential dining plan unlimited or à la carte?"],
        ["Where can students use Dining Dollars?"],
        ["Why should I save Triton Cash for academic breaks?"],
        ["Where can I get deep-dish pizza with leftover Dining Dollars?"],
        ["What ingredients can I buy for cooking in a dorm?"],
    ],
)


if __name__ == "__main__":
    demo.launch()