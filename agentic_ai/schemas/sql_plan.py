from typing import Optional

from pydantic import BaseModel, Field


class SQLPlan(BaseModel):

    can_answer: bool = Field(
        description=(
            "Whether the question can be answered "
            "using the available Gold schema."
        )
    )

    sql: Optional[str] = Field(
        default=None,
        description=(
            "A single read-only PostgreSQL query."
        )
    )

    tables_used: list[str] = Field(
        default_factory=list,
        description=(
            "Gold tables required by the query."
        )
    )

    explanation: str = Field(
        description=(
            "Short explanation of the SQL plan."
        )
    )