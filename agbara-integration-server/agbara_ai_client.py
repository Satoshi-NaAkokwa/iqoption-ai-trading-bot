"""
Agbara AI Client
Handles communication with the Agbara AI multi-modal system
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class AgbaraAIClient:
    """Client for Agbara AI multi-modal system"""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize Agbara AI client

        Args:
            base_url: Base URL for Agbara AI server
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=self._get_headers()
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if Agbara AI is healthy

        Returns:
            Health status
        """
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "status": "unhealthy",
                        "code": response.status
                    }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status

        Returns:
            System status information
        """
        try:
            async with self.session.get(f"{self.base_url}/status") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status check failed: {response.status}"}
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {"error": str(e)}

    async def process_message(
        self,
        message: str,
        user_id: str,
        igbo_mode: bool = False,
        preferred_expert: Optional[str] = None,
        stream: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a message through Agbara AI

        Args:
            message: User message
            user_id: User identifier
            igbo_mode: Enable Igbo language mode
            preferred_expert: Preferred expert model
            stream: Enable streaming response
            context: Additional context

        Returns:
            AI response
        """
        try:
            endpoint = "/v1/chat/completions"
            model = "agbara-igbo" if igbo_mode else "agbara"

            payload = {
                "model": model,
                "messages": [{"role": "user", "content": message}],
                "stream": stream,
                "user": user_id
            }

            if context:
                payload["context"] = context

            if preferred_expert:
                payload["expert"] = preferred_expert

            async with self.session.post(
                f"{self.base_url}{endpoint}",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()

                    # Parse response
                    if data.get("choices"):
                        choice = data["choices"][0]
                        message_obj = choice.get("message", {})
                        return {
                            "success": True,
                            "response": message_obj.get("content", ""),
                            "model": model,
                            "expert_used": data.get("expert_used", "mixed-experts"),
                            "confidence": data.get("confidence", 0.9),
                            "processing_time": data.get("processing_time", 0),
                            "metadata": data.get("metadata", {})
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Invalid response format"
                        }
                else:
                    error_text = await response.text()
                    logger.error(f"Agbara AI error: {error_text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status}",
                        "details": error_text
                    }

        except asyncio.TimeoutError:
            logger.error("Request timeout")
            return {
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_stream(
        self,
        message: str,
        user_id: str,
        igbo_mode: bool = False
    ):
        """
        Process message with streaming response

        Args:
            message: User message
            user_id: User identifier
            igbo_mode: Enable Igbo language mode

        Yields:
            Stream chunks
        """
        try:
            endpoint = "/v1/chat/completions"
            model = "agbara-igbo" if igbo_mode else "agbara"

            payload = {
                "model": model,
                "messages": [{"role": "user", "content": message}],
                "stream": True,
                "user": user_id
            }

            async with self.session.post(
                f"{self.base_url}{endpoint}",
                json=payload
            ) as response:
                if response.status == 200:
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data_str = line[6:]  # Remove 'data: ' prefix
                            if data_str == '[DONE]':
                                break
                            try:
                                import json
                                data = json.loads(data_str)
                                if data.get("choices"):
                                    choice = data["choices"][0]
                                    delta = choice.get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield {
                                            "type": "chunk",
                                            "content": content
                                        }
                            except json.JSONDecodeError:
                                continue
                else:
                    yield {
                        "type": "error",
                        "error": f"Stream error: {response.status}"
                    }

        except Exception as e:
            logger.error(f"Stream processing error: {e}")
            yield {
                "type": "error",
                "error": str(e)
            }

    async def get_igbo_proverb(self) -> Dict[str, Any]:
        """
        Get a random Igbo proverb

        Returns:
            Proverb with translation and meaning
        """
        try:
            async with self.session.get(f"{self.base_url}/v1/igbo/proverb") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Failed to get proverb: {response.status}"}
        except Exception as e:
            logger.error(f"Error getting Igbo proverb: {e}")
            return {"error": str(e)}

    async def translate_igbo(
        self,
        text: str,
        direction: str = "igbo-to-english"
    ) -> Dict[str, Any]:
        """
        Translate Igbo text

        Args:
            text: Text to translate
            direction: Translation direction (igbo-to-english or english-to-igbo)

        Returns:
            Translation result
        """
        try:
            params = {
                "text": text,
                "direction": direction
            }

            async with self.session.get(
                f"{self.base_url}/v1/igbo/translate",
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Translation failed: {response.status}"}
        except Exception as e:
            logger.error(f"Error translating Igbo: {e}")
            return {"error": str(e)}

    async def explain_cultural_concept(self, concept: str) -> Dict[str, Any]:
        """
        Explain an Igbo cultural concept

        Args:
            concept: Cultural concept name (e.g., "Chi", "Omenala")

        Returns:
            Concept explanation
        """
        try:
            params = {"concept": concept}

            async with self.session.get(
                f"{self.base_url}/v1/igbo/concept",
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Concept lookup failed: {response.status}"}
        except Exception as e:
            logger.error(f"Error explaining concept: {e}")
            return {"error": str(e)}

    async def get_experts(self) -> List[Dict[str, Any]]:
        """
        Get list of available expert models

        Returns:
            List of expert models
        """
        try:
            async with self.session.get(f"{self.base_url}/v1/experts") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("experts", [])
                else:
                    return []
        except Exception as e:
            logger.error(f"Error getting experts: {e}")
            return []

    async def load_expert(self, expert_name: str) -> Dict[str, Any]:
        """
        Load a specific expert model

        Args:
            expert_name: Name of expert to load

        Returns:
            Load status
        """
        try:
            async with self.session.post(
                f"{self.base_url}/v1/experts/{expert_name}/load"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Failed to load expert: {response.status}"}
        except Exception as e:
            logger.error(f"Error loading expert: {e}")
            return {"error": str(e)}

    async def batch_process(
        self,
        messages: List[Dict[str, Any]],
        igbo_mode: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Process multiple messages in batch

        Args:
            messages: List of message dictionaries with 'user_id' and 'message'
            igbo_mode: Enable Igbo language mode

        Returns:
            List of responses
        """
        tasks = []
        for msg in messages:
            task = self.process_message(
                message=msg["message"],
                user_id=msg["user_id"],
                igbo_mode=igbo_mode,
                context=msg.get("context")
            )
            tasks.append(task)

        return await asyncio.gather(*tasks, return_exceptions=True)