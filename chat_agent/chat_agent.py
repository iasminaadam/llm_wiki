#chat_agent.py
import os
import json
import re
from config import *
from utils import *
from tools import *

def run_agent_graph(intrebare_utilizator):

    print("\n" + "-" * 50)

    index_content = read_wiki_pages(
        ["index.md"]
    )

    memory = load_memory()

    memory_text = ""

    for item in memory:

        memory_text += f"""
Întrebare:
{item['question']}

Rezumat:
{item['answer_summary']}
"""

    messages = [
        {
            "role": "system",
            "content": AGENT_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"""
ISTORIC:

{memory_text}

ÎNTREBARE:

{intrebare_utilizator}

INDEX WIKI:

{index_content}
"""
        }
    ]

    for step in range(MAX_AGENT_STEPS):

        print(
            f"\n🧠 Pasul {step+1}"
        )

        response = client.chat(
            model=MODEL_NAME,
            messages=messages
        )

        ai_output = response[
            "message"
        ]["content"]

        print(ai_output)

        messages.append({
            "role": "assistant",
            "content": ai_output
        })

        # -------------------------
        # răspuns final
        # -------------------------

        if "Răspuns:" in ai_output:

            raspuns_final = (
                ai_output
                .split("Răspuns:", 1)[1]
                .strip()
            )

            summary = summarize_answer(
                intrebare_utilizator,
                raspuns_final
            )

            add_memory(
                intrebare_utilizator,
                summary
            )

            print(
                "\n"
                + "=" * 20
                + " RĂSPUNS FINAL "
                + "=" * 20
            )

            print(raspuns_final)

            print("=" * 60)

            return

        # -------------------------
        # tool calls
        # -------------------------

        tool_matches = TOOL_PATTERN.findall(
            ai_output
        )

        if not tool_matches:

            print(
                "\n⚠️ Niciun tool call detectat."
            )
            return

        for tool_text in tool_matches:

            print(
                "\n🔧 Execut tool..."
            )

            result = execute_tool(
                tool_text
            )

            print(
                "\n📄 Rezultat tool:"
            )
            print(
                result[:1000]
            )

            messages.append({
                "role": "user",
                "content":
                f"""
Rezultat tool:

{result}
"""
            })

    print(
        "\n⚠️ S-a atins limita de pași."
    )
if __name__ == "__main__":
    print("🤖 Sistemul Agentic Wiki a pornit!")
    print("💡 Scrie 'exit' sau 'quit' pentru a închide programul.")
    
    while True:
        intrebare = input("\n👤 Tu: ").strip()
        
        if intrebare.lower() in ['exit', 'quit', 'ieșire']:
            print("👋 La revedere!")
            break
            
        if not intrebare:
            continue
            
        run_agent_graph(intrebare)