from collections.abc import Callable
from typing import Any, TypeAlias, Protocol, ClassVar, Optional

from rclpy.action.client import ClientGoalHandle, ActionClient
from rclpy.task import Future
from rclpy.node import Node


Feedback: TypeAlias = Any
Result: TypeAlias = Any
Goal: TypeAlias = Any


class _RosAction(Protocol):
    Goal: ClassVar
    Feedback: ClassVar
    Result: ClassVar
    Impl: ClassVar


class ActionClientHelper():
    
    def __init__(
        self,
        node: Node,
        action_type: _RosAction,
        action_name: str
    ) -> None:
        self.client = ActionClient(node, action_type, action_name)
        self._node = node
        
        self._goal_type = action_type.Goal
        
    def send_goal(self,
        goal: Goal,
        response_feedback_callback: Optional[Callable[[ClientGoalHandle], None]] = None,
        goal_feedback_callback: Optional[Callable[[Feedback], None]] = None,
        result_feedback_callback: Optional[Callable[[Result], None]] = None
    ) -> None:
        if not isinstance(goal, self._goal_type):
            self._node.get_logger().error(f"Sent goal type does not match expected goal type! Expected {self._goal_type} but got {type(goal)}")
            return
        self.client.wait_for_server()
        future = self.client.send_goal_async(goal, lambda msg: self._goal_feedback(msg, goal_feedback_callback))
        future.add_done_callback(lambda future: self._response_feedback(future, response_feedback_callback, result_feedback_callback))
    
    def _response_feedback(self,
        future: Future,
        response_callback: Optional[Callable[[ClientGoalHandle], None]],
        result_callback: Optional[Callable[[Result], None]] = None
    ) -> None:
        goal_handle = future.result()
        
        if goal_handle is None:
            self._node.get_logger().error("Future returned from sending goal is None!")
            return
        assert isinstance(goal_handle, ClientGoalHandle)
        
        if response_callback is not None:
            response_callback(goal_handle)
        
        result: Future = goal_handle.get_result_async()
        result.add_done_callback(lambda future: self._result_feedback(future, result_callback))
    
    def _goal_feedback(self, feedback_msg, goal_callback: Optional[Callable[[Feedback], None]]) -> None:
        feedback = feedback_msg.feedback
        if goal_callback is not None:
            goal_callback(feedback)
    
    def _result_feedback(self, future: Future, result_feedback: Optional[Callable[[Result], None]] = None) -> None:
        res = future.result()
        
        if res is None:
            self._node.get_logger().error("Future returned from getting result is None!")
            return
        assert res is not None
        
        result = res.result
        
        if result_feedback is not None:
            result_feedback(result)
