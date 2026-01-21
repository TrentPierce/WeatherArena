#!/usr/bin/env python3
"""Debug Supabase connection issue."""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load .env
load_dotenv()

print("=" * 60)
print("DEBUG: Supabase Connection Test")
print("=" * 60)

# Show environment
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print(f"\nEnvironment Variables:")
print(f"SUPABASE_URL: {url[:50] + '...' if url else 'None'}")
print(f"SUPABASE_KEY: {key[:20] + '...' if key else 'None'}")

# Check for proxy variables
print(f"\nProxy Environment Variables:")
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY', 'no_proxy']
for var in proxy_vars:
    value = os.getenv(var)
    if value:
        print(f"  {var}: {value}")

# Try creating client with minimal options
print(f"\nAttempting to create Supabase client...")

try:
    # Try with explicit environment clearing
    env_backup = {}
    for var in proxy_vars:
        if var in os.environ:
            env_backup[var] = os.environ[var]
            del os.environ[var]
    
    print("  Cleared proxy environment variables")
    
    client = create_client(url, key)
    print("  SUCCESS: Client created!")
    
    # Restore env vars
    for var, value in env_backup.items():
        os.environ[var] = value
    print("  Restored environment variables")
    
except Exception as e:
    print(f"  ERROR: {e}")
    print(f"  Type: {type(e).__name__}")

print("=" * 60)
