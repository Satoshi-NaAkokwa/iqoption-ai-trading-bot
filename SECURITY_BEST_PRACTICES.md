# Security Best Practices - Agbara Integration

## Overview

This guide outlines security best practices for integrating Agbara into your Android applications and Python servers.

---

## Android SDK Security

### 1. API Key Management

#### ❌ Bad Practice
```kotlin
// NEVER hardcode API keys in your code
val apiKey = "sk-live-1234567890abcdefghijklmnopqrstuvwxyz"
```

#### ✅ Good Practice
```kotlin
// 1. Store in local.properties (not committed to git)
// local.properties
AGBARA_API_KEY=sk-live-1234567890abcdefghijklmnopqrstuvwxyz

// 2. Add to build.gradle.kts
android {
    defaultConfig {
        buildConfigField(
            "String",
            "AGBARA_API_KEY",
            "\"${properties["AGBARA_API_KEY"]}\""
        )
    }
}

// 3. Use in code
val apiKey = BuildConfig.AGBARA_API_KEY
```

### 2. Use ProGuard/R8

Add to `proguard-rules.pro`:
```proguard
# Keep Agbara SDK classes
-keep class com.agbara.sdk.** { *; }

# Keep data classes
-keepclassmembers class com.agbara.sdk.models.** { *; }

# Keep enum classes
-keepclassmembers enum com.agbara.sdk.** { *; }

# Obfuscate sensitive data
-obfuscate
-optimizationpasses 5
-dontusemixedcaseclassnames
-dontskipnonpubliclibraryclasses
-dontpreverify
-verbose
-optimizations !code/simplification/arithmetic,!field/*,!class/merging/*
```

### 3. Secure Data Storage

#### ✅ Use Encrypted Preferences
```kotlin
import androidx.security.crypto.EncryptedSharedPreferences

val encryptedPrefs = EncryptedSharedPreferences.create(
    "agbara_secrets",
    "agbara_master_key",
    context,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// Store sensitive data
encryptedPrefs.edit()
    .putString("user_id", userId)
    .putString("auth_token", authToken)
    .apply()
```

#### ✅ Use Encrypted File Storage
```kotlin
import androidx.security.crypto.EncryptedFile

val encryptedFile = EncryptedFile.Builder(
    File(context.filesDir, "user_data.json"),
    context,
    "agbara_master_key",
    EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
).build()

val fileContent = encryptedFile.openFileInput().bufferedReader().use { it.readText() }
```

### 4. Network Security

#### ✅ Use HTTPS Only
```kotlin
val config = AgbaraConfig(
    apiKey = BuildConfig.AGBARA_API_KEY,
    baseUrl = "https://api.agbara.ai",  // Always HTTPS
    webSocketUrl = "wss://api.agbara.ai/ws/chat"  // WSS for WebSocket
)
```

#### ✅ Implement Certificate Pinning
```kotlin
val okHttpClient = OkHttpClient.Builder()
    .certificatePinner(
        CertificatePinner.Builder()
            .add("api.agbara.ai", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
            .build()
    )
    .build()
```

### 5. User Privacy

#### ✅ Anonymize User Data
```kotlin
// Generate anonymous user ID
fun generateAnonymousUserId(): String {
    val random = java.security.SecureRandom()
    val bytes = ByteArray(16)
    random.nextBytes(bytes)
    return bytes.joinToString("") { "%02x".format(it) }
}

// Use in requests
val request = AgbaraAIRequest(
    userId = generateAnonymousUserId(),  // Anonymous
    message = message,
    context = mapOf(
        "platform" to "android",
        "version" to BuildConfig.VERSION_NAME
    )
)
```

#### ✅ Sanitize User Input
```kotlin
import com.agbara.sdk.Utils

val sanitizedMessage = Utils.sanitizeInput(userInput)
val validatedMessage = Validation.validateMessage(sanitizedMessage)

when (validatedMessage) {
    is Validation.SUCCESS -> {
        sendRequest(validatedMessage)
    }
    is Validation.ERROR -> {
        showValidationError(validatedMessage.message)
    }
}
```

### 6. Permission Management

#### ✅ Request Permissions at Runtime
```kotlin
private const val LOCATION_PERMISSION_REQUEST_CODE = 1001

fun requestLocationPermission() {
    if (ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) != PackageManager.PERMISSION_GRANTED
    ) {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(Manifest.permission.ACCESS_FINE_LOCATION),
            LOCATION_PERMISSION_REQUEST_CODE
        )
    } else {
        // Permission already granted
        proceedWithLocationBasedFeatures()
    }
}

override fun onRequestPermissionsResult(
    requestCode: Int,
    permissions: Array<out String>,
    grantResults: IntArray
) {
    super.onRequestPermissionsResult(requestCode, permissions, grantResults)
    
    if (requestCode == LOCATION_PERMISSION_REQUEST_CODE) {
        if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            proceedWithLocationBasedFeatures()
        } else {
            showPermissionDeniedMessage()
        }
    }
}
```

---

## Python Server Security

### 1. Environment Variables

#### ✅ Use Environment Variables
```python
# .env (NEVER commit to git)
AGBARA_API_KEY=sk-live-1234567890abcdefghijklmnopqrstuvwxyz
DATABASE_URL=postgresql://user:password@localhost/db
SECRET_KEY=your-secret-key-here

# Load in code
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AGBARA_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
```

### 2. Input Validation

#### ✅ Validate All Inputs
```python
from pydantic import BaseModel, validator

class ChatRequest(BaseModel):
    message: str
    user_id: str
    model: str = "agbara"

    @validator('message')
    def validate_message(cls, v):
        if not v or len(v) > 10000:
            raise ValueError("Message must be 1-10000 characters")
        
        # Sanitize input
        import re
        v = re.sub(r'<[^>]+>', '', v)  # Remove HTML tags
        return v

    @validator('user_id')
    def validate_user_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Invalid user ID format")
        return v
```

### 3. Authentication & Authorization

#### ✅ Implement JWT Authentication
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Use in endpoints
@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatRequest,
    user_id: str = Depends(verify_token)
):
    # Process request
    pass
```

### 4. Rate Limiting

#### ✅ Implement Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded"}
    )

@app.post("/v1/chat/completions")
@limiter.limit("100/minute")
async def chat_completions(
    request: Request,
    chat_request: ChatRequest,
    user_id: str = Depends(verify_token)
):
    # Process request
    pass
```

### 5. SQL Injection Prevention

#### ✅ Use Parameterized Queries
```python
import asyncpg

# ❌ Bad - SQL injection vulnerability
async def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    return await db.fetch(query)

# ✅ Good - Parameterized query
async def get_user(user_id):
    query = "SELECT * FROM users WHERE id = $1"
    return await db.fetch(query, user_id)
```

### 6. CORS Configuration

#### ✅ Configure CORS Properly
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## Data Security

### 1. Encryption at Rest

#### ✅ Encrypt Sensitive Data
```python
from cryptography.fernet import Fernet

# Generate encryption key
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Encrypt data
encrypted_data = cipher_suite.encrypt(b"sensitive data")

# Decrypt data
decrypted_data = cipher_suite.decrypt(encrypted_data)
```

### 2. Secure Logging

#### ✅ Sanitize Logs
```python
import logging

logger = logging.getLogger(__name__)

def log_user_action(user_id, action):
    # Sanitize user_id
    sanitized_id = user_id[:8] + "..."  # Truncate
    logger.info(f"User {sanitized_id} performed {action}")

# ❌ Bad - Logs sensitive data
logger.info(f"User sk-live-1234567890 performed action")

# ✅ Good - Sanitized logs
logger.info(f"User sk-live-... performed action")
```

### 3. Data Retention

#### ✅ Implement Data Retention Policy
```python
from datetime import datetime, timedelta
import asyncio

async def cleanup_old_logs():
    cutoff_date = datetime.now() - timedelta(days=90)
    
    query = """
        DELETE FROM user_logs 
        WHERE created_at < $1
    """
    
    await db.execute(query, cutoff_date)

async def cleanup_old_analytics():
    cutoff_date = datetime.now() - timedelta(days=30)
    
    query = """
        DELETE FROM analytics_data 
        WHERE created_at < $1
    """
    
    await db.execute(query, cutoff_date)

# Schedule cleanup
import asyncio
async def schedule_cleanup():
    while True:
        await cleanup_old_logs()
        await cleanup_old_analytics()
        await asyncio.sleep(24 * 3600)  # Run daily
```

---

## Web Security

### 1. HTTPS Enforcement

#### ✅ Force HTTPS
```python
from fastapi import Request
from fastapi.responses import RedirectResponse

@app.middleware("http")
async def enforce_https(request: Request, call_next):
    if request.url.scheme != "https":
        url = request.url.replace(scheme="https")
        return RedirectResponse(url, status_code=301)
    
    response = await call_next(request)
    return response
```

### 2. Security Headers

#### ✅ Add Security Headers
```python
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

## Compliance

### 1. GDPR Compliance

#### ✅ Data Minimization
```python
# Only collect necessary data
class UserProfile(BaseModel):
    user_id: str
    email: str  # Only if needed
    preferences: Optional[dict] = None  # Optional
    
    # ❌ Don't collect unnecessary data
    # full_name: str  # Not needed
    # phone_number: str  # Not needed
```

#### ✅ Right to be Forgotten
```python
@app.delete("/users/{user_id}")
async def delete_user_data(user_id: str):
    # Delete all user data
    await db.execute("DELETE FROM users WHERE id = $1", user_id)
    await db.execute("DELETE FROM user_logs WHERE user_id = $1", user_id)
    await db.execute("DELETE FROM analytics WHERE user_id = $1", user_id)
    
    return {"message": "User data deleted"}
```

### 2. CCPA Compliance

#### ✅ Data Export
```python
@app.get("/users/{user_id}/export")
async def export_user_data(user_id: str):
    # Export all user data
    user_data = await db.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    logs = await db.fetch("SELECT * FROM user_logs WHERE user_id = $1", user_id)
    
    export = {
        "profile": user_data,
        "logs": logs,
        "export_date": datetime.now().isoformat()
    }
    
    return export
```

---

## Security Checklist

### Android SDK

- [x] API keys stored securely (BuildConfig, not hardcoded)
- [x] ProGuard/R8 enabled for code obfuscation
- [x] Encrypted preferences for sensitive data
- [x] HTTPS/WSS enforced for all communications
- [x] Certificate pinning implemented
- [x] User data anonymized
- [x] Input validation and sanitization
- [x] Runtime permission requests
- [x] No sensitive data in logs

### Python Server

- [x] Environment variables for secrets
- [x] Input validation using Pydantic
- [x] JWT authentication implemented
- [x] Rate limiting configured
- [x] Parameterized queries (SQL injection prevention)
- [x] CORS properly configured
- [x] Security headers added
- [x] HTTPS enforced
- [x] Data encryption at rest
- [x] Sanitized logging

### Data Privacy

- [x] GDPR compliant (data minimization, right to be forgotten)
- [x] CCPA compliant (data export)
- [x] Data retention policy implemented
- [x] No PII in logs
- [x] User consent mechanism

---

**For more information, see the Developer Guide and API Reference.**