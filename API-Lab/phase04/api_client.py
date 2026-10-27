import os
from pathlib import Path
import requests
from dotenv import load_dotenv

# =============================================================================
# Task 16: Public vs Protected API
# =============================================================================
"""
Task 16 Comparison: Public API vs Protected API

Question: Create a short comparison between a public API and a protected API covering:
1. Whether credentials are required
2. Why authentication is used
3. Example authentication mechanism
4. What happens when credentials are invalid

Answer:
---------------------------------------------------------------------------------------------------------
Feature                      Public API                               Protected API
---------------------------------------------------------------------------------------------------------
Credentials Required         No credentials required. Open for anyone Credentials required (e.g., API key,
                             to query publicly without signing in.     bearer token, or OAuth secret).

Purpose / Why Used           Designed for public, non-sensitive data   Used to verify user identity, control
                             (e.g., public weather or test data).     access to sensitive resources, enforce
                                                                      rate limits, and prevent malicious abuse.

Example Mechanism            No auth headers needed; direct GET       Bearer Token header (`Authorization: Bearer <TOKEN>`),
                             request to the URL endpoint.             API Key header (`X-API-Key: <KEY>`), or OAuth 2.0.

Invalid Credentials Result   Not applicable (or access remains open   The server rejects the request and returns
                             unless IP-level throttling triggers).    HTTP 401 Unauthorized or HTTP 403 Forbidden.
---------------------------------------------------------------------------------------------------------
"""

def sanitize_token(token: str) -> str:
    """Masks secret tokens for safe terminal logging and auditing."""
    if not token or len(token) <= 6:
        return "***"
    return f"{token[:4]}...{token[-3:]}"

def main():
    print("=" * 60)
    print("   PHASE 04: AUTHENTICATION, API KEYS & SECURE CONFIG")
    print("=" * 60)

    # Print Task 16 summary to console
    print("\n--- Task 16: Public vs Protected API ---")
    print("Conceptual comparison between Public and Protected APIs documented in source comments.")
    print("Key distinction: Public APIs require no credentials, whereas Protected APIs enforce")
    print("identity verification via tokens/keys and reject unauthorized requests with HTTP 401/403.")

    # =========================================================================
    # Task 17: Implement an Authorization Header
    # =========================================================================
    print("\n--- Task 17: Implement an Authorization Header ---")
    
    # Representative dummy token (do not use real credentials)
    sample_token = "dummy_secret_jwt_token_xyz987"
    
    # Construct request headers following the standard 'Authorization: Bearer TOKEN' pattern
    headers = {
        "Authorization": f"Bearer {sample_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Create sanitized headers dictionary for safe display
    sanitized_headers = {
        k: (f"Bearer {sanitize_token(sample_token)}" if k == "Authorization" else v)
        for k, v in headers.items()
    }
    
    print("Constructed Request Headers (Sanitized for logging):")
    for key, value in sanitized_headers.items():
        print(f"  {key}: {value}")
        
    # Send demonstration request with headers to a public endpoint
    test_url = "https://jsonplaceholder.typicode.com/posts/1"
    response = requests.get(test_url, headers=headers)
    print(f"Test request to {test_url} dispatched with Authorization header.")
    print(f"Response Status Code: {response.status_code} (Success)")

    # =========================================================================
    # Task 18: Move Credentials to .env
    # =========================================================================
    print("\n--- Task 18: Move Credentials to .env ---")
    
    load_dotenv()
    
    # Retrieve the key securely from the environment
    api_key = os.getenv("API_KEY")
    
    if not api_key:
        print("[ERROR] API_KEY environment variable was not found in .env!")
    else:
        print("API_KEY successfully loaded from environment (.env).")
        print(f"Sanitized API_KEY value: {sanitize_token(api_key)}")
        
        # Build headers using the environment variable
        auth_headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Client-Version": "1.0.0"
        }
        
        # Prepare and log sanitized configuration
        sanitized_auth_headers = {
            k: (f"Bearer {sanitize_token(api_key)}" if k == "Authorization" else v)
            for k, v in auth_headers.items()
        }
        print("Sanitized Request Configuration using loaded .env key:")
        for h_key, h_val in sanitized_auth_headers.items():
            print(f"  {h_key}: {h_val}")
            
        # Verify Git exclusion
        gitignore_path = Path(__file__).parent / ".gitignore"
        if gitignore_path.exists():
            content = gitignore_path.read_text(encoding="utf-8")
            is_ignored = ".env" in content
            print(f"Security Check: .env is listed in .gitignore? -> {is_ignored}")

    print("\n" + "=" * 60)
    print("   PHASE 04 COMPLETED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    main()
