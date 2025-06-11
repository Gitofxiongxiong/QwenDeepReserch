import os
from pydantic import BaseModel, Field
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig


class Configuration(BaseModel):
    query_generator_model: str = Field(
        default="gemini-2.0-flash",
        metadata={
            "description": "用来生成搜索查询的模型"
        },
    )

    reflection_model: str = Field(
        metadata={
            "description": "用来反思的模型"
        },
    )

    answer_model: str = Field(
        metadata={
            "description": "用来回答的模型"
        },
    )

    number_of_initial_queries: int = Field(
        default=3,
        metadata={"description": "初始化时生成的查询数量"},
    )

    max_research_loops: int = Field(
        default=2,
        metadata={"description": "最大的反思循环次数"},
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """转换RunnableConfig到Configuration"""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
