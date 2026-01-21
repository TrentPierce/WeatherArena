#!/usr/bin/env python3
"""Quick test to verify .env file is being loaded correctly."""

from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

print("Environment Variables Check")
print("=" * 50)

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

if url:
    # Just show the domain, not the full URL for security
    from urllib.parse import urlparse
    domain = urlparse(url).netloc if url.startswith('http') else url
    print(f"[OK] SUPABASE_URL loaded: {domain}")
else:
    print("[FAIL] SUPABASE_URL not found in .env")

if key:
    # Just show first/last few chars
    masked = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
    print(f"[OK] SUPABASE_KEY loaded: {masked}")
else:
    print("[FAIL] SUPABASE_KEY not found in .env")

print("=" * 50)

if url and key:
    print("[OK] All environment variables loaded successfully!")
    exit(0)
else:
    print("[FAIL] Missing environment variables. Please check your .env file.")
    exit(1)
