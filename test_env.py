#!/usr/bin/env python3
"""Test environment variable loading."""

import os
from dotenv import load_dotenv

print("🧪 Testing environment variable loading...")

# Load .env file
load_dotenv()

# Check variables
neon_conn = os.getenv('NEON_CONNECTION_STRING')
openai_key = os.getenv('OPENAI_API_KEY')
serper_key = os.getenv('SERPER_API_KEY')

print(f"NEON_CONNECTION_STRING: {'✅ Found' if neon_conn else '❌ Missing'}")
if neon_conn:
    masked = neon_conn[:30] + "..." + neon_conn[-20:]
    print(f"   Value: {masked}")

print(f"OPENAI_API_KEY: {'✅ Found' if openai_key else '❌ Missing'}")
if openai_key:
    print(f"   Value: {openai_key[:20]}...")

print(f"SERPER_API_KEY: {'✅ Found' if serper_key else '❌ Missing'}")
if serper_key:
    print(f"   Value: {serper_key[:20]}...")

if neon_conn and openai_key and serper_key:
    print("\n🎉 All required environment variables are loaded!")
else:
    print("\n❌ Some environment variables are missing")