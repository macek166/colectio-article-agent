# Google Cloud Setup - Krok za krokem

## 🎯 Cíl
Nastavit Google Drive API pro automatické ukládání článků do tvé Google Drive složky.

## 📋 Krok 1: Vytvoření Google Cloud Projektu

### 1.1 Přejdi na Google Cloud Console
- Otevři: https://console.cloud.google.com/
- Přihlaš se svým Google účtem

### 1.2 Vytvoř nový projekt
1. Klikni na dropdown s názvem projektu (nahoře vlevo)
2. Klikni "New Project"
3. Zadej název: **"TCG Content Generator"**
4. Klikni "Create"
5. Počkej, až se projekt vytvoří (1-2 minuty)

### 1.3 Vyber projekt
- Ujisti se, že máš vybraný správný projekt v dropdownu

## 📋 Krok 2: Povolení Google Drive API

### 2.1 Přejdi na API Library
- Jdi na: https://console.cloud.google.com/apis/library
- Nebo v menu: APIs & Services → Library

### 2.2 Najdi a povol Google Drive API
1. Do vyhledávání zadej: **"Google Drive API"**
2. Klikni na "Google Drive API" (od Google)
3. Klikni **"Enable"**
4. Počkaj, až se API povolí

## 📋 Krok 3: Vytvoření OAuth 2.0 Credentials

### 3.1 Přejdi na Credentials
- Jdi na: https://console.cloud.google.com/apis/credentials
- Nebo v menu: APIs & Services → Credentials

### 3.2 Konfigurace OAuth Consent Screen (pokud je potřeba)
Pokud vidíš upozornění o OAuth consent screen:

1. Klikni "Configure Consent Screen"
2. Vyber **"External"** (pokud nemáš Google Workspace)
3. Vyplň povinné údaje:
   - **App name**: TCG Content Generator
   - **User support email**: tvůj email
   - **Developer contact**: tvůj email
4. Klikni "Save and Continue"
5. Na stránce "Scopes" klikni "Save and Continue"
6. Na stránce "Test users" přidej svůj email
7. Klikni "Save and Continue"

### 3.3 Vytvoření OAuth 2.0 Client ID
1. Klikni **"Create Credentials"**
2. Vyber **"OAuth 2.0 Client IDs"**
3. Application type: **"Desktop application"**
4. Name: **"TCG Content Generator Desktop"**
5. Klikni **"Create"**

### 3.4 Stažení credentials
1. Po vytvoření se zobrazí dialog s Client ID a Secret
2. Klikni **"Download JSON"**
3. Soubor se stáhne (obvykle do Downloads)
4. **DŮLEŽITÉ**: Přejmenuj soubor na `credentials.json`

## 📋 Krok 4: Umístění credentials souboru

### 4.1 Zkopíruj credentials.json
1. Najdi stažený soubor (obvykle v Downloads)
2. Přejmenuj ho na **`credentials.json`** (pokud už není)
3. Zkopíruj ho do root složky tvého projektu
4. Měl by být ve stejné složce jako `app.py`, `requirements.txt`, atd.

### 4.2 Ověř umístění
Tvá struktura by měla vypadat takto:
```
colectio-article-agent/
├── credentials.json          ← NOVÝ SOUBOR
├── .env
├── app.py
├── requirements.txt
├── setup_google_drive.py
└── ...
```

## 📋 Krok 5: Aktualizace .gitignore

### 5.1 Přidej do .gitignore
Otevři `.gitignore` a přidej tyto řádky:
```
# Google Drive credentials (NEVER COMMIT!)
credentials.json
token.json
```

## 📋 Krok 6: Test setupu

### 6.1 Nainstaluj závislosti
```bash
pip install -r requirements.txt
```

### 6.2 Spusť Google Drive setup
```bash
python setup_google_drive.py
```

### 6.3 Co se stane:
1. Otevře se prohlížeč
2. Přihlaš se do Google účtu
3. Povolíš přístup k Google Drive
4. Setup vytvoří složky a otestuje upload

## 🔒 Bezpečnostní poznámky

### ⚠️ NIKDY necommituj:
- `credentials.json` - obsahuje tajné klíče
- `token.json` - obsahuje přístupové tokeny

### ✅ Bezpečné praktiky:
- Credentials jsou pouze lokálně
- Token se automaticky obnovuje
- Přístup pouze k souborům, které aplikace vytvoří

## 🎯 Výsledek

Po dokončení budeš mít:
- ✅ Google Cloud projekt s Drive API
- ✅ OAuth credentials pro desktop aplikaci
- ✅ Automatické ukládání článků do Google Drive
- ✅ Organizované složky podle kategorií a dat

## 🆘 Řešení problémů

### Problém: "OAuth consent screen not configured"
**Řešení**: Dokončit krok 3.2 (OAuth Consent Screen)

### Problém: "credentials.json not found"
**Řešení**: Zkontrolovat umístění souboru v root složce

### Problém: "Access denied"
**Řešení**: Přidat svůj email do test users (krok 3.2)

### Problém: Browser se neotevře
**Řešení**: Zkopírovat URL z terminálu a otevřít manuálně

---

**Až budeš mít credentials.json, spusť: `python setup_google_drive.py`**