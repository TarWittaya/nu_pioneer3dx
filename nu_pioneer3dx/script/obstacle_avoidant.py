import math
import rospy
import sys

from robot_position import RobotPosition
from vector_calculation import LinearVector


class ObstacleAvoidant:

    def __init__(self):

        self.obs_force_scale = 0.5  # The larger, the more distance from robot to obstacle
        self.global_percent = 0.1
        self.local_percent = 1 - self.global_percent

    def get_obstacle_vector(self, laser):

        obs_force_x = 0
        obs_force_y = 0

        for i in laser.laser_value:

            force_x = force_y = 0

            if laser.laser_value[i] <= 3:

                force_yaw = (i * math.pi / 180) + robot.robot_yaw + math.pi

                obs_magnitude = self.obs_force_scale / laser.laser_value[i]

                force_x = obs_magnitude * math.cos(force_yaw)
                force_y = obs_magnitude * math.sin(force_yaw)

            obs_force_x += force_x
            obs_force_y += force_y

        return obs_force_x, obs_force_y

    def compute(self, vector, laser, robot, goal):

        # goal_yaw is map_yaw
        goal_magnitude, goal_yaw = vector.get_vector(robot, goal)

        goal_magnitude_x = goal_magnitude * math.cos(goal_yaw)
        goal_magnitude_y = goal_magnitude * math.sin(goal_yaw)

        obs_magnitude_x, obs_magnitude_y = self.get_obstacle_vector(laser)

        obs_magnitude = math.sqrt(
            math.pow(obs_magnitude_x, 2) + math.pow(obs_magnitude_y, 2)) * self.local_percent

        summed_magnitude_x = (
            goal_magnitude_x * self.global_percent) + (obs_magnitude_x * self.local_percent)
        summed_magnitude_y = (
            goal_magnitude_y * self.global_percent) + (obs_magnitude_y * self.local_percent)

        summed_yaw = math.atan2(summed_magnitude_y, summed_magnitude_x)

        if summed_yaw < 0:
            summed_yaw += 2 * math.pi

        return obs_magnitude, goal_magnitude, summed_yaw


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Please specify the laser type (rplidar / hokuyo) and world type (gazebo / real).")
    else:

        laser_type = sys.argv[1]

        if sys.argv[2] == "gazebo":

            if sys.argv[1] == "rplidar":
                from get_rplidar_gazebo import SensorValue
            else:
                print("No type of this laser!!")
                exit()

        elif sys.argv[2] == "real":

            if sys.argv[1] == "laser":
                from get_rplidar import SensorValue
            else:
                print("No type of this laser!!")
                exit()

        else:
            print("Invalid World Type")
            exit()

        rospy.init_node("obstacle_avoidant")
        robot = RobotPosition()
        laser = SensorValue()
        vector = LinearVector()

        program = ObstacleAvoidant()

        while True:

            print("Enter your coordinate: ")
            goal_x = input("x: ")
            goal_y = input("y: ")

            goal = {"x": goal_x, "y": goal_y, "yaw": math.pi}

            finished = False

            while not finished:

                obs_magnitude, goal_magnitude, target_yaw = program.compute(
                    vector, laser, robot, goal)

                final_yaw = vector.get_move_radian(target_yaw, robot)

                finished = vector.order_robot(
                    obs_magnitude, goal_magnitude, final_yaw)

                rospy.sleep(0.1)
