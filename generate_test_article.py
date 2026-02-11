import sys
from pathlib import Path
from datetime import datetime
import os

# Add src to python path to import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.google_drive_client import GoogleDriveClient

def generate_and_upload():
    print("🚀 Generuji testovací článek pro Google Docs...")
    
    # 1. Initialize client
    client = GoogleDriveClient()
    if not client.authenticate():
        print("❌ Chyba autentizace!")
        return
        
    # 2. Setup folders just in case
    client.setup_article_folders()
    
    # 3. Define sample article content (simulating Agent output)
    title = "Investiční průvodce: Charizard Base Set 1. edice"
    category = "pokemon"
    
    content = """
Úvod do investování: Charizard First Edition
===========================================

Pokud existuje jedna karta, která definuje celý sběratelský trh s Pokémony, je to Charizard z první edice Base Setu (1999). Tato karta není jen kusem kartonu; je to ikona popkultury a "svatý grál" pro sběratele po celém světě.

Historie a význam
----------------
Vydaný v roce 1999 společností Wizards of the Coast, Base Set byl prvním anglickým rozšířením Pokémon TCG. Charizard, s útočným číslem 100 HP a ikonickým útokem Fire Spin, byl okamžitě nejžádanější kartou. Verze "First Edition" je specifická malým logem (razítkem) "1st EDITION" na levé straně karty, které označuje první tiskovou várku. Navíc je tato verze tzv. "Shadowless" (bez stínu), což znamená, že obrázek Pokémona nemá na pravé straně vržený stín – designový prvek, který byl v pozdějších tiscích přidán.

Cenový vývoj
-----------
Hodnota této karty v průběhu let exponenciálně rostla.
*   **2010:** Karty ve stavu PSA 10 se prodávaly za několik tisíc dolarů.
*   **2020 (Logana Paul efekt):** Popularita explodovala. Ceny PSA 10 přesáhly 200 000 USD.
*   **Současnost:** Stabilní investiční aktivum, které si drží hodnotu lépe než mnohé akcie.

Na co si dát pozor při koupi
---------------------------
1.  **Pravost:** Existuje mnoho padělků. Vždy vyžadujte certifikaci od renomovaných společností jako PSA, BGS nebo CGC.
2.  **Stav (Condition):** I malá tečka na zadní straně (whitening) nebo jemný škrábanec na holografické fólii může srazit cenu o desítky procent.
3.  **Centering:** Jak dobře je obrázek vycentrován. Perfektní centrování je u těchto starých karet vzácné.

Závěr
-----
Vlastnit Charizarda z první edice je jako vlastnit kus historie. Ať už jste sběratel, který plní dětský sen, nebo investor hledající alternativní aktiva, tato karta představuje vrchol Pokémon TCG.
    """
    
    metadata = {
        "category": category,
        "word_count": len(content.split()),
        "research_sources": ["TCGPlayer.com", "PSA Card Facts", "Pokemon.com"],
        "keywords": ["Charizard", "Investment", "Base Set", "Shadowless"]
    }
    
    # 4. Upload
    print(f"\n📤 Nahrávám článek: '{title}'...")
    file_id = client.upload_article(title, content, category, metadata)
    
    if file_id:
        print(f"\n✅ HOTOVO! Článek byl úspěšně nahrán.")
        print(f"📄 ID souboru: {file_id}")
        print("\n👉 Nyní se podívej do svého Google Drive do složky 'TCG Articles/Pokemon'.")
        print("   Měl bys tam vidět nový Google Dokument, který můžeš rovnou editovat.")
    else:
        print("\n❌ Něco se pokazilo při nahrávání.")

if __name__ == "__main__":
    generate_and_upload()
