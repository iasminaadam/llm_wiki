#utils.py
import os
from config import *
from config import client, MODEL_NAME
    
def add_memory(memory, question, answer):
    memory.append({
        "question": question,
        "answer_summary": answer
    })

    return memory[-MAX_MEMORY_ITEMS:]

def summarize_answer(
    question,
    answer
):

    response = client.chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "system",
                "content": """
                Rezumă răspunsul în maximum 2 propoziții.
                """
            },
            {
                "role": "user",
                "content": f"""
                Întrebare:
                {question}

                Răspuns:
                {answer}
                """
            }
        ]
    )

    return response["message"]["content"]

