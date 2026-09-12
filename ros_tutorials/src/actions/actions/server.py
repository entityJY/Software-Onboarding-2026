# Assignment: Create a ROS 2 Action That Sleeps for a Given Amount of Time
# In this exercise, you will build a simple action-based node that receives a
# goal specifying how long to sleep. The server then sleeps for that duration,
# provides feedback while it is running, and returns a result when finished.
#
# The goal is to practice the action communication pattern used in ROS:
# a client sends a goal, the server processes it asynchronously, and the server
# periodically reports progress before returning the final result.
#
# The exercise introduces the basic ROS 2 action server pattern:
# - create a custom node class that inherits from rclpy.node.Node
# - initialize the node with a unique name, such as "sleep_action_server"
# - define a custom action type with goal, result, and feedback fields
# - create an action server with self.create_server(...)
# - implement a callback that sleeps for the requested duration and returns a result
# - publish feedback during execution and process the action until completion
#
# This file is the server half of the exercise. A matching client node sends a
# goal with a sleep duration and waits for the action to finish. Together, these
# nodes demonstrate how ROS 2 actions provide long-running request/response flow
# with progress updates.

import rclpy
from rclpy.action.server import ActionServer, ServerGoalHandle, GoalResponse
from rclpy.node import Node
from rclpy.duration import Duration

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


class SleepActionServer(Node):
    def __init__(self):
        super().__init__('action_server')

        # DONE: Create an action server for the SleepFor action type.
        # DONE: Use an execute_callback that handles the goal.
        # DONE: Publish feedback while sleeping.

        # create_server:
        #   Creates an action server that receives goals and manages execution.
        #   Usage: self.create_server(ActionType, 'action_name', execute_callback)
        #   - ActionType: the ROS action class you define in an .action file
        #   - 'action_name': unique name for the action, e.g. 'sleep_for'
        #   - execute_callback: function that handles the action goal
        #   Typical use: long-running tasks such as moving a robot, waiting, or processing work.
        ActionServer(
            self,
            SleepFor,
            'sleep_for',
            self.execute_callback,
        )
        
        self.get_logger().info("sleep_for action server loaded")

    # Create an action callback that sleeps for the requested duration.
    # The callback should read the goal, send feedback periodically, and return a result.
    def execute_callback(self, goal_handle: ServerGoalHandle) -> SleepFor.Result:
        # DONE: Read goal_handle.request.seconds
        total_time: float = goal_handle.request.seconds
        seconds = int(total_time)
        nanoseconds = int((total_time-seconds)*1e+9)
        # DONE: Sleep for the requested duration
        # DONE: Send feedback with remaining time
        feedback_msg = SleepFor.Feedback()
        res = SleepFor.Result(success=False)
        
        while seconds > 0 or nanoseconds > 0:
            if seconds > 0:
                success = self.get_clock().sleep_for(Duration(seconds=1))
                if not success:
                    goal_handle.abort()
                    return res
                seconds -= 1
                feedback_msg.remaining = float(seconds) + float(nanoseconds)/1e+9
                goal_handle.publish_feedback(feedback_msg)
            else:
                success = self.get_clock().sleep_for(Duration(nanoseconds=nanoseconds))
                if not success:
                    goal_handle.abort()
                    return res
                nanoseconds = 0
        # DONE: Set the result and return it
        goal_handle.succeed()
        res.success = True
        return res


def main():
    rclpy.init()
    node = SleepActionServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()