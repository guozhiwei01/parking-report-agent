import json
import logging
from datetime import datetime, timezone
from typing import Any


logger = logging.getLogger("parking_report_agent")


def log_event(event: str, **fields: Any) -> None:
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **fields,
    }
    logger.info(json.dumps(payload, ensure_ascii=False, default=str))
