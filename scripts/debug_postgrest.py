#!/usr/bin/env python3
"""Test direct postgrest connection (bypassing supabase client)."""

import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

print("=" * 60)
print("DEBUG: Direct Postgrest Connection Test")
print("=" * 60)

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print(f"\nConnecting to: {url}")

try:
    from postgrest import PostgrestClient
    
    # Parse URL to get endpoint
    if url.startswith('https://'):
        endpoint = url.replace('https://', '')
    elif url.startswith('http://'):
        endpoint = url.replace('http://', '')
    else:
        endpoint = url
    
    # Remove trailing slash
    endpoint = endpoint.rstrip('/')
    
    print(f"Using endpoint: {endpoint}")
    
    # Create postgrest client
    client = PostgrestClient(f"https://{endpoint}")
    client.headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
    
    print("  SUCCESS: Postgrest client created!")
    
    # Test connection by querying a table
    print("\nTesting connection with simple query...")
    result = client.table('model_rankings').select('*').limit(1).execute()
    
    print(f"  SUCCESS: Query executed!")
    print(f"  Result: {result.data if hasattr(result, 'data') else result}")
    
except Exception as e:
    print(f"  FAILED: {e}")
    print(f"  Type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("=" * 60)
