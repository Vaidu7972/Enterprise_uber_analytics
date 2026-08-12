from typing import Literal, Optional

from pydantic import BaseModel, Field


class QuestionIntent(BaseModel):

    route: Literal[
        "general",
        "data_agent",
        "support_agent",
        "ml_agent",
        "multi_agent"
    ]

    intent: str

    entity: Optional[str] = None

    metric: Optional[str] = None

    operation: Optional[str] = None

    limit: Optional[int] = None

    time_period: Optional[str] = None

    location: Optional[str] = None

    identifier: Optional[str] = None

    routing_reason: str = Field(
        description="Short explanation of why this route was selected."
    )