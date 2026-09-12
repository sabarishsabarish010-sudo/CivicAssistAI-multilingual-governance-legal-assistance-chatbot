from __future__ import annotations

import logging
from typing import Any, Dict, Optional


logger = logging.getLogger(__name__)


class NotificationService:
    """
    Handles CivicAssist notification events.

    The service is intentionally provider-independent. It records and
    validates notification requests without hard-coding an external
    SMS, email, WhatsApp, or push-notification provider.
    """

    def __init__(self) -> None:
        self.enabled = True

    async def notify(
        self,
        recipient: str,
        message: str,
        notification_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        recipient = recipient.strip()
        message = message.strip()
        notification_type = notification_type.strip().lower()

        if not recipient:
            raise ValueError("Notification recipient cannot be empty.")

        if not message:
            raise ValueError("Notification message cannot be empty.")

        if not notification_type:
            raise ValueError("Notification type cannot be empty.")

        if not self.enabled:
            return {
                "status": "disabled",
                "notification_type": notification_type,
            }

        notification_data = {
            "recipient": recipient,
            "message": message,
            "notification_type": notification_type,
            "metadata": metadata or {},
        }

        logger.info(
            "Notification event created: type=%s",
            notification_type,
        )

        return {
            "status": "queued",
            "notification_type": notification_type,
            "recipient": recipient,
            "metadata": notification_data["metadata"],
        }

    async def notify_scheme_update(
        self,
        recipient: str,
        scheme_id: str,
        message: str,
    ) -> Dict[str, Any]:
        scheme_id = scheme_id.strip()

        if not scheme_id:
            raise ValueError("Scheme ID cannot be empty.")

        return await self.notify(
            recipient=recipient,
            message=message,
            notification_type="scheme_update",
            metadata={
                "scheme_id": scheme_id,
            },
        )

    async def notify_application_update(
        self,
        recipient: str,
        application_id: str,
        message: str,
    ) -> Dict[str, Any]:
        application_id = application_id.strip()

        if not application_id:
            raise ValueError("Application ID cannot be empty.")

        return await self.notify(
            recipient=recipient,
            message=message,
            notification_type="application_update",
            metadata={
                "application_id": application_id,
            },
        )


_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    global _service

    if _service is None:
        _service = NotificationService()

    return _service


async def send_notification(
    recipient: str,
    message: str,
    notification_type: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    service = get_notification_service()

    return await service.notify(
        recipient=recipient,
        message=message,
        notification_type=notification_type,
        metadata=metadata,
    )


async def notify_scheme_update(
    recipient: str,
    scheme_id: str,
    message: str,
) -> Dict[str, Any]:
    service = get_notification_service()

    return await service.notify_scheme_update(
        recipient=recipient,
        scheme_id=scheme_id,
        message=message,
    )


async def notify_application_update(
    recipient: str,
    application_id: str,
    message: str,
) -> Dict[str, Any]:
    service = get_notification_service()

    return await service.notify_application_update(
        recipient=recipient,
        application_id=application_id,
        message=message,
    )