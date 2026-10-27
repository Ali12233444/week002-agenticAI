# Phase 06: From API Integration to Agent Tools

## Overview
In modern Agentic AI workflows, an AI agent does not browse the web like a human or write ad-hoc API client scripts at runtime. Instead, external capabilities are abstracted into **Agent Tools**—structured, deterministic function interfaces that an LLM can understand, select, and invoke autonomously through tool-use protocols (such as OpenAI Function Calling or Gemini Tool Use).

This document specifies the transition from a REST API endpoint to an Agent Tool interface.

---

## Task 24: API Tool Specification

Below is the concrete API-level tool specification for retrieving blog post records from the JSONPlaceholder REST service.

| Field | Value / Details |
| :--- | :--- |
| **Tool Name** | `fetch_post_by_id` |
| **Description** | Retrieves a specific blog post record by its unique numeric identifier from the backend API. |
| **HTTP Method** | `GET` |
| **Endpoint** | `https://jsonplaceholder.typicode.com/posts/{id}` |
| **Required Inputs** | `id` (integer) — The unique identifier of the post to retrieve (e.g., `1`, `42`). |
| **Optional Inputs** | `timeout` (integer, default: `10`) — Maximum socket wait time in seconds.<br>`include_user` (boolean, default: `false`) — Reserved flag for nested user hydration. |
| **Expected Output** | JSON Object containing the post details:<br>• `id` (integer): Post ID<br>• `userId` (integer): ID of author<br>• `title` (string): Title of the post<br>• `body` (string): Full body text content |
| **Possible Errors** | • `400 Bad Request` — Invalid ID format (e.g., non-numeric string).<br>• `404 Not Found` — The specified post ID does not exist.<br>• `429 Too Many Requests` — Rate limit exceeded.<br>• `500 Internal Server Error` — Target server crashed or unavailable.<br>• `Timeout` — Request exceeded 10 seconds.<br>• `NetworkError` — DNS resolution failure or network drop. |
| **Authentication Required**| `None` (Public test API; for protected production equivalents, `Authorization: Bearer <TOKEN>` in request header). |

---

## Task 25: Design an Agent-Oriented Tool Interface

An Agent Tool Interface abstracts away HTTP transport details (URL formatting, headers, serialization) and exposes a pure, type-safe semantic contract to the LLM agent.

### 1. High-Level Semantic Definition

- **Tool:** `get_post`
- **Purpose:** Retrieve the title, content body, and author metadata of a specific post using its post ID.
- **Input:**
  - `post_id` (integer, required): The unique integer ID of the target post (must be greater than or equal to 1).
- **Output:**
  - `id` (integer): Unique ID of the post.
  - `title` (string): Title of the post.
  - `body` (string): Content text of the post.
  - `userId` (integer): ID of the author who created the post.
- **Possible Errors:**
  - `404`: Post not found (agent should inform user or check alternate ID).
  - `429`: Rate limit exceeded (agent should pause execution or back off).
  - `500`: Remote server internal error (agent should retry once or fail gracefully).
  - `Timeout`: Remote API took longer than 10 seconds (agent should notify user of network lag).

---

### 2. Standard LLM Function Calling Schema (Gemini / OpenAI Compatible)

When exposed to an autonomous reasoning model, the tool is represented via JSON Schema:

```json
{
  "name": "get_post",
  "description": "Retrieves the full content and metadata of a blog post by its unique ID. Use this tool whenever the user asks to read, analyze, or summarize a specific post.",
  "parameters": {
    "type": "object",
    "properties": {
      "post_id": {
        "type": "integer",
        "description": "The unique numerical identifier of the post to retrieve (e.g. 1, 2, 3)."
      }
    },
    "required": ["post_id"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "id": { "type": "integer" },
      "userId": { "type": "integer" },
      "title": { "type": "string" },
      "body": { "type": "string" }
    }
  }
}
```

---

### 3. Python Agent Tool Implementation Signature

Below is how the agent tool is implemented as an invokable Python callable for an Agent framework (such as LangChain, CrewAI, or Antigravity Tool Protocol):

```python
def get_post(post_id: int) -> dict:
    """
    Agent Tool: get_post
    
    Purpose:
        Retrieves a post from the backend service using its integer ID.
        
    Args:
        post_id (int): Positive integer identifying the post.
        
    Returns:
        dict: Containing 'id', 'title', 'body', 'userId' on success,
              or an error object with status code and error description.
    """
    # 1. Validation
    if not isinstance(post_id, int) or post_id < 1:
        return {"error": "Invalid input: post_id must be a positive integer."}

    # 2. Execution with error boundary
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"error": "404 Not Found", "message": f"Post {post_id} does not exist."}
        elif response.status_code == 429:
            return {"error": "429 Rate Limited", "message": "Too many requests. Please wait."}
        elif response.status_code >= 500:
            return {"error": f"{response.status_code} Server Error", "message": "Upstream service failure."}
        else:
            return {"error": f"HTTP {response.status_code}", "message": response.text}
    except requests.exceptions.Timeout:
        return {"error": "Timeout", "message": "The request took longer than 10 seconds."}
    except requests.exceptions.RequestException as e:
        return {"error": "NetworkFailure", "message": str(e)}
```

---

### 4. Why This Architecture Matters for Agentic AI
1. **Model Understanding:** Clear descriptions and parameter schemas enable the LLM to know *when* and *how* to call the tool accurately.
2. **Deterministic Output:** Structured JSON error contracts allow the agent's planner to reason over failures (e.g. trying an alternative query when a `404` occurs) instead of crashing with an unhandled Python stack trace.
3. **Safety & Guardrails:** Timeouts and rate-limiting safeguards prevent the agent from getting trapped in infinite retry loops that waste tokens and overwhelm APIs.
