#utils.py
import os
import json
from config import *
from config import client, MODEL_NAME

def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return []

    with open(
        MEMORY_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)
    
def save_memory(memory):

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            memory,
            f,
            ensure_ascii=False,
            indent=2
        )

def add_memory(question, answer):

    memory = load_memory()

    memory.append({
        "question": question,
        "answer_summary": answer
    })

    memory = memory[-MAX_MEMORY_ITEMS:]

    save_memory(memory)

def summarize_answer(
    question,
    answer
):

    response = client.chat(
        model=MODEL_NAME,
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