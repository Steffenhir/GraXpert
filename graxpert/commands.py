from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Dict

import numpy as np

from graxpert.app_state import INITIAL_STATE, AppState
from graxpert.background_selection import background_selection


class ICommandHandler(ABC):
    @abstractmethod
    def execute(self, app_state: AppState, cmd_args: Dict) -> AppState:
        pass

    @abstractmethod
    def undo(
        self, cur_state: AppState, prev_state: AppState, cmd_args: Dict
    ) -> AppState:
        pass

    @abstractmethod
    def redo(
        self, cur_state: AppState, next_state: AppState, cmd_args: Dict
    ) -> AppState:
        pass

    @abstractmethod
    def progress(self) -> float:
        pass


class Command:

    def __init__(
        self, handler: ICommandHandler, prev: Command = None, **kwargs
    ) -> None:
        self.prev: Command = prev
        self.next: Command = None
        self.handler: ICommandHandler = handler
        self.app_state: AppState = None
        self.cmd_args = kwargs

    def execute(self) -> AppState:
        if self.prev is None:
            app_state = INITIAL_STATE
        else:
            app_state = self.prev.app_state
        self.app_state = self.handler.execute(app_state, self.cmd_args)
        if self.prev is not None:
            self.prev.next = self
        return self.app_state

    def undo(self) -> Command:
        if self.prev is None:
            prev_state = INITIAL_STATE
            return self
        else:
            prev_state = self.prev.app_state
            self.prev.app_state = self.handler.undo(self.app_state, prev_state, self.cmd_args)
            return self.prev
        

    def redo(self) -> Command:
        assert self.next is not None
        next_state = self.next.app_state
        self.next.app_state = self.handler.redo(self.app_state, next_state, self.cmd_args)
        return self.next


class InitHandler(ICommandHandler):

    def execute(self, app_state: AppState, cmd_args: Dict) -> AppState:
        state = INITIAL_STATE
        state["background_points"] = cmd_args["background_points"]
        return state

    def undo(
        self, cur_state: AppState, prev_state: AppState, cmd_args: Dict
    ) -> AppState:
        state = INITIAL_STATE
        state["background_points"] = cmd_args["background_points"]
        return state

    def redo(
        self, cur_state: AppState, next_state: AppState, cmd_args: Dict
    ) -> AppState:
        return deepcopy(next_state)

    def progress(self) -> float:
        return 1.0

class PointHandler(ICommandHandler):
    def undo(
        self, cur_state: AppState, prev_state: AppState, cmd_args: Dict
    ) -> AppState:
        app_state_copy = deepcopy(cur_state)
        prev_background_points = deepcopy(prev_state["background_points"])
        app_state_copy["background_points"] = prev_background_points
        return app_state_copy

    def redo(
        self, cur_state: AppState, next_state: AppState, cmd_args: Dict
    ) -> AppState:
        app_state_copy = deepcopy(cur_state)
        next_background_points = deepcopy(next_state["background_points"])
        app_state_copy["background_points"] = next_background_points
        return app_state_copy


class AddPointHandler(PointHandler):
    def execute(self, app_state: AppState, cmd_args: Dict) -> AppState:
        app_state_copy = deepcopy(app_state)
        point = cmd_args["point"]
        app_state_copy["background_points"].append(point)
        return app_state_copy

    def progress(self) -> float:
        return 1.0


class RemovePointHandler(PointHandler):
    def execute(self, app_state: AppState, cmd_args: Dict) -> AppState:
        app_state_copy = deepcopy(app_state)
        idx = cmd_args["idx"]
        app_state_copy["background_points"].pop(idx)
        return app_state_copy

    def progress(self) -> float:
        return 1.0


class MovePointHandler(PointHandler):
    def execute(self, app_state: AppState, cmd_args: Dict) -> AppState:
        app_state_copy = deepcopy(app_state)
        idx = cmd_args["idx"]
        new_point = cmd_args["new_point"]
        
        if len(new_point) == 0:
            app_state_copy["background_points"].pop(idx)
        else:
            app_state_copy["background_points"][idx] = new_point
        
        return app_state_copy
        
    def progress(self) -> float:
        return 1.0
    
    
class SelectPointsHandler(PointHandler):
    def execute(self, app_state: AppState, cmd_args: Dict) -> AppState:
        app_state_copy = deepcopy(app_state)
        data = cmd_args["data"]
        num_pts = cmd_args["num_pts"]
        tol = cmd_args["tol"]
        automatic_points = background_selection(data, num_pts, tol)
        for i in range(len(automatic_points)):
            automatic_points[i] = np.array([automatic_points[i][1],automatic_points[i][0],1.0])
            
        """
        for a in automatic_points:
            match = False
            for e in app_state["background_points"]:
                if int(e[0]) == int(a[0]) and int(e[1]) == int(a[1]):
                    match = True
                    break
            if match:
                continue
            app_state_copy["background_points"].append(a)
        """
        
        app_state_copy["background_points"] = automatic_points
        return app_state_copy

    def progress(self) -> float:
        return 1.0

class ResetPointsHandler(PointHandler):
    def execute(self, app_state: AppState, cmd_args: Dict) -> AppState:
        app_state_copy = deepcopy(app_state)
        app_state_copy["background_points"].clear()
        return app_state_copy

    def progress(self) -> float:
        return 1.0


INIT_HANDLER = InitHandler()
ADD_POINT_HANDLER = AddPointHandler()
RM_POINT_HANDLER = RemovePointHandler()
MOVE_POINT_HANDLER = MovePointHandler()
SEL_POINTS_HANDLER = SelectPointsHandler()
RESET_POINTS_HANDLER = ResetPointsHandler()
