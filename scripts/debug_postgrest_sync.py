#!/usr/bin/env python3
"""Test synchronous postgrest connection."""

import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

print("=" * 60)
print("DEBUG: Synchronous Postgrest Connection Test")
print("=" * 60)

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print(f"\nConnecting to: {url}")

try:
    from postgrest import SyncPostgrestClient
    
    # For Supabase, we need to use the /rest/v1 endpoint
    # Remove trailing slash and add /rest/v1 with API key as URL parameter
    endpoint = url.rstrip('/') + '/rest/v1?apikey=' + key
    
    print(f"Using endpoint: {endpoint}")
    
    # Create synchronous postgrest client
    client = SyncPostgrestClient(endpoint)
    
    # Set additional headers
    client.headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
    
    print("  SUCCESS: Synchronous Postgrest client created!")
    
    # Test connection by querying a table
    print("\nTesting connection with simple query...")
    result = client.table('model_rankings').select('*').limit(1).execute()
    
    print(f"  SUCCESS: Query executed!")
    print(f"  Result: {result.data if hasattr(result, 'data') else result}")
    
    # Test inserting data
    print("\nTesting data insertion...")
    insert_result = client.table('model_rankings').insert({
        'model_name': 'test_model',
        'elo_score': 1000.00,
        'total_verifications': 1,
        'average_error': 1.5
    }).execute()
    
    print(f"  SUCCESS: Data inserted!")
    print(f"  Insert result: {insert_result.data if hasattr(insert_result, 'data') else insert_result}")
    
except Exception as e:
    print(f"  FAILED: {e}")
    print(f"  Type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("=" * 60)
