# 🃏 Colectio Article Agent - TCG Content Generator

Tento projekt je automatizovaný **agentní systém** určený pro generování vysoce kvalitního obsahu o sběratelských kartách (Pokémon, Hokej, Fotbal). Agent vyhledává novinky, stahuje zdroje, píše články, edituje je a archivuje do databáze a na Google Drive.

---

## 🏗️ 1. Jak agent funguje (Architektura)

Systém využívá architekturu **CrewAI** k orchestraci několika specializovaných AI agentů, kteří spolupracují na vytvoření článku. Celý proces je řízen `Orchestratorem` a má 4 hlavní fáze:

### 🔄 Fáze 1: Strategie a Výzkum (Strategist & Researcher)
1.  **Strategist Agent:**
    *   Podívá se na internet (přes `SerperDevTool`) na nejnovější trendy a novinky v dané kategorii (např. "latest pokemon card news").
    *   Zkontroluje databázi (dříve vygenerovaná témata), aby nedělal duplicity.
    *   Navrhne nová témata pro články.
2.  **Researcher Agent:**
    *   Pro vybrané téma provede hloubkový průzkum.
    *   Najde nejlepší zdrojový článek (Master Source URL).
    *   Stáhne **plný obsah** zdrojového článku a extrahuje klíčová fakta a investiční postřehy.

### ✍️ Fáze 2: Psaní (Writer)
3.  **Writer Agent:**
    *   Dostane zadání a **originální text zdroje**.
    *   Funguje jako překladatel a adaptér – nevymýšlí si obsah, ale věrně převádí informace do češtiny.
    *   Strukturovaně formátuje článek (Nadpis, Úvod, Hlavní body, Závěr, Zdroje).
    *   **Pravidlo:** Musí vždy uvést odkaz na původní zdroj na začátku článku.

### 📝 Fáze 3: Editace (Editor)
4.  **Editor Agent:**
    *   Přečte si návrh od Writera.
    *   Kontroluje čtivost, gramatiku a tón (odborný, ale přístupný).
    *   Vylepšuje formátování a nadpisy.

### 💾 Fáze 4: Archivace (Archivist)
5.  **Archivist Agent:**
    *   Uloží finalizovaný článek do databáze **Neon (PostgreSQL)**.
    *   Nahraje článek jako Google Doc do příslušné složky na **Google Drive** (např. `TCG Articles/Pokemon/2026-02`).
    *   Uloží metadata (klíčová slova, zdroje, statistiky).

---

## 🛠️ 2. Co je k tomu potřeba (Prerekvizity)

Aby systém fungoval, potřebuje přístup k následujícím službám a API klíčům:

### 🧠 AI Modely
*   **OpenAI API Key** (`OPENAI_API_KEY`): Používá se model `gpt-4o` pro agenty (psaní, editace).

### 🔍 Vyhledávání a Data
*   **Serper.dev API Key** (`SERPER_API_KEY`): Slouží k vyhledávání na Google (Searching) a získávání novinek. Bez něj agent nenajde žádné zdroje.
    *   *Dashboard:* [https://serper.dev/dashboard](https://serper.dev/dashboard)

### 🗄️ Databáze
*   **Neon Database** (`NEON_CONNECTION_STRING`): PostgreSQL databáze pro ukládání témat, článků a historie, aby se nepsalo to samé dvakrát.

### ☁️ Google Integrace
*   **Google Drive API:**
    *   `credentials.json`: Soubor s OAuth 2.0 credentials pro přístup k Drive API.
    *   `token.json`: Soubor s tokenem (vygeneruje se automaticky po prvním přihlášení).
    *   Potřeba mít povolené API a nasdílenou složku `TCG Articles`.

### 💻 Prostředí
*   **Python 3.10+** (doporučeno 3.11 nebo 3.12).
*   **Streamlit:** Pro běh webového rozhraní.

---

## 🚀 3. Jak nasadit jinde (Deployment Guide)

Pokud chcete agenta spustit na novém počítači nebo serveru, postupujte takto:

### Krok 1: Příprava prostředí
1.  **Stáhněte kód** z repozitáře.
2.  Nainstalujte Python (pokud nemáte).
3.  Vytvořte virtuální prostředí (doporučeno):
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate
    ```
4.  Nainstalujte závislosti:
    ```bash
    pip install -r requirements.txt
    ```

### Krok 2: Konfigurace
1.  Ve složce projektu zkopírujte soubor `.env.example` na `.env`:
    ```bash
    cp .env.example .env
    ```
2.  Otevřete `.env` a vyplňte své API klíče (OpenAI, Serper, Neon).
3.  Ujistěte se, že máte ve složce soubor `credentials.json` pro Google Drive (pokud chcete nahrávat na Drive).

### Krok 3: Spuštění
1.  Spusťte aplikaci příkazem:
    ```bash
    streamlit run app.py
    ```
2.  Otevře se prohlížeč na adrese `http://localhost:8501`.
3.  Na postranním panelu vyberte kategorie a počet článků a klikněte na **"Spustit generování"**.

---

## 📊 4. Ucelený přehled souborů

*   `app.py`: Hlavní vstupní bod aplikace (Streamlit UI).
*   `src/orchestrator.py`: Mozek aplikace, řídí tok mezi agenty.
*   `src/agents/`: Složka s definicemi jednotlivých agentů (`strategist.py`, `researcher.py`, `writer.py`, `editor.py`, `archivist.py`).
*   `src/tools/`: Nástroje, které agenti používají (`seo_tools.py` pro hledání, `neon_client.py` pro DB).
*   `src/config/`: Nastavení a prompty (`web_sources.py` obsahuje seznam URL, `writing_styles.py` definuje styly psaní).
*   `.env`: **Vaše tajná hesla a klíče.** (Nikdy neposílejte nikomu cizímu!)
