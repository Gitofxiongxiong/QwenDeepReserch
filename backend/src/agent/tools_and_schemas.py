from typing import List
from pydantic import BaseModel, Field


class SearchQueryList(BaseModel):
    query: List[str] = Field(
        description="用于搜索的查询列表。"
    )
    rationale: str = Field(
        description="对查询列表的解释和原因。"
    )


class Reflection(BaseModel):
    is_sufficient: bool = Field(
        description="是否足够了解问题。"
    )
    knowledge_gap: str = Field(
        description="问题的知识差距。"
    )
    follow_up_queries: List[str] = Field(
        description="用于填补知识差距的后续查询列表。"
    )
