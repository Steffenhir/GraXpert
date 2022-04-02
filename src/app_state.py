from typing import TypedDict, List, AnyStr

class AppState(TypedDict):
    background_points: List
    working_dir: AnyStr

INITIAL_STATE: AppState = {
    "background_points": [],
    "working_dir": ""
}
