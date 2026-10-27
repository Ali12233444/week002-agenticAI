# Final Integration Project: Production-Grade REST API Client

## 1. Project Overview
This project serves as the culmination of **Phases 01 through 05** of the API Lab. It implements a robust, fault-tolerant Python client connecting to the **JSONPlaceholder REST API**, integrating:
- RESTful HTTP communications (`GET`, `POST`)
- Dynamic JSON serialization and field extraction
- Secure environment-variable-driven authentication (`python-dotenv`, `Authorization: Bearer <TOKEN>`)
- Multi-tier error handling (HTTP status detection, timeouts, DNS/network disconnects, and rate limiting)
- Architectural transformation into AI agent tools

---

## 2. API Endpoint & Method Documentation

### A. Retrieve Single Post
- **Endpoint:** `GET https://jsonplaceholder.typicode.com/posts/{id}`
- **Description:** Fetches a specific blog post by its unique numeric ID.
- **Path Parameters:**
  - `id` (integer, required): Unique identifier of the post (e.g., `1`, `42`).
- **Request Headers:**
  ```http
  Authorization: Bearer <API_KEY>
  Accept: application/json
  User-Agent: AgenticAI-APIClient/1.0
  ```
- **Response Structure (`200 OK`):**
  ```json
  {
    "userId": 1,
    "id": 1,
    "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
    "body": "quia et suscipit suscipit recusandae consequuntur expedita..."
  }
  ```

---

### B. List Posts (Collection)
- **Endpoint:** `GET https://jsonplaceholder.typicode.com/posts`
- **Description:** Retrieves all available blog posts in a collection array.
- **Query Parameters:** None required.
- **Response Structure (`200 OK`):**
  ```json
  [
    {
      "userId": 1,
      "id": 1,
      "title": "...",
      "body": "..."
    },
    ...
  ]
  ```

---

### C. Create New Post
- **Endpoint:** `POST https://jsonplaceholder.typicode.com/posts`
- **Description:** Submits a new post object to the server.
- **Request Body (JSON, `Content-Type: application/json`):**
  ```json
  {
    "title": "Agentic AI Integration Architecture",
    "body": "Demonstrating end-to-end REST client capabilities with JSON data.",
    "userId": 101
  }
  ```
- **Response Structure (`201 Created`):**
  ```json
  {
    "id": 101,
    "title": "Agentic AI Integration Architecture",
    "body": "Demonstrating end-to-end REST client capabilities with JSON data.",
    "userId": 101
  }
  ```

---

## 3. Possible Errors & Handling Strategy

The client intercepts failures across four primary categories to prevent application crashes and indefinite hangs:

| Status / Error | Category | Description | Client Handling Strategy |
| :--- | :--- | :--- | :--- |
| **`400 Bad Request`** | API Error | Malformed payload or invalid request syntax. | Returns diagnostic feedback without raising unhandled exceptions. |
| **`401 Unauthorized`** | Auth Error | Missing or invalid Bearer token. | Prompts operator to inspect `.env` configuration. |
| **`404 Not Found`** | API Error | The requested resource ID does not exist on the server. | Gracefully reports missing resource (`Resource not found`). |
| **`429 Too Many Requests`** | Rate Limit | Request quota exhausted within active timeframe. | Extracts `Retry-After` if present; applies exponential backoff. |
| **`500 Internal Server Error`** | Server Error | Remote host suffered an internal failure. | Marks operation failed; advises temporary hold or single retry. |
| **`Timeout`** | Network / SLA | Request exceeded `timeout=10.0` seconds. | Aborts socket wait; frees thread/memory to keep system responsive. |
| **`ConnectionError`** | Network Failure| DNS resolution failure, network drop, or server unreachable. | Gracefully caught via `requests.exceptions.ConnectionError`. |

---

## 4. How this API Operation Becomes an AI Agent Tool

In an Autonomous Agent architecture (such as an LLM ReAct agent, LangChain Agent, or Gemini Function Calling agent):
1. **Abstraction of Network Mechanics:** The agent should not write HTTP queries or worry about URL escaping at runtime. The API client wraps the call into a high-level Python function (e.g., `get_post(post_id: int)`).
2. **Declarative Tool Schema:** The function's name, docstring, parameters (`post_id: int`), and required fields are exported as a JSON schema. The LLM's planner reads this schema to determine if fetching a post will satisfy the user's intent.
3. **Structured Failure Reporting:** Instead of raising a raw Python traceback that halts execution, the tool returns a clean dictionary (e.g. `{"error": "404 Not Found", "message": "Post 99999 does not exist"}`). The agent's reasoning loop perceives this output as an observation and can replan (e.g., "The post doesn't exist, I should prompt the user for a valid ID").
4. **Safety Guardrails:** Hard timeouts (`timeout=10`) and rate limit handling prevent the agent from triggering infinite loops, burning API quotas, or locking the thread.

---

## 5. Setup & Execution Instructions

### Prerequisites
- Python 3.10+
- `pip`

### Installation
1. Navigate to the project root:
   ```bash
   cd API-Lab/final_project
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   # Copy example template
   cp .env.example .env
   ```
4. Run the demonstration suite:
   ```bash
   python src/main.py
   ```
