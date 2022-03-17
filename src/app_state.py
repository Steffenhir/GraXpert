from typing import TypedDict, List

class AppState(TypedDict):
    background_points: List

INITIAL_STATE: AppState = {
    "background_points": []
}