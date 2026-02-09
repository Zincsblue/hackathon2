#!/usr/bin/env python3
"""
Authentication Backend Test Script
Tests all authentication endpoints and flows.
"""
import requests
import json
import sys
import time
from typing import Optional

BASE_URL = "http://localhost:8001/api/v1"
HEADERS = {"Content-Type": "application/json"}

# Test data with unique email using timestamp
timestamp = int(time.time())
TEST_USER = {
    "email": f"test{timestamp}@example.com",
    "password": "testpassword123",
    "name": "Test User"
}

# Store tokens
access_token: Optional[str] = None
refresh_token_cookie: Optional[str] = None


def print_test(name: str):
    """Print test name."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print('='*60)


def print_result(success: bool, message: str):
    """Print test result."""
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status}: {message}")


def test_health_check():
    """Test health check endpoint."""
    print_test("Health Check")
    try:
        response = requests.get("http://localhost:8001/health")
        if response.status_code == 200:
            print_result(True, f"Server is healthy: {response.json()}")
            return True
        else:
            print_result(False, f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Cannot connect to server: {e}")
        print("  Make sure the server is running on port 8001")
        return False


def test_registration():
    """Test user registration."""
    print_test("User Registration")
    global access_token, refresh_token_cookie

    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=TEST_USER,
            headers=HEADERS
        )

        if response.status_code == 201:
            data = response.json()
            access_token = data.get("access_token")

            # Extract refresh token from cookies
            if "refresh_token" in response.cookies:
                refresh_token_cookie = response.cookies["refresh_token"]

            print_result(True, "User registered successfully")
            print(f"  Access Token: {access_token[:50]}...")
            print(f"  Token Type: {data.get('token_type')}")
            print(f"  Expires In: {data.get('expires_in')} seconds")
            print(f"  Refresh Token Cookie: {'Set' if refresh_token_cookie else 'Not Set'}")
            return True
        else:
            print_result(False, f"Registration failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Registration error: {e}")
        return False


def test_duplicate_registration():
    """Test duplicate email registration."""
    print_test("Duplicate Email Registration (Should Fail)")

    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=TEST_USER,
            headers=HEADERS
        )

        if response.status_code == 409:
            print_result(True, "Duplicate email correctly rejected with 409 Conflict")
            return True
        else:
            print_result(False, f"Expected 409, got {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_login():
    """Test user login."""
    print_test("User Login")
    global access_token, refresh_token_cookie

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            },
            headers=HEADERS
        )

        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")

            if "refresh_token" in response.cookies:
                refresh_token_cookie = response.cookies["refresh_token"]

            print_result(True, "Login successful")
            print(f"  Access Token: {access_token[:50]}...")
            print(f"  Refresh Token Cookie: {'Set' if refresh_token_cookie else 'Not Set'}")
            return True
        else:
            print_result(False, f"Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Login error: {e}")
        return False


def test_invalid_login():
    """Test login with invalid credentials."""
    print_test("Invalid Login (Should Fail)")

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": "wrongpassword"
            },
            headers=HEADERS
        )

        if response.status_code == 401:
            print_result(True, "Invalid credentials correctly rejected with 401")
            return True
        else:
            print_result(False, f"Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_get_current_user():
    """Test GET /auth/me endpoint."""
    print_test("Get Current User Profile")

    if not access_token:
        print_result(False, "No access token available")
        return False

    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={
                **HEADERS,
                "Authorization": f"Bearer {access_token}"
            }
        )

        if response.status_code == 200:
            data = response.json()
            print_result(True, "User profile retrieved")
            print(f"  User ID: {data.get('id')}")
            print(f"  Email: {data.get('email')}")
            print(f"  Name: {data.get('name')}")
            print(f"  Active: {data.get('is_active')}")
            print(f"  Verified: {data.get('is_verified')}")
            return True
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_protected_endpoint_without_token():
    """Test accessing protected endpoint without token."""
    print_test("Access Protected Endpoint Without Token (Should Fail)")

    try:
        response = requests.get(
            f"{BASE_URL}/tasks",
            headers=HEADERS
        )

        if response.status_code == 401 or response.status_code == 403:
            print_result(True, f"Correctly rejected with {response.status_code}")
            return True
        else:
            print_result(False, f"Expected 401/403, got {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_create_task():
    """Test creating a task with authentication."""
    print_test("Create Task (Authenticated)")

    if not access_token:
        print_result(False, "No access token available")
        return False

    try:
        response = requests.post(
            f"{BASE_URL}/tasks",
            json={
                "title": "Test Task",
                "description": "This is a test task",
                "completed": False
            },
            headers={
                **HEADERS,
                "Authorization": f"Bearer {access_token}"
            }
        )

        if response.status_code == 201:
            data = response.json()
            print_result(True, "Task created successfully")
            print(f"  Task ID: {data.get('id')}")
            print(f"  Title: {data.get('title')}")
            print(f"  User ID: {data.get('user_id')}")
            return True
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_list_tasks():
    """Test listing tasks with authentication."""
    print_test("List Tasks (Authenticated)")

    if not access_token:
        print_result(False, "No access token available")
        return False

    try:
        response = requests.get(
            f"{BASE_URL}/tasks",
            headers={
                **HEADERS,
                "Authorization": f"Bearer {access_token}"
            }
        )

        if response.status_code == 200:
            data = response.json()
            print_result(True, "Tasks retrieved successfully")
            print(f"  Total Tasks: {data.get('total')}")
            print(f"  Tasks in Response: {len(data.get('tasks', []))}")
            return True
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_token_refresh():
    """Test token refresh."""
    print_test("Token Refresh")
    global access_token

    if not refresh_token_cookie:
        print_result(False, "No refresh token cookie available")
        return False

    try:
        response = requests.post(
            f"{BASE_URL}/auth/refresh",
            headers=HEADERS,
            cookies={"refresh_token": refresh_token_cookie}
        )

        if response.status_code == 200:
            data = response.json()
            old_token = access_token
            access_token = data.get("access_token")

            print_result(True, "Token refreshed successfully")
            print(f"  New Access Token: {access_token[:50]}...")
            print(f"  Token Changed: {old_token != access_token}")
            return True
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_logout():
    """Test logout."""
    print_test("Logout")

    if not refresh_token_cookie:
        print_result(False, "No refresh token cookie available")
        return False

    try:
        response = requests.post(
            f"{BASE_URL}/auth/logout",
            headers=HEADERS,
            cookies={"refresh_token": refresh_token_cookie}
        )

        if response.status_code == 204:
            print_result(True, "Logout successful")
            return True
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "="*60)
    print("AUTHENTICATION BACKEND TEST SUITE")
    print("="*60)

    tests = [
        ("Health Check", test_health_check),
        ("User Registration", test_registration),
        ("Duplicate Registration", test_duplicate_registration),
        ("User Login", test_login),
        ("Invalid Login", test_invalid_login),
        ("Get Current User", test_get_current_user),
        ("Protected Endpoint Without Token", test_protected_endpoint_without_token),
        ("Create Task", test_create_task),
        ("List Tasks", test_list_tasks),
        ("Token Refresh", test_token_refresh),
        ("Logout", test_logout),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_result(False, f"Test crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n*** All tests passed! ***")
        return 0
    else:
        print(f"\n*** {total - passed} test(s) failed ***")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
