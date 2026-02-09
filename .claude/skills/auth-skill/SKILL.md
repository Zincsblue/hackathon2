---
name: auth-skill
description: Implement secure authentication systems including signup, signin, password hashing, JWT tokens, and Better Auth integration.
---

# Authentication System Skill

## Instructions

1. **User Signup**
   - Collect email and password
   - Validate input fields
   - Hash password before saving
   - Store user in database

2. **User Signin**
   - Verify email exists
   - Compare hashed passwords
   - Handle invalid credentials
   - Return auth response

3. **Token Management & Security**
   - Generate secure JWT tokens upon successful authentication
   - Implement "Better Auth" integration for streamlined session handling
   - Use middleware to protect private API routes
   - Ensure secure storage of tokens (e.g., HttpOnly cookies or Secure headers)

## Best Practices
- Use industry-standard hashing algorithms like Argon2 or Bcrypt.
- Implement rate limiting to prevent brute-force attacks on sign-in.
- Always validate and sanitize user inputs to prevent injection attacks.
- Keep secret keys and sensitive configurations in environment variables.

## Example Structure (FastAPI)
```python
from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/signup")
async def signup(user_data: UserCreate):
    hashed_pwd = pwd_context.hash(user_data.password)
    # Save user with hashed_pwd to DB
    return {"message": "User created successfully"}