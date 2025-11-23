"""
Prompts for synthetic data generation.
"""

GENERATE_QA_PROMPT = """
You are an expert at creating evaluation datasets for RAG (Retrieval-Augmented Generation) systems.
Your task is to generate a high-quality Question-Answer pair based STRICTLY on the provided context.

Context:
{context}

Instructions:
1. Create a clear, specific question that can be answered using ONLY the information in the context.
2. Provide the answer to the question. The answer must be accurate and directly supported by the context.
3. The question should be challenging enough to test a retrieval system (not just keyword matching).

Output Format (JSON):
{{
    "question": "The generated question",
    "answer": "The answer based on the context"
}}
"""

EVOLVE_QUESTION_PROMPT = """
You are an expert at making questions more challenging for AI systems.
Your task is to rewrite the following question to make it more complex, while ensuring it can still be answered by the same context.

Original Question: {question}
Context: {context}

Evolution Type: {evolution_type}
(Options: Reasoning, Multi-hop, Conditional)

Instructions:
1. Rewrite the question to require {evolution_type}.
2. Ensure the answer is still fully supported by the context.
3. Update the answer if necessary to match the new question complexity.

Output Format (JSON):
{{
    "question": "The evolved question",
    "answer": "The updated answer"
}}
"""
