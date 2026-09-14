from collections.abc import Callable
from typing import Any, TypeAlias, Protocol, ClassVar

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
        action_name: str,
        response_feedback: Callable[[ClientGoalHandle], None],
        goal_feedback: Callable[[Feedback], None],
        result_feedback: Callable[[Result], None]
    ) -> None:
        self._client = ActionClient(node, action_type, action_name)
        self._node = node
        self._response_feedback = response_feedback
        self._goal_feedback = goal_feedback
        self._result_feedback = result_feedback
        
        self._goal_type = action_type.Goal
        
    def send_goal(self, goal: Goal):
        if not isinstance(goal, self._goal_type):
            self._node.get_logger().error(f"Sent goal type does not match expected goal type! Expected {self._goal_type} but got {type(goal)}")
            return
        self._client.wait_for_server()
        future = self._client.send_goal_async(goal, self._goal_feedback_helper)
        future.add_done_callback(self._response_feedback_helper)
    
    def _response_feedback_helper(self, future: Future):
        goal_handle = future.result()
        
        if goal_handle is None:
            self._node.get_logger().error("Future returned from sending goal is None!")
            return
        assert isinstance(goal_handle, ClientGoalHandle)
        
        self._response_feedback(goal_handle)
        
        result: Future = goal_handle.get_result_async()
        result.add_done_callback(self._result_feedback_helper)
    
    def _goal_feedback_helper(self, feedback_msg):
        feedback = feedback_msg.feedback
        self._goal_feedback(feedback)
    
    def _result_feedback_helper(self, future: Future):
        res = future.result()
        
        if res is None:
            self._node.get_logger().error("Future returned from getting result is None!")
            return
        assert res is not None
        
        result = res.result
        self._result_feedback(result)
