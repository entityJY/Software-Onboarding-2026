# Assignment: Create a ROS 2 Action That Sleeps for a Given Amount of Time
# In this exercise, you will build a client node that sends a goal to the sleep
# action server. The client requests a duration to wait, then receives periodic
# feedback while the server is sleeping and a final result once the task is done.
#
# The exercise introduces the basic ROS 2 action client pattern:
# - create a custom node class that inherits from rclpy.node.Node
# - initialize the node with a unique name, such as "sleep_action_client"
# - create an action client with self.create_client(...)
# - send a goal containing the requested duration
# - wait for feedback and the final result
# - log the result and status updates
#
# This file is the client half of the exercise. It sends a goal to the action
# server and processes the returned feedback/result. Together, these two nodes
# demonstrate how ROS 2 actions support long-running tasks with progress updates.

import rclpy
from rclpy.node import Node
from rclpy.action.client import ActionClient, ClientGoalHandle
from rclpy.task import Future

# Action design:
#   Goal: seconds (float64)
#   Result: success (bool)
#   Feedback: remaining (float64)
# 
# Here, import SleepFor from the interfaces.action module
# SleepFor is the custom action type.
from interfaces.action import SleepFor

# ROS 2 boilerplate pattern:
# 1. Import rclpy and the base Node class.
# 2. Create a custom node class that inherits from Node.
# 3. In __init__, call super().__init__("node_name") to register the node.
# 4. Add action servers, publishers, subscribers, timers, and other ROS interfaces in __init__.
# 5. In main(), initialize rclpy, create the node, then spin it.
#    Finally destroy the node and shutdown ROS.
#
# This pattern is the standard starting point for most ROS 2 Python nodes.


class SleepActionClient(Node):
    def __init__(self):
        super().__init__('action_client')

        # DONE: Create an action client for the SleepFor action type.
        # DONE: Wait until the action server is available.
        # DONE: Construct a goal with a duration value.

        # create_client:
        #   Creates an action client used to send goals to a ROS action server.
        #   Usage: self.create_client(ActionType, 'action_name')
        #   - ActionType: the ROS action class you defined in an .action file
        #   - 'action_name': name of the action server to call
        #   Typical use: request a long-running task such as movement or timed work.
        self._client = ActionClient(
            self,
            SleepFor,
            'sleep_for',
        )
        
        # self.get_logger():
        #   Returns the node's ROS logger, used to print progress and results.
        self.get_logger().info("Sending goal")
        self.send_goal()

    # Create a method that sends the action goal.
    def send_goal(self):
        # DONE: Build a goal request with a sleep duration.
        goal_req = SleepFor.Goal()
        goal_req.seconds = 5.5
        # DONE: Send the goal to the action server.
        self._client.wait_for_server()
        future = self._client.send_goal_async(goal_req, self.goal_feedback)
        future.add_done_callback(self.response_feedback)
        # DONE: Handle feedback and wait for the final result.
    
    def goal_feedback(self, feedback_msg):
        feedback: SleepFor.Feedback = feedback_msg.feedback
        self.get_logger().info(f"Seconds remaining in sleep: {feedback.remaining}")
    
    def response_feedback(self, future: Future):
        goal_handle = future.result()
        assert isinstance(goal_handle, ClientGoalHandle)
        
        if not goal_handle.accepted:
            self.get_logger().info("Goal rejected")
            return
        self.get_logger().info("Goal accepted")
        
        result: Future = goal_handle.get_result_async()
        result.add_done_callback(self.result_feedback)
    
    def result_feedback(self, future: Future):
        res = future.result()
        assert res is not None
        result: SleepFor.Result = res.result
        
        if result.success:
            self.get_logger().info("Goal completed")
            return
        self.get_logger().info("Goal failed")


def main():
    rclpy.init()
    node = SleepActionClient()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()