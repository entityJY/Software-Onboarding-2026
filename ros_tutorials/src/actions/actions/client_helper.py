from collections.abc import Callable
from typing import Protocol, Any
from functools import wraps

from rclpy.action.client import ClientGoalHandle
from rclpy.task import Future

class Feedback(Protocol):
    __slots__: list[str]
    _fields_and_field_types: dict[str, str]
    
    @classmethod
    def get_fields_and_field_types(cls) -> dict[str, str]: ...

def goal_feedback(func: Callable[[Any, Any], None]):
    @wraps(func)
    def wrapper(self, feedback_msg):
        feedback = feedback_msg.feedback
        func(self, feedback)
    return wrapper

def response_feedback(func: Callable[[Any, ClientGoalHandle], None]):
    @wraps(func)
    def wrapper(self, future: Future):
        goal_handle = future.result()
        assert isinstance(goal_handle, ClientGoalHandle)
        func(self, goal_handle)
    return wrapper

def result_feedback(func: Callable[[Any, Any], None]):
    @wraps(func)
    def wrapper(self, future: Future):
        res = future.result()
        assert res is not None
        result = res.result
        func(self, result)
    return wrapper
