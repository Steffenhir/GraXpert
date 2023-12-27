from dataclasses import dataclass, field
from typing import List


@dataclass
class AppState:
    background_points: List = field(default_factory=list)


INITIAL_STATE = AppState()
