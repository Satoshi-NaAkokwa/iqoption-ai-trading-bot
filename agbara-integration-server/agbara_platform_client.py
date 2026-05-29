"""
Agbara Platform Client
Handles communication with agbara.ai platform
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgbaraPlatformClient:
    """Client for agbara.ai platform integration"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://agbara.ai/api",
        timeout: int = 30
    ):
        """
        Initialize Agbara platform client

        Args:
            api_key: API key for authentication
            base_url: Base URL for platform API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
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
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Platform": "ikoro-chat-android"
        }

    async def verify_user(self, user_id: str) -> Dict[str, Any]:
        """
        Verify user with platform

        Args:
            user_id: User identifier

        Returns:
            User verification result
        """
        try:
            async with self.session.get(
                f"{self.base_url}/users/{user_id}/verify"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "verified": data.get("verified", False),
                        "user_data": data.get("user"),
                        "digital_id": data.get("digital_id")
                    }
                elif response.status == 404:
                    return {
                        "success": False,
                        "error": "User not found",
                        "verified": False
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Verification failed: {response.status}",
                        "verified": False
                    }

        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return {
                "success": False,
                "error": str(e),
                "verified": False
            }

    async def create_user(
        self,
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new user

        Args:
            user_data: User information

        Returns:
            Creation result
        """
        try:
            async with self.session.post(
                f"{self.base_url}/users",
                json=user_data
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    return {
                        "success": True,
                        "user_id": data.get("user_id"),
                        "digital_id": data.get("digital_id"),
                        "status": "created"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"User creation failed: {response.status}"
                    }

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_balance(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get user balance

        Args:
            user_id: User identifier

        Returns:
            Balance information
        """
        try:
            async with self.session.get(
                f"{self.base_url}/users/{user_id}/balance"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "balance": data.get("balance", 0.0),
                        "currency": data.get("currency", "BTC"),
                        "last_updated": data.get("last_updated")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Balance check failed: {response.status}"
                    }

        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_transaction(
        self,
        user_id: str,
        amount: float,
        recipient_id: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a transaction

        Args:
            user_id: Sender user ID
            amount: Transaction amount
            recipient_id: Recipient user ID
            description: Transaction description
            metadata: Additional metadata

        Returns:
            Transaction result
        """
        try:
            payload = {
                "sender_id": user_id,
                "recipient_id": recipient_id,
                "amount": amount,
                "description": description,
                "metadata": metadata or {},
                "platform": "ikoro-chat"
            }

            async with self.session.post(
                f"{self.base_url}/transactions",
                json=payload
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    return {
                        "success": True,
                        "transaction_id": data.get("transaction_id"),
                        "status": TransactionStatus.PENDING.value,
                        "amount": amount,
                        "fee": data.get("fee", 0.0),
                        "created_at": datetime.now().isoformat()
                    }
                elif response.status == 400:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get("error", "Invalid request"),
                        "code": error_data.get("code")
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

    async def get_transaction_status(
        self,
        transaction_id: str
    ) -> Dict[str, Any]:
        """
        Get transaction status

        Args:
            transaction_id: Transaction identifier

        Returns:
            Transaction status
        """
        try:
            async with self.session.get(
                f"{self.base_url}/transactions/{transaction_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "transaction_id": transaction_id,
                        "status": data.get("status"),
                        "amount": data.get("amount"),
                        "fee": data.get("fee"),
                        "confirmed_at": data.get("confirmed_at")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Status check failed: {response.status}"
                    }

        except Exception as e:
            logger.error(f"Error getting transaction status: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_transaction_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get transaction history

        Args:
            user_id: User identifier
            limit: Number of transactions to return
            offset: Pagination offset

        Returns:
            Transaction history
        """
        try:
            params = {
                "limit": limit,
                "offset": offset
            }

            async with self.session.get(
                f"{self.base_url}/users/{user_id}/transactions",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "transactions": data.get("transactions", []),
                        "total": data.get("total", 0),
                        "limit": limit,
                        "offset": offset
                    }
                else:
                    return {
                        "success": False,
                        "error": f"History fetch failed: {response.status}"
                    }

        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def send_notification(
        self,
        user_id: str,
        notification_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send notification to user

        Args:
            user_id: User identifier
            notification_type: Type of notification
            message: Notification message
            data: Additional data

        Returns:
            Send result
        """
        try:
            payload = {
                "user_id": user_id,
                "type": notification_type,
                "message": message,
                "data": data or {},
                "platform": "ikoro-chat"
            }

            async with self.session.post(
                f"{self.base_url}/notifications",
                json=payload
            ) as response:
                if response.status == 201:
                    return {
                        "success": True,
                        "notification_id": response.json().get("notification_id")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Notification failed: {response.status}"
                    }

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def verify_digital_id(
        self,
        user_id: str,
        digital_id: str
    ) -> Dict[str, Any]:
        """
        Verify digital ID

        Args:
            user_id: User identifier
            digital_id: Digital ID to verify

        Returns:
            Verification result
        """
        try:
            payload = {
                "user_id": user_id,
                "digital_id": digital_id
            }

            async with self.session.post(
                f"{self.base_url}/digital-id/verify",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "valid": data.get("valid", False),
                        "user_matches": data.get("user_matches", False),
                        "expiry_date": data.get("expiry_date")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Verification failed: {response.status}",
                        "valid": False
                    }

        except Exception as e:
            logger.error(f"Error verifying digital ID: {e}")
            return {
                "success": False,
                "error": str(e),
                "valid": False
            }

    async def get_financial_summary(
        self,
        user_id: str,
        period: str = "month"
    ) -> Dict[str, Any]:
        """
        Get financial summary for user

        Args:
            user_id: User identifier
            period: Time period (day, week, month, year)

        Returns:
            Financial summary
        """
        try:
            params = {"period": period}

            async with self.session.get(
                f"{self.base_url}/users/{user_id}/financial-summary",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "summary": data.get("summary", {}),
                        "period": period
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Summary fetch failed: {response.status}"
                    }

        except Exception as e:
            logger.error(f"Error getting financial summary: {e}")
            return {
                "success": False,
                "error": str(e)
            }