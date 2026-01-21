#!/usr/bin/env python3
"""Test direct HTTP request to Supabase."""

import os
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()

print("=" * 60)
print("DEBUG: Direct HTTP Request Test")
print("=" * 60)

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print(f"\nTesting direct HTTP request to: {url}")

try:
    # Test a simple query using requests
    endpoint = url.rstrip('/') + '/rest/v1/model_rankings'
    
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'select': '*'
    }
    
    print(f"Endpoint: {endpoint}")
    print(f"Headers: {headers}")
    
    response = requests.get(endpoint, headers=headers, params=params)
    
    print(f"\nResponse status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("  SUCCESS: Direct HTTP request worked!")
    else:
        print("  FAILED: Direct HTTP request failed")
        
except Exception as e:
    print(f"  FAILED: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
