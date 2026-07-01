#chat_agent.py
import os
import json
import re
from config import *
from utils import *
from tools import *
import time

def run_agent_graph(intrebare_utilizator):

    total_start = time.perf_counter()
    
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

    # Include index content only in the first message
    initial_prompt = f"""
        ISTORIC:

        {memory_text}

        ÎNTREBARE:

        {intrebare_utilizator}

        INDEX WIKI:

        {index_content}
        """

    messages = [
        {
            "role": "system",
            "content": AGENT_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": initial_prompt
        }
    ]

    for step in range(MAX_AGENT_STEPS):

        print(f"\nPasul {step+1}")

        llm_start = time.perf_counter()

        response = client.chat(
            model=MODEL_NAME,
            messages=messages
        )

        llm_time = time.perf_counter() - llm_start
        print(f"⏱️ LLM Step {step+1}: {llm_time:.2f}s")

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

            summary_start = time.perf_counter()

            summary = summarize_answer(
                intrebare_utilizator,
                raspuns_final
            )

            summary_time = time.perf_counter() - summary_start
            print(f"⏱️ Summary model: {summary_time:.2f}s")

            add_memory(
                intrebare_utilizator,
                summary
            )

            # print(
            #     "\n"
            #     + "=" * 20
            #     + " RĂSPUNS FINAL "
            #     + "=" * 20
            # )

            # print(raspuns_final)
            # print("=" * 60)
            total_time = time.perf_counter() - total_start
            print(f"✅ Total response time: {total_time:.2f}s")

            return raspuns_final

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
            return ai_output

        for tool_text in tool_matches:

            print(
                "\n🔧 Execut tool..."
            )
            
            tool_start = time.perf_counter()
            result = execute_tool(tool_text)
            tool_time = time.perf_counter() - tool_start
            print(f"⏱️ Tool execution: {tool_time:.2f}s")

            # print(
            #     "\n📄 Rezultat tool:"
            # )
            # print(
            #     result[:1000]
            # )

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

    clear_memory_on_start()

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