#!/usr/bin/env python3
"""Debug Supabase connection with different approaches."""

import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

print("=" * 60)
print("DEBUG: Supabase Connection - Alternative Approaches")
print("=" * 60)

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

# Try different import approaches
print("\nApproach 1: Direct import")
try:
    from supabase import create_client, Client
    client = create_client(url, key)
    print("  SUCCESS: Direct import worked!")
except Exception as e:
    print(f"  FAILED: {e}")

print("\nApproach 2: Import individual components")
try:
    from supabase.client import Client as SupabaseClient
    from supabase.lib.client_options import ClientOptions
    
    # Try with minimal options
    options = ClientOptions()
    client = SupabaseClient(url, key, options)
    print("  SUCCESS: Individual components worked!")
except Exception as e:
    print(f"  FAILED: {e}")

print("\nApproach 3: Check library version and dependencies")
try:
    import supabase
    print(f"  Supabase version: {supabase.__version__ if hasattr(supabase, '__version__') else 'unknown'}")
    
    import gotrue
    print(f"  Gotrue version: {gotrue.__version__ if hasattr(gotrue, '__version__') else 'unknown'}")
    
    import httpx
    print(f"  Httpx version: {httpx.__version__ if hasattr(httpx, '__version__') else 'unknown'}")
    
except Exception as e:
    print(f"  FAILED to check versions: {e}")

print("=" * 60)
