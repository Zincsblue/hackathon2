# Backend Authentication Testing Guide

## Quick Start

### Step 1: Start Redis (Required for Rate Limiting)

**Option A - Using Docker (Recommended):**
```bash
docker run -d -p 6379:6379 --name redis-auth redis:alpine
```

**Option B - Using WSL:**
```bash
wsl sudo service redis-server start
```

**Option C - Windows Native:**
- Download from: https://github.com/microsoftarchive/redis/releases
- Run: `redis-server`

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

---

### Step 2: Start the FastAPI Server

**Option A - Using the batch file:**
```bash
start_server.bat
```

**Option B - Manual start:**
```bash
# Activate virtual environment
venv\Scripts\activate

# Start server
uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify server is running:**
- Open browser: http://localhost:8000/health
- Should see: `{"status":"healthy","service":"Task Management API","version":"1.0.0"}`
- API Docs: http://localhost:8000/docs

---

### Step 3: Run the Test Suite

**Option A - Using the batch file:**
```bash
run_tests.bat
```

**Option B - Manual run:**
```bash
# Activate virtual environment
venv\Scripts\activate

# Run tests
python test_auth.py
```

---

## Manual Testing with curl

If you prefer to test manually, here are the curl commands:

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Register a User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"testpass123\",\"name\":\"Test User\"}"
```

**Expected Response (201):**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Save the access token for next steps!**

### 3. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"testpass123\"}"
```

### 4. Get Current User Profile
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### 5. Create a Task (Authenticated)
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Buy groceries\",\"description\":\"Milk, eggs, bread\",\"completed\":false}"
```

### 6. List Tasks (Authenticated)
```bash
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### 7. Test Unauthorized Access (Should Fail)
```bash
curl -X GET http://localhost:8000/api/v1/tasks
# Should return 401 or 403
```

### 8. Logout
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Cookie: refresh_token=YOUR_REFRESH_TOKEN"
```

---

## Testing Checklist

### ✅ Core Authentication
- [ ] User registration works
- [ ] Duplicate email returns 409 Conflict
- [ ] Login with valid credentials works
- [ ] Login with invalid credentials returns 401
- [ ] Access token is returned in response
- [ ] Refresh token is set in httpOnly cookie

### ✅ API Protection
- [ ] GET /auth/me returns user profile with valid token
- [ ] GET /auth/me returns 401 without token
- [ ] Task endpoints require authentication
- [ ] Unauthenticated requests return 401
- [ ] Users can only access their own tasks

### ✅ Session Management
- [ ] Token refresh works
- [ ] Token refresh rotates tokens
- [ ] Logout revokes refresh token
- [ ] Revoked tokens cannot be used

### ✅ Security Features
- [ ] Rate limiting works (try 4+ registrations quickly)
- [ ] Account lockout after 10 failed logins
- [ ] Security headers present in responses
- [ ] Passwords are hashed (check database)

### ✅ Error Handling
- [ ] Invalid email format returns 422
- [ ] Short password returns 422
- [ ] Invalid token returns 401
- [ ] Expired token returns 401

---

## Expected Test Results

When you run `python test_auth.py`, you should see:

```
============================================================
AUTHENTICATION BACKEND TEST SUITE
============================================================

============================================================
TEST: Health Check
============================================================
✅ PASS: Server is healthy: {'status': 'healthy', ...}

============================================================
TEST: User Registration
============================================================
✅ PASS: User registered successfully
  Access Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  Token Type: bearer
  Expires In: 900 seconds
  Refresh Token Cookie: Set

... (more tests) ...

============================================================
TEST SUMMARY
============================================================
✅ PASS: Health Check
✅ PASS: User Registration
✅ PASS: Duplicate Registration
✅ PASS: User Login
✅ PASS: Invalid Login
✅ PASS: Get Current User
✅ PASS: Protected Endpoint Without Token
✅ PASS: Create Task
✅ PASS: List Tasks
✅ PASS: Token Refresh
✅ PASS: Logout

Total: 11/11 tests passed (100.0%)

🎉 All tests passed!
```

---

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use
- Verify DATABASE_URL in .env is correct
- Check if virtual environment is activated
- Run: `pip install -r requirements.txt`

### Redis connection errors
- Verify Redis is running: `redis-cli ping`
- Check REDIS_URL in .env: `redis://localhost:6379`
- Try restarting Redis

### Database connection errors
- Verify DATABASE_URL in .env
- Check Neon database is accessible
- Verify migration is applied: `alembic current`

### 401 Unauthorized errors
- Check if token is included in Authorization header
- Verify token format: `Bearer <token>`
- Check if token has expired (15 min lifetime)

### Rate limiting errors (429)
- This is expected behavior!
- Wait 1 minute and try again
- Or restart Redis to clear rate limits

---

## Next Steps After Testing

Once all tests pass:

1. **Review Security Logs**
   - Check `security.log` file for authentication events
   - Verify logging is working correctly

2. **Test with API Documentation**
   - Open http://localhost:8000/docs
   - Try endpoints interactively
   - Test edge cases

3. **Database Verification**
   - Connect to Neon database
   - Verify users table has test data
   - Check passwords are hashed (not plaintext)
   - Verify refresh_tokens table

4. **Performance Testing**
   - Test with multiple concurrent requests
   - Verify rate limiting works
   - Check response times

5. **Frontend Integration**
   - Backend is ready for frontend
   - Implement Better Auth on Next.js
   - Connect to these endpoints

---

## API Endpoints Summary

| Method | Endpoint | Auth Required | Rate Limit | Description |
|--------|----------|---------------|------------|-------------|
| GET | /health | No | None | Health check |
| POST | /api/v1/auth/register | No | 3/min | Register user |
| POST | /api/v1/auth/login | No | 5/min | Login user |
| POST | /api/v1/auth/refresh | Cookie | 20/min | Refresh token |
| POST | /api/v1/auth/logout | Cookie | 10/min | Logout user |
| GET | /api/v1/auth/me | Yes | 100/min | Get profile |
| POST | /api/v1/tasks | Yes | 100/min | Create task |
| GET | /api/v1/tasks | Yes | 100/min | List tasks |
| GET | /api/v1/tasks/{id} | Yes | 100/min | Get task |
| PATCH | /api/v1/tasks/{id} | Yes | 100/min | Update task |
| DELETE | /api/v1/tasks/{id} | Yes | 100/min | Delete task |

---

**Ready to test!** Start with Step 1 (Redis), then Step 2 (Server), then Step 3 (Tests).
