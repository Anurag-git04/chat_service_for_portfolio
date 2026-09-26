import requests

url = "http://127.0.0.1:8000/api/chat"

def test_chat():
    # Test 1: Send a message
    response = requests.post(url, json={"message": "Hello, how are you?"})
    print(f"\n--- Test 1 ---")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Send another message
    response = requests.post(url, json={"message": "What can you help me with?"})
    print(f"\n--- Test 2 ---")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 3: Third message
    response = requests.post(url, json={"message": "Tell me a joke"})
    print(f"\n--- Test 3 ---")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 4: Should hit rate limit
    response = requests.post(url, json={"message": "This should be blocked"})
    print(f"\n--- Test 4 (Should be rate limited) ---")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_chat()
