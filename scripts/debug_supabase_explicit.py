#!/usr/bin/env python3
"""Test Supabase connection with explicit configuration."""

import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

print("=" * 60)
print("DEBUG: Supabase Connection with Explicit Config")
print("=" * 60)

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print(f"\nConnecting to: {url}")

try:
    # Try importing and creating client with explicit options
    from supabase import create_client, Client
    from supabase.lib.client_options import ClientOptions
    
    # Create client options explicitly
    options = ClientOptions()
    
    # Try creating client
    print("Creating client with explicit options...")
    client = create_client(url, key, options)
    
    print("  SUCCESS: Client created!")
    
    # Test connection
    print("\nTesting connection...")
    result = client.table('model_rankings').select('*').limit(1).execute()
    
    print(f"  SUCCESS: Query executed!")
    print(f"  Result: {result.data if hasattr(result, 'data') else result}")
    
except Exception as e:
    print(f"  FAILED: {e}")
    print(f"  Type: {type(e).__name__}")
    
    # Try to get more details
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("=" * 60)
