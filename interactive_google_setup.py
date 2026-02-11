#!/usr/bin/env python3
"""Interactive Google Cloud setup guide."""

import os
import sys
import webbrowser
from pathlib import Path

def print_header(title):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"🎯 {title}")
    print("=" * 60)

def print_step(step_num, title):
    """Print formatted step."""
    print(f"\n📋 Krok {step_num}: {title}")
    print("-" * 40)

def wait_for_user():
    """Wait for user confirmation."""
    input("\n⏸️  Stiskni ENTER až budeš hotový...")

def check_credentials_file():
    """Check if credentials file exists."""
    return os.path.exists("credentials.json")

def interactive_setup():
    """Interactive Google Cloud setup."""
    
    print_header("Google Cloud Setup - Interaktivní průvodce")
    
    print("Tento průvodce tě provede nastavením Google Drive integrace.")
    print("Budeš potřebovat:")
    print("• Google účet")
    print("• Přístup k internetu")
    print("• Cca 10 minut času")
    
    input("\n🚀 Stiskni ENTER pro začátek...")
    
    # Step 1: Google Cloud Console
    print_step(1, "Google Cloud Console")
    print("1. Otevřu ti Google Cloud Console")
    print("2. Přihlaš se svým Google účtem")
    print("3. Pokud nemáš projekt, vytvoř nový:")
    print("   - Název: 'TCG Content Generator'")
    print("   - Klikni 'Create'")
    
    try:
        webbrowser.open("https://console.cloud.google.com/")
        print("✅ Otevírám Google Cloud Console...")
    except:
        print("❌ Nepodařilo se otevřít prohlížeč")
        print("Jdi manuálně na: https://console.cloud.google.com/")
    
    wait_for_user()
    
    # Step 2: Enable Drive API
    print_step(2, "Povolení Google Drive API")
    print("1. Otevřu ti API Library")
    print("2. Vyhledej 'Google Drive API'")
    print("3. Klikni na 'Google Drive API' (od Google)")
    print("4. Klikni 'Enable'")
    
    try:
        webbrowser.open("https://console.cloud.google.com/apis/library")
        print("✅ Otevírám API Library...")
    except:
        print("❌ Nepodařilo se otevřít prohlížeč")
        print("Jdi manuálně na: https://console.cloud.google.com/apis/library")
    
    wait_for_user()
    
    # Step 3: OAuth Consent Screen
    print_step(3, "OAuth Consent Screen (pokud je potřeba)")
    print("Pokud vidíš upozornění o OAuth consent screen:")
    print("1. Klikni 'Configure Consent Screen'")
    print("2. Vyber 'External'")
    print("3. Vyplň:")
    print("   - App name: TCG Content Generator")
    print("   - User support email: tvůj email")
    print("   - Developer contact: tvůj email")
    print("4. Klikni 'Save and Continue' (3x)")
    print("5. Na 'Test users' přidej svůj email")
    
    try:
        webbrowser.open("https://console.cloud.google.com/apis/credentials/consent")
        print("✅ Otevírám OAuth Consent Screen...")
    except:
        print("❌ Nepodařilo se otevřít prohlížeč")
        print("Jdi na: APIs & Services → OAuth consent screen")
    
    wait_for_user()
    
    # Step 4: Create Credentials
    print_step(4, "Vytvoření OAuth 2.0 Credentials")
    print("1. Otevřu ti Credentials stránku")
    print("2. Klikni 'Create Credentials'")
    print("3. Vyber 'OAuth 2.0 Client IDs'")
    print("4. Application type: 'Desktop application'")
    print("5. Name: 'TCG Content Generator Desktop'")
    print("6. Klikni 'Create'")
    print("7. V dialogu klikni 'Download JSON'")
    
    try:
        webbrowser.open("https://console.cloud.google.com/apis/credentials")
        print("✅ Otevírám Credentials stránku...")
    except:
        print("❌ Nepodařilo se otevřít prohlížeč")
        print("Jdi na: APIs & Services → Credentials")
    
    wait_for_user()
    
    # Step 5: File placement
    print_step(5, "Umístění credentials souboru")
    print("1. Najdi stažený JSON soubor (obvykle v Downloads)")
    print("2. Přejmenuj ho na 'credentials.json'")
    print("3. Zkopíruj ho do této složky:")
    print(f"   {os.getcwd()}")
    print("4. Soubor by měl být vedle app.py, requirements.txt, atd.")
    
    wait_for_user()
    
    # Check if file exists
    if check_credentials_file():
        print("✅ Skvěle! credentials.json nalezen!")
    else:
        print("❌ credentials.json nenalezen!")
        print("Zkontroluj, že je soubor ve správné složce:")
        print(f"   {os.getcwd()}/credentials.json")
        
        retry = input("\n🔄 Zkusit znovu? (y/n): ").lower()
        if retry == 'y':
            if check_credentials_file():
                print("✅ Nyní credentials.json nalezen!")
            else:
                print("❌ Stále nenalezen. Zkontroluj umístění souboru.")
                return False
        else:
            print("❌ Setup přerušen. Spusť znovu až budeš mít credentials.json")
            return False
    
    # Step 6: Update .gitignore
    print_step(6, "Aktualizace .gitignore")
    
    gitignore_content = """
# Google Drive credentials (NEVER COMMIT!)
credentials.json
token.json
"""
    
    try:
        with open('.gitignore', 'r') as f:
            current_content = f.read()
        
        if 'credentials.json' not in current_content:
            with open('.gitignore', 'a') as f:
                f.write(gitignore_content)
            print("✅ .gitignore aktualizován")
        else:
            print("✅ .gitignore už obsahuje potřebné záznamy")
    except FileNotFoundError:
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("✅ .gitignore vytvořen")
    
    # Step 7: Install dependencies
    print_step(7, "Instalace závislostí")
    print("Instaluji Google Drive závislosti...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Závislosti nainstalovány")
        else:
            print("❌ Chyba při instalaci závislostí:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Chyba při instalaci: {e}")
        print("Spusť manuálně: pip install -r requirements.txt")
        return False
    
    # Step 8: Test setup
    print_step(8, "Test Google Drive setupu")
    print("Nyní spustím test Google Drive integrace...")
    print("Otevře se prohlížeč pro autentifikaci s Google.")
    
    input("\n🚀 Stiskni ENTER pro spuštění testu...")
    
    try:
        # Import and test
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from utils.google_drive_client import GoogleDriveClient
        
        client = GoogleDriveClient()
        
        print("🔐 Spouštím autentifikaci...")
        if client.authenticate():
            print("✅ Autentifikace úspěšná!")
            
            print("📁 Vytvářím složky...")
            if client.setup_article_folders():
                print("✅ Složky vytvořeny!")
                
                print("🧪 Testuji upload...")
                test_content = "Test článek pro ověření Google Drive integrace."
                file_id = client.upload_article(
                    title="Google Drive Test",
                    content=test_content,
                    category="pokemon",
                    metadata={"test": True}
                )
                
                if file_id:
                    print(f"✅ Test upload úspěšný! File ID: {file_id}")
                    print("\n🎉 Google Drive integrace je plně funkční!")
                    return True
                else:
                    print("❌ Test upload selhal")
                    return False
            else:
                print("❌ Vytvoření složek selhalo")
                return False
        else:
            print("❌ Autentifikace selhala")
            return False
            
    except Exception as e:
        print(f"❌ Test selhal: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    
    print("🎯 Google Cloud Setup - Interaktivní průvodce")
    print("=" * 60)
    
    # Check if already setup
    if check_credentials_file():
        print("✅ credentials.json už existuje!")
        test_only = input("Chceš pouze otestovat existující setup? (y/n): ").lower()
        
        if test_only == 'y':
            print("\n🧪 Spouštím pouze test...")
            try:
                sys.path.insert(0, str(Path(__file__).parent / "src"))
                from utils.google_drive_client import GoogleDriveClient
                
                client = GoogleDriveClient()
                if client.authenticate() and client.setup_article_folders():
                    print("✅ Google Drive integrace funguje!")
                    return True
                else:
                    print("❌ Test selhal")
                    return False
            except Exception as e:
                print(f"❌ Test selhal: {e}")
                return False
    
    # Run full setup
    success = interactive_setup()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 SETUP DOKONČEN ÚSPĚŠNĚ!")
        print("=" * 60)
        print("✅ Google Cloud projekt nastaven")
        print("✅ Google Drive API povoleno")
        print("✅ OAuth credentials vytvořeny")
        print("✅ Autentifikace funguje")
        print("✅ Složky vytvořeny")
        print("✅ Test upload úspěšný")
        print("\n📁 Tvé články se budou ukládat do:")
        print("   Google Drive → TCG Articles → [Kategorie] → [YYYY-MM]")
        print("\n🚀 Systém je připraven k použití!")
    else:
        print("\n" + "=" * 60)
        print("❌ SETUP SELHAL")
        print("=" * 60)
        print("Zkontroluj kroky výše a zkus znovu.")
        print("Nebo se podívej do GOOGLE_CLOUD_SETUP_GUIDE.md")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)