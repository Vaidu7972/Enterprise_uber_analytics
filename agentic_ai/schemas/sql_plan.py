from typing import Optional
from pydantic import BaseModel, Field


class SQLPlan(BaseModel):
    can_answer: bool = Field(
        default=True,
        description="Whether the question can be answered using the available Gold schema."
    )

    sql: Optional[str] = Field(
        default=None,
        description="A single read-only PostgreSQL query."
    )

    tables_used: list[str] = Field(
        default_factory=list,
        description="Gold tables required by the query."
    )

    explanation: str = Field(
        default="Querying Gold warehouse data.",
        description="Short explanation of the SQL plan."
    )

    reasoning: Optional[str] = Field(
        default=None,
        description="Reasoning for the SQL plan."
    )