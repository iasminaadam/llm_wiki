import os
import re
from ollama import Client

RAW_DIR = "wiki/raw"
WIKI_DIR = "wiki/wiki"
MODEL_NAME = "qwen2.5:32b"
PROCESSED_LOG = "processed_files.txt"

FACULTY_MAP = {
    "ac": "Facultatea de Automatică și Calculatoare",
    "arh": "Facultatea de Arhitectură",
    "icpm": "Facultatea de Inginerie Chimică și Protecția Mediului",
    "ci": "Facultatea de Construcții și Instalații",
    "cmmi": "Facultatea de Construcții de Mașini și Management Industrial",
    "etti": "Facultatea de Electronică, Telecomunicații și Tehnologia Informației",
    "hgim": "Facultatea de Hidrotehnică, Geodezie și Ingineria Mediului",
    "ieeia": "Facultatea de Inginerie Electrică, Energetică și Informatică Aplicată",
    "mec": "Facultatea de Mecanică",
    "sim": "Facultatea de Știința și Ingineria Materialelor",
    "dima": "Facultatea de Design Industrial și Managementul Afacerilor",
    "tuiasi": "Universitate General (Informații Globale TUIASI)"
}

SYSTEM_PROMPT = """
    Ești un Arhitect de Cunoștințe (Knowledge Architect) specializat în admiterea universitară de la Universitatea Tehnică „Gheorghe Asachi” din Iași (TUIASI). 
    Misiunea ta este să analizezi un fișier brut primit și să organizezi această informație în fișiere de tip Markdown structurate în `wiki/wiki`.

    Primești de la sistem CONTEXTUL FIX (Facultatea sau zona generală) de care aparține fișierul curent.

    Urmează cu strictețe aceste reguli de arhitectură pentru a construi un Graf de Cunoștințe valid:
    
    1. LIMBA: Toate fișierele scrise în `wiki/wiki` TREBUIE să fie în limba română corectă, academică și clară. Traduci din engleză dacă este cazul.
    
    2. STRUCTURA DE INDEX MANDATORIE (`index.md`):
       La fiecare rulare, trebuie să creezi sau să actualizezi fișierul `index.md`. Acesta TREBUIE să respecte cu strictețe următoarea ierarhie de titluri. Adaugă paginile noi create EXCLUSIV sub secțiunea potrivită, fără a modifica titlurile mari preexistente:
       
       # Admitere TUIASI - Pagina Principală
       
       ## 🏛️ Informații Generale Universitate
       (Aici introduci link-uri globale, ex: [[acte_necesare_admitere]], [[calendar_general]], [[taxe_generale]])
       
       ## 🎓 Facultăți și Programe de Studiu
       (Fiecare facultate procesată trebuie să își găsească link-urile sub sub-titlul ei specific. Folosește denumirile oficiale transmise în context):
       ### [Numele Complet al Facultății primit în Context]
       * [[nume_pagina_facultate]] - Scurtă descriere a link-ului.

    3. CONECTARE ÎN GRAPH (WIKI-LINKS):
       - Introdu în text legături către alte pagini din listă folosind sintaxa [[nume_pagina]].
       - Numele fișierelor din link-uri și din tag-ul XML trebuie să fie EXCLUSIV cu litere mici și snake_case (ex: [[mec_taxe_scolarizare]], [[ac_ghid_admitere]]).
       - NU adăuga extensia .md în interiorul parantezelor pătrate.
       - Când creezi o pagină specifică unei facultăți, leag-o inteligent de paginile generale (ex: „Dosarul se depune urmând procedura din [[acte_necesare_admitere]]”).
    
    4. INCREMENTALITATE: Când primești informații noi, nu șterge structurile bune existente din fișiere, ci completează-le. Dacă apar contradicții clare între date, adaugă un bloc de avertizare: `> [!WARNING] Contradicție detectată între surse...`.
    
    5. FORMATUL REZULTATULUI: Returnează rezultatul tău împachetat în blocuri XML personalizate pentru fiecare fișier modificat sau creat, exact așa:

    <file name="index.md">
    [Conținutul complet și actualizat al indexului conform schemei]
    </file>

    <file name="abrev_pagina_noua.md">
    # Titlu Pagină
    Conținut...
    </file>
"""

def compile_knowledge_base():
    if not os.path.exists(WIKI_DIR):
        os.makedirs(WIKI_DIR)

    # --- INIȚIALIZARE CHECKPOINT SYSTEM ---
    processed_files = set()
    if os.path.exists(PROCESSED_LOG):
        with open(PROCESSED_LOG, 'r', encoding='utf-8') as f:
            processed_files = set(line.strip() for line in f if line.strip())

    raw_files = [f for f in os.listdir(RAW_DIR) if f.endswith('.md')]
    
    for file_name in raw_files:
        # Dacă fișierul a fost deja procesat complet într-o sesiune anterioară, sărim peste el
        if file_name in processed_files:
            print(f"⏩ Skipping already processed file: {file_name}")
            continue
            
        print(f"🔄 Processing: {file_name}...")
        
        # Extragem prefixul din numele fișierului (până la primul '_')
        prefix = file_name.split('_')[0].lower()
        facultate_context = FACULTY_MAP.get(prefix, f"Facultate Necunoscută ({prefix.upper()})")
        print(f"       📌 Context identificat: {facultate_context}")
        
        with open(os.path.join(RAW_DIR, file_name), 'r', encoding='utf-8') as f:
            raw_content = f.read()
            
        index_path = os.path.join(WIKI_DIR, "index.md")
        existing_index_content = ""
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                existing_index_content = f.read()
                
        existing_wiki_files = os.listdir(WIKI_DIR)
        
        # Injectăm contextul determinist direct în input-ul pentru LLM
        context_status = f"--- METADATE METRICĂ GRAF ---\n"
        context_status += f"FIȘIERUL CURENT APARȚINE DE: {facultate_context} (Prefix fișiere recomandat: '{prefix}_')\n"
        context_status += f"---------------------------------\n\n"
        context_status += f"Fișiere existente în wiki/wiki: {existing_wiki_files}\n"
        
        if existing_index_content:
            context_status += f"\nConținutul actual din index.md este:\n{existing_index_content}\n"
        
        user_input = f"{context_status}\n\nFișierul brut de procesat ACUM ({file_name}):\n\n{raw_content}"
        
        try:
            client = Client(host='http://localhost:11435')
            response = client.generate(
                model=MODEL_NAME,
                system=SYSTEM_PROMPT,
                prompt=user_input,
                options={"temperature": 0.2}
            )
            
            output_text = response['response']
            file_blocks = re.findall(r'<file name="(.*?)">(.*?)</file>', output_text, re.DOTALL)
            
            # Salvăm fișierele generate pe disc
            for target_filename, target_content in file_blocks:
                target_path = os.path.join(WIKI_DIR, target_filename.strip())
                with open(target_path, 'w', encoding='utf-8') as wf:
                    wf.write(target_content.strip())
                    print(f"  💾 File saved successfully: {target_filename}")
            
            # --- SALVARE STARE (SUCCESS CHECKPOINT) ---
            # Salvăm în log doar după ce fișierul a fost procesat de AI și scris pe disc complet fără erori
            with open(PROCESSED_LOG, 'a', encoding='utf-8') as f:
                f.write(f"{file_name}\n")
            processed_files.add(file_name)
            
        except Exception as e:
            print(f"❌ Error encountered while processing {file_name}: {e}")
            print("⚠️ Stopping process execution. You can restart the script safely anytime.")
            break

if __name__ == "__main__":
    compile_knowledge_base()
    print("✅ Knowledge base process evaluated.")