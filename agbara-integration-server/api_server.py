#!/usr/bin/env python3
"""
Agbara Integration Server
Serves as the bridge between agbara.ai, Agbara AI, and Ikorochat-android
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiohttp

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agbara Integration Server",
    description="Integration layer for Agbara AI ecosystem",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
class DataStore:
    def __init__(self):
        self.agbara_ai_status = {}
        self.user_sessions = {}
        self.message_queue = asyncio.Queue()
        self.analytics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0
        }

store = DataStore()

# Pydantic models
class AgbaraAIRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None
    mode: Optional[str] = "auto"  # auto, local, remote
    igbo_mode: Optional[bool] = False

class AgbaraAIResponse(BaseModel):
    response: str
    expert_used: str
    processing_time: float
    confidence: float
    metadata: Optional[Dict[str, Any]] = None

class PlatformIntegrationRequest(BaseModel):
    platform: str  # agbara.ai, ikoro-chat, etc.
    action: str
    data: Dict[str, Any]
    user_id: str

class PlatformIntegrationResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

# Agbara AI Client
class AgbaraAIClient:
    """Client for communicating with Agbara AI system"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def process_message(
        self,
        message: str,
        igbo_mode: bool = False,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Send message to Agbara AI for processing"""
        try:
            endpoint = "/v1/chat/completions"
            model = "agbara-igbo" if igbo_mode else "agbara"

            payload = {
                "model": model,
                "messages": [{"role": "user", "content": message}],
                "stream": stream
            }

            async with self.session.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "response": data["choices"][0]["message"]["content"],
                        "model": model,
                        "expert_used": self._extract_expert(data),
                        "confidence": 0.95  # Placeholder
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Agbara AI error: {error_text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status}"
                    }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _extract_expert(self, data: Dict) -> str:
        """Extract expert used from response"""
        # This would be enhanced based on actual API response structure
        return "mixed-experts"

# agbara.ai Client
class AgbaraPlatformClient:
    """Client for agbara.ai platform integration"""

    def __init__(self, api_key: str, base_url: str = "https://agbara.ai/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def verify_user(self, user_id: str) -> Dict[str, Any]:
        """Verify user with agbara.ai platform"""
        try:
            async with self.session.get(
                f"{self.base_url}/users/{user_id}/verify",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "verified": data.get("verified", False),
                        "user_data": data
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Verification failed: {response.status}"
                    }

        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_transaction(
        self,
        user_id: str,
        amount: float,
        recipient: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process transaction via agbara.ai"""
        try:
            payload = {
                "user_id": user_id,
                "amount": amount,
                "recipient": recipient,
                "description": description
            }

            async with self.session.post(
                f"{self.base_url}/transactions",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "transaction_id": data.get("transaction_id"),
                        "status": data.get("status")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Transaction failed: {response.status}"
                    }

        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "agbara_ai": "online",
        "agbara_platform": "online",
        "total_requests": store.analytics["total_requests"],
        "success_rate": (
            store.analytics["successful_requests"] /
            store.analytics["total_requests"]
            if store.analytics["total_requests"] > 0 else 0
        ),
        "avg_response_time_ms": store.analytics["avg_response_time"] * 1000
    }

@app.post("/v1/agbara/process", response_model=AgbaraAIResponse)
async def process_agbara_message(request: AgbaraAIRequest):
    """Process message through Agbara AI"""
    start_time = datetime.now()

    try:
        # Update analytics
        store.analytics["total_requests"] += 1

        # Process with Agbara AI
        async with AgbaraAIClient() as agbara_client:
            result = await agbara_client.process_message(
                message=request.message,
                igbo_mode=request.igbo_mode
            )

        if result["success"]:
            # Update success analytics
            store.analytics["successful_requests"] += 1

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Update average response time
            total = store.analytics["total_requests"]
            current_avg = store.analytics["avg_response_time"]
            store.analytics["avg_response_time"] = (
                (current_avg * (total - 1) + processing_time) / total
            )

            return AgbaraAIResponse(
                response=result["response"],
                expert_used=result["expert_used"],
                processing_time=processing_time,
                confidence=result["confidence"],
                metadata={
                    "model": result["model"],
                    "user_id": request.user_id,
                    "igbo_mode": request.igbo_mode
                }
            )
        else:
            store.analytics["failed_requests"] += 1
            raise HTTPException(status_code=500, detail=result["error"])

    except Exception as e:
        store.analytics["failed_requests"] += 1
        logger.error(f"Error processing Agbara message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/platform/integrate", response_model=PlatformIntegrationResponse)
async def integrate_platform(request: PlatformIntegrationRequest):
    """Integrate with various platforms"""
    try:
        if request.platform == "agbara.ai":
            # Handle agbara.ai integration
            result = await _handle_agbara_platform(request)
        elif request.platform == "ikoro-chat":
            # Handle Ikorochat integration
            result = await _handle_ikoro_chat(request)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown platform: {request.platform}"
            )

        return PlatformIntegrationResponse(
            success=result["success"],
            result=result.get("result"),
            error=result.get("error"),
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Platform integration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()

    try:
        # Get user ID from query params
        user_id = websocket.query_params.get("user_id")
        if not user_id:
            await websocket.close(code=4001, reason="Missing user_id")
            return

        logger.info(f"WebSocket connection established for user: {user_id}")

        # Store connection
        store.user_sessions[user_id] = websocket

        while True:
            # Receive message
            data = await websocket.receive_json()

            # Process message
            request = AgbaraAIRequest(
                user_id=user_id,
                message=data.get("message", ""),
                igbo_mode=data.get("igbo_mode", False)
            )

            # Get response from Agbara AI
            async with AgbaraAIClient() as agbara_client:
                result = await agbara_client.process_message(
                    message=request.message,
                    igbo_mode=request.igbo_mode
                )

            # Send response
            response = {
                "type": "response",
                "data": {
                    "response": result.get("response", ""),
                    "expert_used": result.get("expert_used", ""),
                    "confidence": result.get("confidence", 0.0)
                }
            }

            await websocket.send_json(response)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {user_id}")
        if user_id in store.user_sessions:
            del store.user_sessions[user_id]

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=4000, reason=str(e))

# Helper functions
async def _handle_agbara_platform(request: PlatformIntegrationRequest) -> Dict:
    """Handle agbara.ai platform integration"""
    # This would be implemented with actual API calls to agbara.ai
    return {
        "success": True,
        "result": {
            "platform": "agbara.ai",
            "action": request.action,
            "status": "processed"
        }
    }

async def _handle_ikoro_chat(request: PlatformIntegrationRequest) -> Dict:
    """Handle Ikorochat integration"""
    # This would be implemented with actual Ikorochat integration
    return {
        "success": True,
        "result": {
            "platform": "ikoro-chat",
            "action": request.action,
            "status": "processed"
        }
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    logger.info("Agbara Integration Server starting up...")

    # Initialize Agbara AI connection
    # This would check if Agbara AI is running
    store.agbara_ai_status["status"] = "online"
    store.agbara_ai_status["timestamp"] = datetime.now().isoformat()

    logger.info("Agbara Integration Server started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    logger.info("Agbara Integration Server shutting down...")

    # Close all user sessions
    for user_id, websocket in store.user_sessions.items():
        try:
            await websocket.close()
        except Exception as e:
            logger.error(f"Error closing WebSocket for {user_id}: {e}")

    logger.info("Agbara Integration Server shutdown complete")

if __name__ == "__main__":
    import uvicorn

    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )