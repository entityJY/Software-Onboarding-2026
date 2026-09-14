from collections.abc import Callable
from typing import Any, TypeAlias
from functools import wraps

from rclpy.action.client import ClientGoalHandle
from rclpy.task import Future


Feedback: TypeAlias = Any
Result: TypeAlias = Any


def goal_feedback(func: Callable[[Any, Feedback], None]):
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

def result_feedback(func: Callable[[Any, Result], None]):
    @wraps(func)
    def wrapper(self, future: Future):
        res = future.result()
        assert res is not None
        result = res.result
        func(self, result)
    return wrapper
