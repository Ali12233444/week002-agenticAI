"""
Final Integration Project - Task 26: Complete API Client
Combines concepts from Phases 01 to 05:
- HTTP Methods & REST Communication
- JSON Parsing and Data Extraction
- Secure Authentication via Environment Variables (.env)
- Comprehensive Error Handling (404, 401, 429, 500)
- Request Timeouts & Network Failure Resilience
- Rate Limiting Awareness
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import requests
from requests.exceptions import Timeout, ConnectionError, HTTPError, RequestException
from dotenv import load_dotenv

# =============================================================================
# Configuration & Environment Setup
# =============================================================================
# Locate .env file relative to project root or current directory
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
env_candidates = [project_root / ".env", current_dir / ".env", Path.cwd() / ".env"]

env_loaded = False
for env_path in env_candidates:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        env_loaded = True
        break

if not env_loaded:
    load_dotenv()  # Fallback to default search

API_BASE_URL = os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com").rstrip("/")
API_KEY = os.getenv("API_KEY", "dummy_default_token_xyz123")
DEFAULT_TIMEOUT = float(os.getenv("DEFAULT_TIMEOUT", "10.0"))


def sanitize_token(token: Optional[str]) -> str:
    """Masks authentication token for safe console logging."""
    if not token or len(token) <= 6:
        return "***"
    return f"{token[:4]}...{token[-3:]}"


class JSONPlaceholderClient:
    """
    Production-grade API Client encapsulating REST communication,
    secure headers, JSON parsing, and fault-tolerant error handling.
    """

    def __init__(self, base_url: str = API_BASE_URL, api_key: str = API_KEY, timeout: float = DEFAULT_TIMEOUT):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self._setup_headers()

    def _setup_headers(self) -> None:
        """Configures standard and authentication headers."""
        self.session.headers.update({
            "User-Agent": "AgenticAI-APIClient/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        })

    def get_sanitized_headers(self) -> Dict[str, str]:
        """Returns headers with masked authentication details for inspection."""
        sanitized = {}
        for k, v in self.session.headers.items():
            if k.lower() == "authorization":
                sanitized[k] = f"Bearer {sanitize_token(self.api_key)}"
            else:
                sanitized[k] = v
        return sanitized

    @staticmethod
    def map_status_code(status_code: int) -> str:
        """Returns informative diagnostic message for HTTP status codes."""
        status_map = {
            200: "200 OK - Request processed successfully.",
            201: "201 Created - New resource successfully created.",
            400: "400 Bad Request - Invalid request parameters or payload syntax.",
            401: "401 Unauthorized - Missing or invalid authentication credentials.",
            403: "403 Forbidden - Server refused access to the requested resource.",
            404: "404 Not Found - The requested resource does not exist.",
            429: "429 Too Many Requests - Rate limit reached. Back off and retry later.",
            500: "500 Internal Server Error - The remote server encountered an unexpected error."
        }
        return status_map.get(status_code, f"{status_code} - Unhandled HTTP status code.")

    def _execute_request(self, method: str, endpoint: str, timeout_override: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        """
        Executes HTTP request with complete error trapping across all failure categories.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        timeout = timeout_override if timeout_override is not None else self.timeout

        try:
            response = self.session.request(method=method, url=url, timeout=timeout, **kwargs)
            status = response.status_code

            # Check rate limiting headers if provided by upstream server
            rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
            if rate_limit_remaining is not None:
                print(f"[Rate-Limit Info] Requests remaining in quota: {rate_limit_remaining}")

            if 200 <= status < 300:
                try:
                    data = response.json()
                except ValueError:
                    data = response.text
                return {
                    "success": True,
                    "status_code": status,
                    "message": self.map_status_code(status),
                    "data": data
                }
            else:
                # API error response (4xx, 5xx)
                return {
                    "success": False,
                    "status_code": status,
                    "error_category": "API_ERROR",
                    "message": self.map_status_code(status),
                    "data": None
                }

        except Timeout:
            return {
                "success": False,
                "status_code": None,
                "error_category": "TIMEOUT",
                "message": f"Request to {url} timed out after {timeout} seconds.",
                "data": None
            }

        except ConnectionError as ce:
            return {
                "success": False,
                "status_code": None,
                "error_category": "NETWORK_FAILURE",
                "message": f"Network/DNS connection failure while contacting {url}.",
                "details": str(ce),
                "data": None
            }

        except RequestException as re:
            return {
                "success": False,
                "status_code": None,
                "error_category": "REQUEST_FAILURE",
                "message": f"HTTP transport exception: {str(re)}",
                "data": None
            }

    # ===============================================
    # High-level API Operations
    # ==============================================================

    def get_post(self, post_id: int) -> Dict[str, Any]:
        """Fetches a single post by ID (GET /posts/{id})."""
        return self._execute_request(method="GET", endpoint=f"posts/{post_id}")

    def list_posts(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Fetches collection of posts (GET /posts) and optionally slices the list."""
        result = self._execute_request(method="GET", endpoint="posts")
        if result["success"] and isinstance(result["data"], list) and limit is not None:
            result["total_count"] = len(result["data"])
            result["data"] = result["data"][:limit]
        elif result["success"] and isinstance(result["data"], list):
            result["total_count"] = len(result["data"])
        return result

    def create_post(self, title: str, body: str, user_id: int = 1) -> Dict[str, Any]:
        """Creates a new post resource (POST /posts)."""
        payload = {
            "title": title,
            "body": body,
            "userId": user_id
        }
        return self._execute_request(method="POST", endpoint="posts", json=payload)

    def simulate_timeout_call(self) -> Dict[str, Any]:
        """Simulates a timeout condition with an unachievable 0.0001s limit."""
        return self._execute_request(method="GET", endpoint="posts/1", timeout_override=0.0001)

    def simulate_network_failure(self) -> Dict[str, Any]:
        """Attempts to contact an invalid domain to verify network error recovery."""
        invalid_url = "https://non-existent-api-server-domain-12345.org/api/posts"
        try:
            requests.get(invalid_url, timeout=3.0)
            return {"success": True}
        except ConnectionError as ce:
            return {
                "success": False,
                "error_category": "NETWORK_FAILURE",
                "message": "Successfully caught network connection failure.",
                "details": str(ce)
            }


# =============================================================================
# Demonstration and Verification Execution
# =============================================================================

def run_integration_demonstration():
    print("=" * 70)
    print("       FINAL INTEGRATION PROJECT: COMPLETE REST API CLIENT")
    print("       Demonstrating Phases 01-05 Integration (Task 26)")
    print("=" * 70)

    # 1. Initialize client and display configuration
    client = JSONPlaceholderClient()
    print("\n[Step 1: Client Initialization & Secure Auth Headers]")
    print(f"Base API Endpoint: {client.base_url}")
    print(f"Default Timeout:   {client.timeout}s")
    print("Sanitized Active Headers:")
    for hk, hv in client.get_sanitized_headers().items():
        print(f"  - {hk}: {hv}")

    # 2. Retrieve a Single Post (GET /posts/1)
    print("\n[Step 2: Retrieve Single Post - GET /posts/1]")
    res_single = client.get_post(1)
    if res_single["success"]:
        post = res_single["data"]
        print(f"Status Code: {res_single['status_code']} ({res_single['message']})")
        print(f"  Post ID:   {post.get('id')}")
        print(f"  User ID:   {post.get('userId')}")
        print(f"  Title:     {post.get('title')}")
        print(f"  Body:      {post.get('body').replace(chr(10), ' ')}")
    else:
        print(f"Failed to fetch post 1: {res_single['message']}")

    # 3. Retrieve and Process Collection (GET /posts)
    print("\n[Step 3: Retrieve and Process Collection - GET /posts]")
    res_collection = client.list_posts(limit=5)
    if res_collection["success"]:
        print(f"Status Code: {res_collection['status_code']}")
        print(f"Total Posts Available on Server: {res_collection.get('total_count')}")
        print("First 5 Post Titles Extracted:")
        for idx, p in enumerate(res_collection["data"], start=1):
            print(f"  {idx}. [ID {p.get('id')}]: {p.get('title')}")
    else:
        print(f"Failed to fetch collection: {res_collection['message']}")

    # 4. Create a New Resource (POST /posts)
    print("\n[Step 4: Create a New Post - POST /posts]")
    new_post_payload = {
        "title": "Agentic AI Integration Architecture",
        "body": "Demonstrating end-to-end REST client capabilities with JSON data.",
        "user_id": 101
    }
    res_create = client.create_post(**new_post_payload)
    if res_create["success"]:
        created = res_create["data"]
        print(f"Status Code: {res_create['status_code']} ({res_create['message']})")
        print(f"Created Resource ID: {created.get('id')}")
        print(f"Created Title:       {created.get('title')}")
        print(f"Author User ID:      {created.get('userId')}")
    else:
        print(f"Post creation failed: {res_create['message']}")

    # 5. Error Handling Scenarios
    print("\n[Step 5: Fault-Tolerance & Error Handling Scenarios]")

    # Scenario 5A: 404 Resource Not Found
    print("\n--- Scenario 5A: Non-existent Resource (404) ---")
    res_404 = client.get_post(99999)
    print(f"Success Flag:    {res_404['success']}")
    print(f"Error Category:  {res_404.get('error_category')}")
    print(f"Status Code:     {res_404.get('status_code')}")
    print(f"Diagnostic Info: {res_404.get('message')}")

    # Scenario 5B: Timeout Handling
    print("\n--- Scenario 5B: Request Timeout Handling ---")
    res_timeout = client.simulate_timeout_call()
    print(f"Success Flag:    {res_timeout['success']}")
    print(f"Error Category:  {res_timeout.get('error_category')}")
    print(f"Diagnostic Info: {res_timeout.get('message')}")

    # Scenario 5C: Network / DNS Failure Handling
    print("\n--- Scenario 5C: Network / DNS Failure Handling ---")
    res_network = client.simulate_network_failure()
    print(f"Success Flag:    {res_network['success']}")
    print(f"Error Category:  {res_network.get('error_category')}")
    print(f"Diagnostic Info: {res_network.get('message')}")

    # Scenario 5D: Status Code Mapping Verification
    print("\n--- Scenario 5D: Status Code Catalog Verification ---")
    status_sample = [200, 201, 400, 401, 404, 429, 500]
    for sc in status_sample:
        print(f"  [{sc}] -> {JSONPlaceholderClient.map_status_code(sc)}")

    print("\n" + "=" * 70)
    print("       FINAL INTEGRATION DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run_integration_demonstration()
