import os
import json
import re
from ollama import Client

WIKI_DIR = "wiki/wiki"
MODEL_NAME = "qwen2.5:32b"
client = Client(host='http://localhost:11435')

MEMORY_FILE = "memory.json"
MAX_MEMORY_ITEMS = 5

def citeste_pagina(nume_fisier):
    """Deschide și citește o pagină din Wiki."""
    # Curățăm spațiile și ghilimelele rătăcite
    nume_fisier = nume_fisier.strip(" '\"")
    
    if not nume_fisier.endswith('.md'):
        nume_fisier += '.md'
        
    cale_fisier = os.path.join(WIKI_DIR, nume_fisier)
    
    if os.path.exists(cale_fisier):
        with open(cale_fisier, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return f"❌ Eroare: Pagina '{nume_fisier}' nu există în Wiki."
    
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

AGENT_SYSTEM_PROMPT = """
Ești un Asistent Academic Inteligent. Sarcina ta este să răspunzi la întrebările utilizatorului folosind EXCLUSIV informațiile din Wiki-ul local.

Sistemul îți va furniza de la început conținutul fișierului `index.md` (harta grafului).
Pentru a găsi informații detaliate, poți cere deschiderea unuia sau mai multor fișiere Markdown în aceeași etapă.

Formatul tău de gândire trebuie să respecte cu strictețe acești pași:

Gândire: Ce informație îmi lipsește pe baza a ce am citit deja? Ce fișier(e) trebuie să consult din index?
Acțiune: fisier1.md, fisier2.md

Când ai adunat toate informațiile necesare, formulează răspunsul final:
Răspuns: [Aici scrii răspunsul tău complet în limba română, citând paginile parcurse, ex: [[taxe_scolarizare]]]

Reguli stricte:
- La 'Acțiune:' poți lista mai multe fișiere separate prin virgulă.
- Solicită DOAR fișierele pe care le vezi menționate explicit în paginile citite anterior (ex: din index.md).
- Când ești gata să oferi concluzia, folosește DOAR cuvântul 'Răspuns:', renunțând la 'Acțiune:'.
"""

def run_agent_graph(intrebare_utilizator):
    print("\n" + "-" * 50)
    
    # Pre-încărcăm indexul din start
    continut_index = citeste_pagina("index.md")

    memory = load_memory()
    memory_text = ""
    for item in memory:
        memory_text += f"""
        Întrebare:
        {item['question']}
        Rezumat răspuns:
        {item['answer_summary']}
        """
    
    istoric_cautare = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": f"Istoric conversație: {memory_text}\n\n Întrebare: {intrebare_utilizator}\n\n[Conținutul fișierului index.md (Harta Grafului)]:\n\n{continut_index}\n\nAnalizează indexul și decide ce pagini trebuie să deschizi. Oferă o `Acțiune:` (dacă ai nevoie de detalii) sau direct un `Răspuns:` (dacă informația din index e suficientă)."}
    ]
    
    pas_curent = 1
    max_pasi = 5  # Mai puțini pași necesari, deoarece poate accesa mai multe fișiere simultan
    
    while pas_curent <= max_pasi:
        print(f"\n🧠 [Pasul {pas_curent}] AI analizează datele...")
                
        response = client.chat(model=MODEL_NAME, messages=istoric_cautare)
        ai_output = response['message']['content']
        
        # Printează logica internă a modelului
        print(ai_output)
        
        istoric_cautare.append({"role": "assistant", "content": ai_output})
        
        # Verificăm dacă oferă răspunsul final
        if "Răspuns:" in ai_output:
            print("\n✅ [Sistem] Agentul a terminat parcurgerea grafului!")
            raspuns_final = ai_output.split("Răspuns:")[-1].strip()

            summary = summarize_answer(intrebare_utilizator, raspuns_final)
            add_memory(intrebare_utilizator, summary)
            
            print("\n" + "="*20 + " RĂSPUNS FINAL " + "="*20)
            print(raspuns_final)
            print("=" * 55 + "\n")
            break
            
        # Verificăm dacă cere fișiere (Acțiune: fisier1, fisier2)
        match_actiune = re.search(r'Acțiune:\s*(.+)', ai_output)
        
        if match_actiune:
            # Extragem și procesăm lista de fișiere (separate prin virgulă)
            fisiere_brute = match_actiune.group(1).split(',')
            fisiere_solicitate = [f.strip() for f in fisiere_brute if f.strip()]
            
            print(f"       ➡️ [Sistem] Deschidem fișierele: {', '.join(fisiere_solicitate)}")
            
            continut_combinat = ""
            for fisier in fisiere_solicitate:
                continut = citeste_pagina(fisier)
                continut_combinat += f"\n--- [Conținut {fisier}] ---\n{continut}\n"
            
            istoric_cautare.append({
                "role": "user", 
                "content": f"Iată conținutul fișierelor solicitate:\n{continut_combinat}\nContinuă explorarea dacă îți mai lipsesc date, altfel formulează Răspunsul:"
            })
            pas_curent += 1
        else:
            print("\n⚠️ Format incorect. AI-ul nu a oferit nici o Acțiune validă, nici un Răspuns.")
            break

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