#chat_agent.py
import os
import json
import re
from config import *
from utils import *
from tools import *
import time

def run_agent_graph(intrebare_utilizator, memory):

    total_start = time.perf_counter()

    print("\n" + "-" * 50)

    index_content = read_wiki_pages(["index.md"])
    memory_text = ""

    for item in memory:
        memory_text += f"""
        Întrebare:
        {item['question']}
        Rezumat:
        {item['answer_summary']}
        """

    tool_results = []

    for step in range(MAX_AGENT_STEPS):

        print(f"\nPasul {step + 1}")

        if step == 0:

            prompt = f"""
                ISTORIC:
                {memory_text}
                ÎNTREBARE:
                {intrebare_utilizator}
                INDEX WIKI:
                {index_content}
                """

        elif step == MAX_AGENT_STEPS - 1:

            prompt = f"""
                ISTORIC:
                {memory_text}
                ÎNTREBARE:
                {intrebare_utilizator}
                REZULTATE TOOL-URI:
                {chr(10).join(tool_results)}
                ATENȚIE:
                Acesta este ultimul pas disponibil.
                Nu mai apela niciun tool.
                Folosește exclusiv informațiile deja obținute și oferă răspunsul final.
                Răspunde obligatoriu în formatul:
                Răspuns:
                ...
                """

        else:

            prompt = f"""
                ISTORIC:
                {memory_text}
                ÎNTREBARE:
                {intrebare_utilizator}
                REZULTATE TOOL-URI:
                {chr(10).join(tool_results)}
                """

        messages = [
            {
                "role": "system",
                "content": AGENT_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        llm_start = time.perf_counter()

        response = client.chat(
            model=MODEL_NAME,
            messages=messages
        )

        llm_time = time.perf_counter() - llm_start
        print(f"⏱️ LLM Step {step+1}: {llm_time:.2f}s")

        ai_output = response["message"]["content"]

        print(ai_output)

        # ---------------------------------
        # Final answer
        # ---------------------------------

        if "Răspuns:" in ai_output:

            raspuns_final = ai_output.split(
                "Răspuns:", 1
            )[1].strip()

            summary_start = time.perf_counter()

            summary = summarize_answer(
                intrebare_utilizator,
                raspuns_final
            )

            memory = add_memory(
                memory,
                intrebare_utilizator,
                summary
            )

            summary_time = time.perf_counter() - summary_start
            print(f"⏱️ Summary model: {summary_time:.2f}s")

            total_time = time.perf_counter() - total_start
            print(f"✅ Total response time: {total_time:.2f}s")

            return raspuns_final, memory

        # ---------------------------------
        # Tool calls
        # ---------------------------------

        tool_matches = TOOL_PATTERN.findall(ai_output)
        
        if step == MAX_AGENT_STEPS - 1:
            print("⚠️ Modelul a încercat să apeleze tool-uri la ultimul pas.")
            return "Îmi pare rău, nu am reușit să formulez un răspuns.", memory

        for tool_text in tool_matches:

            tool_start = time.perf_counter()

            result = execute_tool(tool_text)

            tool_time = time.perf_counter() - tool_start

            print(f"⏱️ Tool execution: {tool_time:.2f}s")

            tool_results.append(
                f"""
                    TOOL:
                    {tool_text}
                    REZULTAT:
                    {result}
                    """
            )

    print("\n⚠️ S-a atins limita de pași.")

    return "Îmi pare rău, nu am reușit să formulez un răspuns.", memory


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