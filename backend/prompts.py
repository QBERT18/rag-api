SYSTEM_PROMPT = (
    "You are a helpful assistant. Use the provided context when relevant. "
    "If the context doesn't answer the question, say so. "
    "Maintain continuity with the prior conversation."
)

CONTEXT_TEMPLATE = """Context:
{context}

Question: {question}"""
