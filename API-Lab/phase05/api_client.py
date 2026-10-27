"""
API-Lab - Phase 05: Errors, Timeouts & Rate Limits
Tasks 19 to 23
"""

import requests
from requests.exceptions import Timeout, ConnectionError, HTTPError, RequestException



# =============================================================================
# Task 20: Helper Function for Multiple HTTP Status Codes
# =============================================================================
def evaluate_http_status(status_code: int) -> str:
    """
    Evaluates an HTTP status code and returns a clear, actionable description.
    Distinguishes between 200/201, 400, 401, 404, 429, and 500.
    """
    status_catalog = {
        200: "200 OK: Request succeeded. The server returned the requested resource.",
        201: "201 Created: Request succeeded and a new resource was created.",
        400: "400 Bad Request: The server could not understand the request due to invalid syntax or payload.",
        401: "401 Unauthorized: Authentication is required or the provided credentials are invalid.",
        404: "404 Not Found: The requested resource does not exist on the server.",
        429: "429 Too Many Requests: Rate limit exceeded. Please back off and retry later.",
        500: "500 Internal Server Error: The server encountered an unexpected error while processing the request."
    }
    
    if status_code in status_catalog:
        return status_catalog[status_code]
    elif 200 <= status_code < 300:
        return f"{status_code} Success: Successful operation."
    elif 400 <= status_code < 500:
        return f"{status_code} Client Error: Issue with client request."
    elif 500 <= status_code < 600:
        return f"{status_code} Server Error: Server failed to fulfill valid request."
    return f"{status_code}: Unrecognized HTTP status code."




# =============================================================================
# Task 22: Comprehensive Request Function
# =============================================================================
def make_robust_request(url: str, timeout_seconds: float = 10.0, headers: dict = None):
    """
    Executes a network request with comprehensive error handling.
    Cleanly categorizes:
      1. Successful request (HTTP 200-299)
      2. API error (HTTP 4xx / 5xx)
      3. Timeout
      4. Network / Request failure
    """
    print(f"\n[Dispatching Request] -> URL: {url} | Timeout: {timeout_seconds}s")
    try:
        response = requests.get(url, headers=headers, timeout=timeout_seconds)
        
        # Check HTTP status code
        if 200 <= response.status_code < 300:
            print(f"[Outcome: SUCCESS] Status Code: {response.status_code}")
            return {"status": "success", "status_code": response.status_code, "data": response.json()}
        else:
            # Categorized as an API Error
            print(f"[Outcome: API ERROR] Status Code: {response.status_code}")
            explanation = evaluate_http_status(response.status_code)
            print(f"  Details: {explanation}")
            return {"status": "api_error", "status_code": response.status_code, "error": explanation}
            
    except Timeout:
        print(f"[Outcome: TIMEOUT] Request timed out after {timeout_seconds} seconds.")
        print("  Prevention: Program prevented from hanging indefinitely.")
        return {"status": "timeout_error", "error": "Request timed out"}
        
    except ConnectionError as ce:
        print(f"[Outcome: NETWORK FAILURE] Connection failed or host unreachable.")
        print(f"  Details: {ce.__class__.__name__}")
        return {"status": "network_error", "error": str(ce)}
        
    except RequestException as re:
        print(f"[Outcome: REQUEST FAILURE] Generic requests exception encountered.")
        print(f"  Details: {str(re)}")
        return {"status": "request_error", "error": str(re)}


def main():
    print("=" * 60)
    print("   PHASE 05: ERRORS, TIMEOUTS & RATE LIMITS")
    print("=" * 60)

    # =========================================================================
    # Task 19: Handle a 404 Error
    # =========================================================================
    print("\n--- Task 19: Handle a 404 Error ---")
    invalid_url = "https://jsonplaceholder.typicode.com/posts/99999"
    
    try:
        resp = requests.get(invalid_url, timeout=10)
        if resp.status_code == 404:
            print("Request failed.")
            print(f"Status Code: {resp.status_code}")
            print("Resource not found.")
        else:
            print(f"Received unexpected status: {resp.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")

    # =========================================================================
    # Task 20: Handle Multiple HTTP Errors (Demonstration / Simulation)
    # =========================================================================
    print("\n--- Task 20: Handle Multiple HTTP Errors ---")
    print("Testing evaluate_http_status() helper across required status codes:")
    test_codes = [200, 201, 400, 401, 404, 429, 500]
    for code in test_codes:
        message = evaluate_http_status(code)
        print(f"  [{code}] -> {message}")

    # =============================================================================
    # Task 21: Why Timeout is Necessary (Theory & Explanation)
    # =============================================================================
    # Theoretical Explanation for Task 21:
    # A request timeout is essential because network requests operate over unreliable physical
    # infrastructure. If a remote server is frozen, drops packets, or experiences network
    # congestion, a client without a timeout will block (hang) indefinitely waiting for a
    # response that may never arrive. Setting `timeout=10` ensures that the client retains
    # control, frees system sockets/threads, and can gracefully recover or notify the user.

    # =========================================================================
    # Task 21: Add Request Timeout
    # =========================================================================
    print("\n--- Task 21: Add Request Timeout ---")
    print("Explanation: A timeout prevents client programs from waiting indefinitely if")
    print("the remote server or connection drops packets or becomes unresponsive.")
    
    # Demonstration 1: Successful call with timeout=10
    print("\n1. Normal request with timeout=10:")
    try:
        valid_res = requests.get("https://jsonplaceholder.typicode.com/posts/1", timeout=10)
        print(f"  Success: Received status code {valid_res.status_code} well within 10s limit.")
    except Timeout:
        print("  Error: Request timed out.")

    # Demonstration 2: Demonstration of timeout exception handling (using an impossible timeout: 0.0001s)
    print("\n2. Timeout simulation (triggering try/except requests.exceptions.Timeout):")
    try:
        requests.get("https://jsonplaceholder.typicode.com/posts/1", timeout=0.0001)
    except Timeout:
        print("  [Caught Timeout Exception] Gracefully detected and prevented infinite wait.")
    except RequestException as e:
        print(f"  Other request error: {e}")

    # =========================================================================
    # Task 22: Comprehensive Error Handling Demonstration
    # =========================================================================
    print("\n--- Task 22: Comprehensive Error Handling Architecture ---")
    print("Demonstrating clean distinction across all 4 categories:")

    # Category 1: Successful Request
    make_robust_request("https://jsonplaceholder.typicode.com/posts/1", timeout_seconds=10.0)

    # Category 2: API Error (404)
    make_robust_request("https://jsonplaceholder.typicode.com/posts/99999", timeout_seconds=10.0)

    # Category 3: Timeout Trigger
    make_robust_request("https://jsonplaceholder.typicode.com/posts/1", timeout_seconds=0.0001)

    # Category 4: Network / DNS Failure
    make_robust_request("https://invalid-non-existent-domain-xyz123456.org/api", timeout_seconds=5.0)

    # =========================================================================
    # Task 23: Rate Limiting Summary
    # =========================================================================
    # =============================================================================
    # Task 23: Investigate Rate Limiting (Theory Questions & Answers)
    # =============================================================================
    """
    Task 23: Rate Limiting Investigation

    Question 1: What is a rate limit?
    Answer:
    A rate limit is a policy set by an API server that controls how many requests
    a specific client, IP address, or API key can make within a designated timeframe
    (e.g., 60 requests per minute or 10,000 requests per day).

    Question 2: Why do APIs impose rate limits?
    Answer:
    APIs enforce rate limits to protect server infrastructure from overload and denial-of-service
    (DoS) conditions, maintain fair resource availability for all users, prevent unauthorized
    data scraping, and manage backend infrastructure and third-party operational costs.

    Question 3: What does HTTP 429 mean?
    Answer:
    HTTP 429 stands for 'Too Many Requests'. It signifies that the client has exceeded its
    allotted request quota or velocity threshold. Servers often return a 'Retry-After' response
    header indicating how many seconds the client must wait before making another request.

    Question 4: Why can an automated program generate too many requests?
    Answer:
    Unlike human users who interact at natural reading speeds, automated scripts and loops execute
    in milliseconds. An unthrottled loop or multithreaded worker can dispatch hundreds or thousands
    of HTTP requests in seconds without intentional pacing.

    Question 5: Why is this especially important for agentic systems?
    Answer:
    Autonomous AI agents operate in dynamic reasoning-action loops (such as ReAct). If an agent
    gets trapped in a decision cycle or repeatedly tries to fix an error by re-querying tools,
    it can flood an API. Without proper rate-limit detection, backoff strategies, and retry
    guardrails, an agent can exhaust API quotas, trigger account suspensions, or incur massive costs.
    """

    print("\n" + "=" * 60)
    print("   PHASE 05 COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()
