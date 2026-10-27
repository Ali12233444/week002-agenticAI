import requests

def main():
    print("=" * 60)
    print("   PHASE 03: JSON & PYTHON API INTEGRATION")
    print("=" * 60)

    # ==============================================================
    # Task 11: Create a JSON Student Record
    # =========================================================================
    # Theoretical Note:
    # A JSON object is a text-based format structured with key-value pairs
    # using double quotes for keys and strings. In Python, this maps directly
    # to a native dictionary (`dict`), where keys and values can be accessed
    # using key indexing or the .get() method.
    print("\n--- Task 11: Create a JSON Student Record ---")
    
    # Raw JSON string representation
    student_json_str = '{"name": "Ali", "marks": 85, "program": "BSCS"}'
    
    # Equivalent Python dictionary
    student = {
        "name": "Ali",
        "marks": 85,
        "program": "BSCS"
    }
    
    print(f"Original JSON String: {student_json_str}")
    print(f"Python Dictionary:    {student}")
    print(f"Student Name:         {student['name']}")
    print(f"Student Marks:        {student['marks']}")
    print(f"Student Program:      {student['program']}")

    # ====================================================
    # Task 12: Work With a JSON Array
    # ==========================================================
    # Theoretical Note:
    # A JSON array is an ordered collection of values enclosed in square brackets.
    # In Python, it is represented as a list of dictionaries (`list[dict]`).
    print("\n--- Task 12: Work With a JSON Array ---")
    
    students = [
        {"id": 1, "name": "Ali"},
        {"id": 2, "name": "Sara"},
        {"id": 3, "name": "Ahmed"}
    ]
    
    print(f"Total students in array: {len(students)}")
    for s in students:
        print(f"ID: {s['id']} | Name: {s['name']}")

    # =========================================================================
    # Task 13: Create Your First Python API Client
    # =========================================================================
    print("\n--- Task 13: Create Your First Python API Client ---")
    single_post_url = "https://jsonplaceholder.typicode.com/posts/1"
    
    response = requests.get(single_post_url)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        post_data = response.json()
        print(f"Post ID: {post_data.get('id')}")
        print(f"Title:   {post_data.get('title')}")
        # Display body with clean line wrapping
        body_preview = post_data.get('body', '').replace('\n', ' ')
        print(f"Body:    {body_preview}")
    else:
        print(f"Error fetching post: Received status code {response.status_code}")

    # =========================================================================
    # Task 14: Retrieve Multiple API Records
    # =========================================================================
    print("\n--- Task 14: Retrieve Multiple API Records (Posts 1, 2, 3) ---")
    post_ids = [1, 2, 3]
    base_url = "https://jsonplaceholder.typicode.com/posts"
    
    for pid in post_ids:
        post_url = f"{base_url}/{pid}"
        res = requests.get(post_url)
        if res.status_code == 200:
            p_data = res.json()
            print(f"Post {pid}: {p_data.get('title')}")
        else:
            print(f"Post {pid}: Failed to retrieve (Status {res.status_code})")

    # =========================================================================
    # Task 15: Retrieve and Process a Collection
    # =========================================================================
    print("\n--- Task 15: Retrieve and Process a Collection ---")
    collection_url = "https://jsonplaceholder.typicode.com/posts"
    
    res_collection = requests.get(collection_url)
    print(f"Request Status: {res_collection.status_code}")
    
    if res_collection.status_code == 200:
        posts_list = res_collection.json()
        total_posts = len(posts_list)
        print(f"Total number of posts returned: {total_posts}")
        print("First 5 post titles:")
        for idx, post in enumerate(posts_list[:5], start=1):
            print(f"  {idx}. [ID {post.get('id')}]: {post.get('title')}")
    else:
        print(f"Failed to fetch posts collection. Status code: {res_collection.status_code}")

    print("\n" + "=" * 60)
    print("   PHASE 03 COMPLETED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    main()
