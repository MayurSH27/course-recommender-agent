from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    messages: list[Any] = field(default_factory=list)
    tool_calls: list[dict] = field(default_factory=list)
    tool_results: list[dict] = field(default_factory=list)