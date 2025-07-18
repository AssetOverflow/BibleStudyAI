#!/usr/bin/env python3
"""
Comprehensive API Testing Script for BibleStudyAI
Tests all available endpoints and validates responses.
"""

import requests
import json
import time
    # Create note
    note_data = {
        "title": "Test Note",
        "content": "This is a test note about John 3:16"
    }yping import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}


def make_request(
    method: str, endpoint: str, data: Optional[Dict] = None
) -> Dict[str, Any]:
    """Make HTTP request and return structured response"""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=HEADERS)
        elif method.upper() == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=HEADERS, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=HEADERS)
        else:
            raise ValueError(f"Unsupported method: {method}")

        return {
            "status_code": response.status_code,
            "success": response.status_code < 400,
            "data": response.json() if response.content else None,
            "headers": dict(response.headers),
            "url": url,
        }
    except requests.exceptions.RequestException as e:
        return {"status_code": None, "success": False, "error": str(e), "url": url}
    except json.JSONDecodeError as e:
        return {
            "status_code": response.status_code,
            "success": False,
            "error": f"JSON decode error: {e}",
            "content": response.text[:200],
            "url": url,
        }


def print_test_result(
    test_name: str, result: Dict[str, Any], expected_status: int = 200
):
    """Print formatted test result"""
    success = (
        result.get("success", False) and result.get("status_code") == expected_status
    )
    status = "✅ PASS" if success else "❌ FAIL"

    print(f"\n{status} {test_name}")
    print(f"   URL: {result['url']}")
    print(f"   Status: {result.get('status_code', 'N/A')}")

    if not success:
        if "error" in result:
            print(f"   Error: {result['error']}")
        if "content" in result:
            print(f"   Content: {result['content']}")

    if success and result.get("data"):
        if isinstance(result["data"], list):
            print(f"   Response: List with {len(result['data'])} items")
            if result["data"]:
                print(f"   Sample: {str(result['data'][0])[:100]}...")
        elif isinstance(result["data"], dict):
            print(f"   Response: {str(result['data'])[:100]}...")
        else:
            print(f"   Response: {result['data']}")


def test_basic_endpoints():
    """Test basic API endpoints"""
    print("=" * 60)
    print("TESTING BASIC ENDPOINTS")
    print("=" * 60)

    # Root endpoint
    result = make_request("GET", "/")
    print_test_result("Root endpoint", result)

    # Health check
    result = make_request("GET", "/health")
    print_test_result("Health check", result)

    # API docs
    result = make_request("GET", "/docs")
    print_test_result("API Documentation", result)


def test_bible_endpoints():
    """Test Bible service endpoints"""
    print("\n" + "=" * 60)
    print("TESTING BIBLE ENDPOINTS")
    print("=" * 60)

    # Get translations
    result = make_request("GET", "/api/bible/translations")
    print_test_result("Get Bible translations", result)

    # Get books for a translation
    result = make_request("GET", "/api/bible/KJV/books")
    print_test_result("Get books for KJV", result)

    # Get chapters for a book
    result = make_request("GET", "/api/bible/KJV/John/chapters")
    print_test_result("Get chapters for John (KJV)", result)

    # Get verses for a chapter
    result = make_request("GET", "/api/bible/KJV/John/3/verses")
    print_test_result("Get John 3 verses (KJV)", result)

    # Search verses
    result = make_request("GET", "/api/bible/KJV/search?query=love")
    print_test_result("Search for 'love' in KJV", result)

    # Test with different translation
    result = make_request("GET", "/api/bible/ESV/Psalms/23/verses")
    print_test_result("Get Psalm 23 verses (ESV)", result)


def test_auth_endpoints():
    """Test authentication endpoints"""
    print("
" + "=" * 60)
    print("TESTING AUTH ENDPOINTS") 
    print("=" * 60)
    
    # Use timestamp to ensure unique email
    import time
    timestamp = int(time.time())
    unique_email = f"test{timestamp}@example.com"
    
    # Register user
    user_data = {
        "email": unique_email,
        "name": f"Test User {timestamp}", 
        "password": "testpassword123"
    }
    result = make_request("POST", "/auth/register", user_data)
    print_test_result("Register user", result, 201)
    
    # Login
    login_data = {
        "email": unique_email,
        "name": f"Test User {timestamp}",  # Required by UserCreate model
        "password": "testpassword123"
    }
    result = make_request("POST", "/auth/login", login_data)
    print_test_result("Login user", result)
    
    # Extract token for authenticated requests
    token = None
    if result.get("success") and result.get("data"):
        token = result["data"].get("access_token")
        if token:
            print(f"   Token obtained: {token[:20]}...")
    
    return token
def test_notes_endpoints(token: Optional[str] = None):
    """Test notes endpoints"""
    print("\n" + "=" * 60)
    print("TESTING NOTES ENDPOINTS")
    print("=" * 60)

    auth_headers = HEADERS.copy()
    if token:
        auth_headers["Authorization"] = f"Bearer {token}"

    # Create note
    note_data = {
        "title": "Test Note",
        "content": "This is a test note about John 3:16",
        "reference": "John 3:16",
    }

    try:
        url = f"{BASE_URL}/api/notes/"
        response = requests.post(url, headers=auth_headers, json=note_data)
        result = {
            "status_code": response.status_code,
            "success": response.status_code < 400,
            "data": response.json() if response.content else None,
            "url": url,
        }
        print_test_result("Create note", result, 201)

        # Get notes
        response = requests.get(f"{BASE_URL}/api/notes/", headers=auth_headers)
        result = {
            "status_code": response.status_code,
            "success": response.status_code < 400,
            "data": response.json() if response.content else None,
            "url": f"{BASE_URL}/api/notes/",
        }
        print_test_result("Get notes", result)

    except Exception as e:
        print(f"❌ FAIL Notes endpoints: {e}")


def test_chat_endpoints():
    """Test chat/RAG endpoints"""
    print("\n" + "=" * 60)
    print("TESTING CHAT/RAG ENDPOINTS")
    print("=" * 60)

    # Test RAG endpoint (available)
    query_data = {"question": "What does the Bible say about love?"}
    result = make_request("POST", "/api/rag/answer", query_data)
    print_test_result("RAG Query about love", result)

    # Note: Other chat endpoints are commented out in main.py, so they'll return 404
    print("   Note: Other chat endpoints (/api/chat/*) are disabled in main.py")


def test_search_endpoints():
    """Test search-related endpoints"""
    print("\n" + "=" * 60)
    print("TESTING SEARCH ENDPOINTS")
    print("=" * 60)

    print("   Note: Search endpoints (/api/chat/*) are disabled in main.py")
    print("   Only /api/rag/answer is currently available for AI queries")


def main():
    """Run all tests"""
    print("🚀 Starting BibleStudyAI API Testing Suite")
    print(f"Base URL: {BASE_URL}")
    
    # Test basic functionality
    test_basic_endpoints()
    test_bible_endpoints()
    
    # Test authentication and get token
    token = test_auth_endpoints()
    
    # Test notes with auth token
    test_notes_endpoints(token)
    
    # Test chat/RAG functionality
    test_chat_endpoints()
    
    # Test search functionality
    test_search_endpoints()
    
    print("
" + "=" * 60)
    print("✅ API Testing Complete!")
    print("=" * 60)
if __name__ == "__main__":
    main()
