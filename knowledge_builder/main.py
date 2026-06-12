# main.py
from config import *
from tools import *
from utils import *
import os
from ollama import Client

def run_agent_loop(
    client,
    faculty_context,
    raw_filename,
    raw_content
):
    messages = []

    index_content = ""

    index_path = os.path.join(WIKI_DIR, "index.md")

    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            index_content = f.read()

    user_context = f"""
    FACULTATE:
    {faculty_context}

    FIȘIER BRUT:
    {raw_filename}

    CONȚINUT BRUT:
    {raw_content}

    INDEX CURENT:
    {index_content}
    """

    messages.append({
        "role": "user",
        "content": user_context
    })

    for step in range(MAX_AGENT_STEPS):

        print(f"   🤖 Agent step {step+1}")

        response = client.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                *messages
            ],
            options={
                "temperature": 0.2
            }
        )

        assistant_text = response["message"]["content"]

        print(assistant_text)

        messages.append({
            "role": "assistant",
            "content": assistant_text
        })

        if "<done/>" in assistant_text:
            print("   ✅ Agent finished")
            return True

        tool_matches = TOOL_PATTERN.findall(assistant_text)

        if not tool_matches:
            print("   ❌ No tool call detected")
            return False

        for tool_content in tool_matches:
            tool_result = execute_tool(
                tool_content.strip()
            )
            if ("[!WARNING]" in tool_result or tool_result.startswith("❌")):
                log_error(
                    f"{raw_filename}\n"
                    f"{tool_result}\n"
                )
            messages.append({
                "role": "tool",
                "content": tool_result
            })

    print("   ⚠️ Max steps reached")

    return False

def compile_knowledge_base():

    os.makedirs(WIKI_DIR, exist_ok=True)

    processed_files = set()

    if os.path.exists(PROCESSED_LOG):
        with open(PROCESSED_LOG, "r", encoding="utf-8") as f:
            processed_files = {
                line.strip()
                for line in f
                if line.strip()
            }

    client = Client(
        host="http://localhost:11435"
    )

    raw_files = [
        f
        for f in os.listdir(RAW_DIR)
        if f.endswith(".md")
    ]

    for file_name in raw_files:

        if file_name in processed_files:
            print(f"⏩ Skipping {file_name}")
            continue

        prefix = file_name.split("_")[0].lower()

        faculty_context = FACULTY_MAP.get(
            prefix,
            f"Facultate Necunoscută ({prefix})"
        )

        print(f"\n🔄 {file_name}")
        print(f"📌 {faculty_context}")

        try:

            with open(
                os.path.join(RAW_DIR, file_name),
                "r",
                encoding="utf-8"
            ) as f:

                raw_content = f.read()

            success = run_agent_loop(
                client,
                faculty_context,
                file_name,
                raw_content
            )

            if success:

                with open(
                    PROCESSED_LOG,
                    "a",
                    encoding="utf-8"
                ) as f:

                    f.write(file_name + "\n")

                processed_files.add(file_name)

            else:
                log_error(
                    f"FAILED FILE: {file_name}"
                )
                continue

        except Exception as e:

            log_error(
                f"EXCEPTION {file_name}: {str(e)}"
            )
            continue

if __name__ == "__main__":
    compile_knowledge_base()
    print("✅ Knowledge base process evaluated.")