# Research: Authentication & Security Best Practices

**Project Context**: Todo Full-Stack Web Application (FastAPI + Next.js + Better Auth)
**Security Level**: Moderate (multi-user web application with personal data)
**Date**: 2026-02-08

---

## 1. Password Requirements

**Decision**: Minimum 8 characters, no complexity requirements, check against common password list

**Rationale**:
- NIST SP 800-63B (Digital Identity Guidelines) recommends minimum 8 characters for user-chosen passwords
- Length is more important than complexity for password strength
- Complexity requirements (special characters, numbers, etc.) lead to predictable patterns and user frustration
- Checking against common/breached password lists (e.g., Have I Been Pwned) provides better security than arbitrary complexity rules
- Users should be allowed to use spaces and all printable ASCII/Unicode characters
- Maximum length should be at least 64 characters to accommodate passphrases

**Alternatives Considered**:
- **Complex requirements (uppercase, lowercase, numbers, special chars)**: Rejected because research shows this leads to weaker passwords (e.g., "Password1!") and poor user experience
- **Minimum 12+ characters**: More secure but may create friction for a todo app; 8 characters is acceptable for moderate security needs
- **No minimum length**: Unacceptable security risk

**Implementation Notes**:
- Use a library like `pwnedpasswords` to check against breached password database
- Provide real-time password strength feedback in the UI
- Allow password managers to generate and store passwords

---

## 2. JWT Token Lifetime

**Decision**:
- Access Token: 15 minutes
- Refresh Token: 7 days

**Rationale**:
- **Short-lived access tokens** (15 minutes) limit the window of opportunity if a token is compromised
- Access tokens are sent with every API request, increasing exposure risk
- **Longer refresh tokens** (7 days) balance security with user experience
- Refresh tokens are only used occasionally (when access token expires) and can be stored more securely
- 7 days allows users to stay logged in for a week without re-authentication, suitable for a productivity app
- Refresh tokens can be revoked server-side if needed (unlike stateless access tokens)

**Alternatives Considered**:
- **Access Token: 5 minutes**: More secure but causes too many refresh requests, impacting UX and server load
- **Access Token: 1 hour**: Reduces refresh frequency but increases risk window significantly
- **Refresh Token: 30 days**: Better UX but increases security risk for a multi-user app
- **No refresh token (long-lived access token)**: Simpler but cannot revoke sessions without maintaining a blacklist

**Implementation Notes**:
- Store refresh token expiry in database to enable server-side revocation
- Implement token rotation: issue new refresh token with each refresh request
- Add "Remember Me" option that extends refresh token to 30 days

---

## 3. Session Persistence

**Decision**: Use httpOnly cookies for refresh tokens with persistent storage

**Rationale**:
- httpOnly cookies persist across browser restarts automatically
- Cookies with appropriate expiration dates (matching refresh token lifetime) provide seamless session persistence
- Users expect to remain logged in after closing/reopening browser in modern web apps
- Refresh token in httpOnly cookie can be used to obtain new access token on app load
- Provides good balance between security and user experience

**Alternatives Considered**:
- **localStorage for tokens**: Persists across restarts but vulnerable to XSS attacks
- **sessionStorage only**: More secure but loses session on browser close, poor UX
- **No persistence (always require login)**: Maximum security but unacceptable UX for a productivity app
- **Server-side sessions only**: More secure but requires session storage/database and doesn't work well with stateless APIs

**Implementation Notes**:
- Set cookie attributes: `httpOnly=true`, `secure=true`, `sameSite=strict`
- Frontend should check for valid refresh token on app initialization
- Implement automatic token refresh before access token expires
- Provide explicit "Logout" that clears the refresh token cookie

---

## 4. JWT Implementation in FastAPI

**Decision**: Use `python-jose[cryptography]` library with HS256 algorithm

**Rationale**:
- `python-jose` is the most commonly used JWT library in FastAPI ecosystem
- Well-documented with extensive FastAPI examples in official documentation
- Supports multiple algorithms (HS256, RS256, etc.)
- HS256 (HMAC with SHA-256) is sufficient for single-backend architecture
- Simpler than RS256 (no key pair management needed)
- Good performance for token generation and verification
- Active maintenance and security updates

**Alternatives Considered**:
- **PyJWT**: Also popular and well-maintained, but python-jose has better FastAPI integration examples
- **RS256 algorithm**: More secure for distributed systems but overkill for single backend; requires managing public/private key pairs
- **authlib**: More comprehensive but heavier; unnecessary for our use case
- **Custom JWT implementation**: Never recommended due to security risks

**Implementation Notes**:
```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key-from-env"  # Must be in .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

**Dependencies**:
- `python-jose[cryptography]` - JWT handling
- `passlib[bcrypt]` or `argon2-cffi` - Password hashing
- `python-multipart` - Form data handling

---

## 5. Better Auth Integration

**Decision**: Use Better Auth for frontend session management, issue JWT tokens for backend API authentication

**Rationale**:
- Better Auth handles Next.js authentication flow (login UI, session management, cookies)
- Better Auth can be configured to include custom session data (like JWT tokens)
- Frontend uses Better Auth's session management
- Backend (FastAPI) independently verifies JWT tokens from Authorization header
- Separation of concerns: Better Auth manages user sessions, FastAPI validates API requests
- Better Auth provides built-in features: email verification, password reset, OAuth providers

**Alternatives Considered**:
- **NextAuth.js**: Popular but Better Auth is more modern and has better TypeScript support
- **Custom Next.js auth**: More control but requires implementing all auth flows from scratch
- **Backend-only auth (no Better Auth)**: Simpler but loses Next.js-specific optimizations and features
- **Shared session store**: Tighter coupling but adds complexity and single point of failure

**Implementation Approach**:
1. Better Auth handles user registration, login, and session creation in Next.js
2. On successful login, Better Auth creates session and stores user info
3. Frontend includes JWT token (from Better Auth session or separate endpoint) in API requests
4. FastAPI validates JWT token independently using shared secret
5. Both systems can access user ID from token/session to filter data

**Configuration Notes**:
- Share SECRET_KEY between Better Auth and FastAPI (via environment variables)
- Better Auth session cookie domain must match Next.js domain
- API requests include: `Authorization: Bearer <jwt_token>`
- Consider using Better Auth's database adapter to share user table with FastAPI

---

## 6. Token Storage

**Decision**:
- **Refresh Token**: httpOnly cookie (set by backend)
- **Access Token**: React state/context (memory only, not persisted)

**Rationale**:
- **httpOnly cookies** cannot be accessed by JavaScript, protecting against XSS attacks
- Refresh tokens are long-lived and more valuable to attackers, so they need maximum protection
- Access tokens are short-lived (15 min) and kept in memory, minimizing exposure
- If access token is stolen via XSS, it expires quickly
- Cookies are automatically sent with requests to same domain
- `sameSite=strict` attribute prevents CSRF attacks
- Memory storage means access token is lost on page refresh, but can be regenerated from refresh token

**Alternatives Considered**:
- **localStorage for all tokens**: Simple but vulnerable to XSS; any malicious script can steal tokens
- **sessionStorage for all tokens**: Better than localStorage but still XSS-vulnerable
- **Cookies for both tokens**: More secure but access token in cookie increases CSRF risk
- **IndexedDB**: Similar security profile to localStorage, adds complexity

**Security Comparison**:

| Storage Method | XSS Vulnerable | CSRF Vulnerable | Persists | Best For |
|----------------|----------------|-----------------|----------|----------|
| localStorage | Yes | No | Yes | Not recommended for tokens |
| sessionStorage | Yes | No | No | Not recommended for tokens |
| httpOnly Cookie | No | Yes (mitigated by sameSite) | Yes | Refresh tokens |
| Memory (state) | Yes (but short-lived) | No | No | Access tokens |

**Implementation Notes**:
```javascript
// Frontend: Store access token in React context
const [accessToken, setAccessToken] = useState(null);

// Refresh token is in httpOnly cookie (not accessible to JS)
// Backend sets cookie with: Set-Cookie: refresh_token=...; HttpOnly; Secure; SameSite=Strict

// API calls include access token in header
fetch('/api/tasks', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
```

---

## 7. Rate Limiting

**Decision**: Use `slowapi` with Redis backend for distributed rate limiting

**Rationale**:
- `slowapi` is a FastAPI-compatible port of Flask-Limiter
- Familiar decorator-based syntax: `@limiter.limit("5/minute")`
- Supports multiple storage backends (memory, Redis)
- Redis backend enables rate limiting across multiple API instances
- Essential for preventing brute force attacks on login endpoint
- Can apply different limits to different endpoints
- Provides clear error messages to clients (429 Too Many Requests)

**Rate Limit Strategy**:
- **Login endpoint**: 5 attempts per minute per IP
- **Registration endpoint**: 3 attempts per minute per IP
- **Password reset**: 3 attempts per hour per email
- **General API endpoints**: 100 requests per minute per user
- **Public endpoints**: 20 requests per minute per IP

**Alternatives Considered**:
- **fastapi-limiter**: Good alternative, similar features but less documentation
- **Custom middleware**: More control but requires implementing rate limiting logic from scratch
- **No rate limiting**: Unacceptable security risk for authentication endpoints
- **API Gateway rate limiting**: Better for production but adds infrastructure complexity

**Implementation Notes**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginCredentials):
    # Login logic
    pass
```

**Additional Security Measures**:
- Implement account lockout after 10 failed attempts (requires database tracking)
- Add CAPTCHA after 3 failed attempts
- Log failed login attempts for security monitoring
- Consider progressive delays (exponential backoff) for repeated failures

---

## 8. Password Hashing

**Decision**: Use Argon2id (via `argon2-cffi` library)

**Rationale**:
- **Argon2** won the Password Hashing Competition (2015) and is the modern standard
- **Argon2id** variant provides best balance: resistant to both side-channel and GPU attacks
- Memory-hard algorithm makes brute force attacks expensive
- Configurable time and memory costs allow tuning for security/performance balance
- Recommended by OWASP, NIST, and security experts
- Python implementation (`argon2-cffi`) is well-maintained and uses C bindings for performance
- Future-proof: designed to remain secure as hardware improves

**Alternatives Considered**:
- **bcrypt**: Still acceptable and widely used, but older (1999) and less resistant to GPU attacks than Argon2
- **scrypt**: Good memory-hard algorithm but Argon2 is newer and more configurable
- **PBKDF2**: Older standard, not memory-hard, vulnerable to GPU attacks; not recommended for new projects
- **SHA-256/SHA-512**: Fast hashing algorithms, NOT suitable for passwords (too fast = easy to brute force)

**Performance Comparison**:
- Argon2: ~100-500ms per hash (configurable)
- bcrypt: ~100-300ms per hash (configurable)
- PBKDF2: ~50-200ms per hash (configurable)
- SHA-256: <1ms per hash (TOO FAST for passwords)

**Implementation Notes**:
```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=2,        # Number of iterations
    memory_cost=65536,  # Memory usage in KiB (64 MB)
    parallelism=1,      # Number of parallel threads
    hash_len=32,        # Length of hash in bytes
    salt_len=16         # Length of salt in bytes
)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hash: str) -> bool:
    try:
        ph.verify(hash, password)
        # Check if hash needs rehashing (parameters changed)
        if ph.check_needs_rehash(hash):
            return "rehash_needed"
        return True
    except VerifyMismatchError:
        return False
```

**Configuration Rationale**:
- `time_cost=2`: 2 iterations, balances security and performance
- `memory_cost=65536`: 64 MB memory, makes GPU attacks expensive
- `parallelism=1`: Single thread, sufficient for web app (login is not parallelized)
- These settings provide ~200-300ms hash time, acceptable for login operations

**Migration from bcrypt** (if needed):
- Keep existing bcrypt hashes in database
- On successful login with bcrypt hash, rehash with Argon2 and update database
- Gradually migrate all passwords over time

**Dependencies**:
```
argon2-cffi==23.1.0  # Argon2 password hashing
```

---

## Summary: Recommended Security Stack

### Backend (FastAPI)
```python
# requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
python-jose[cryptography]==3.3.0
argon2-cffi==23.1.0
slowapi==0.1.9
redis==5.0.1
python-multipart==0.0.6
```

### Frontend (Next.js)
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "better-auth": "^1.0.0",
    "react": "^18.2.0"
  }
}
```

### Environment Variables
```bash
# Backend (.env)
SECRET_KEY=<generate-with-openssl-rand-hex-32>
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://localhost:6379
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=<same-as-backend-SECRET_KEY>
```

### Security Checklist
- [ ] Passwords: Min 8 chars, check against breached password list
- [ ] Hashing: Argon2id with appropriate cost parameters
- [ ] Tokens: 15-min access token, 7-day refresh token
- [ ] Storage: httpOnly cookies for refresh, memory for access
- [ ] Rate Limiting: 5 login attempts/min, 100 API requests/min
- [ ] HTTPS: Enforce in production (secure cookies)
- [ ] CORS: Configure allowed origins
- [ ] Input Validation: Validate all user inputs
- [ ] SQL Injection: Use SQLModel parameterized queries
- [ ] XSS Protection: Sanitize outputs, use Content Security Policy
- [ ] CSRF Protection: sameSite=strict cookies
- [ ] Logging: Log authentication events (success/failure)
- [ ] Monitoring: Alert on unusual patterns (many failed logins)

---

## References & Standards

- **NIST SP 800-63B**: Digital Identity Guidelines (Password requirements)
- **OWASP**: Authentication Cheat Sheet, Password Storage Cheat Sheet
- **RFC 7519**: JSON Web Token (JWT) standard
- **RFC 6749**: OAuth 2.0 Authorization Framework
- **Argon2**: Password Hashing Competition winner (2015)
- **FastAPI Security Documentation**: Official OAuth2 with Password and Bearer guide
- **Better Auth Documentation**: Next.js authentication library

---

## Next Steps

1. **Review with team**: Ensure these decisions align with project requirements
2. **Document in ADR**: Create Architecture Decision Record for authentication approach
3. **Update spec**: Incorporate these decisions into authentication feature spec
4. **Implementation order**:
   - Set up database schema for users and refresh tokens
   - Implement password hashing and user registration
   - Implement JWT token generation and verification
   - Add rate limiting middleware
   - Integrate Better Auth in Next.js frontend
   - Test authentication flow end-to-end
   - Add security headers and CORS configuration

---

**Document Status**: Draft for Review
**Last Updated**: 2026-02-08
**Author**: Claude Code (Research Agent)
