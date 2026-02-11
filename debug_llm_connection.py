
import os
import sys
from dotenv import load_dotenv
import openai
import anthropic

# Load environment variables
load_dotenv()


# Redirect stdout to file
log_file = open("debug_results.log", "w", encoding="utf-8")

def log(msg):
    print(msg)
    log_file.write(msg + "\n")
    log_file.flush()

def test_openai():
    log("\n--- Testing OpenAI ---")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        log("FAIL: OPENAI_API_KEY not found in .env")
        return
    
    log(f"API Key found: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # Test models
        models = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        
        for model in models:
            log(f"Testing model: {model} ...")
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                log(f"OK")
            except Exception as e:
                log(f"FAIL: {str(e)}")

    except Exception as e:
        log(f"Client Init Failed: {e}")

def test_anthropic():
    log("\n--- Testing Anthropic ---")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        log("FAIL: ANTHROPIC_API_KEY not found in .env")
        return

    log(f"API Key found: {api_key[:15]}...")
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Test models - prioritized order
        models = [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-latest", 
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307"
        ]
        
        for model in models:
            log(f"Testing model: {model} ...")
            try:
                response = client.messages.create(
                    model=model,
                    max_tokens=5,
                    messages=[{"role": "user", "content": "Hello"}]
                )
                log(f"OK")
            except anthropic.NotFoundError:
                log(f"FAIL: Not Found (404)")
            except anthropic.AuthenticationError:
                log(f"FAIL: Auth Error (401)")
            except anthropic.BadRequestError as e:
                log(f"FAIL: Bad Request: {e}")
            except Exception as e:
                log(f"FAIL: Error: {str(e)}")

    except Exception as e:
        log(f"Client Init Failed: {e}")

if __name__ == "__main__":
    try:
        test_openai()
        test_anthropic()
    finally:
        log_file.close()

