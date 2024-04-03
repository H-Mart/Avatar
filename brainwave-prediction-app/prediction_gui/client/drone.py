from djitellopy import Tello
import cv2


class Drone:
    def __init__(self, testing=False):
        if testing:
            self.tello = None
        else:
            self.tello = Tello()

    def send_action(self, action: str):
        if self.tello is None:
            return self._get_drone_action_testing(action)
        else:
            return self._execute_drone_action(action)

    def _execute_drone_action(self, action: str):
        translation_distance = 30
        rotation_angle = 45

        translation_actions = {
            'backward': self.tello.move_back,
            'down': self.tello.move_down,
            'forward': self.tello.move_forward,
            'left': self.tello.move_left,
            'right': self.tello.move_right,
            'up': self.tello.move_up,
        }

        rotation_actions = {
            'turn_left': self.tello.rotate_counter_clockwise,
            'turn_right': self.tello.rotate_clockwise,
        }

        other_actions = {
            'connect': self.tello.connect,
            'land': self.tello.land,
            'takeoff': self.tello.takeoff,
            'flip': self.tello.flip_back,
            'keep alive': self.tello.query_battery,
        }

        if action in translation_actions:
            translation_actions[action](translation_distance)
        elif action in rotation_actions:
            rotation_actions[action](rotation_angle)
        elif action in other_actions:
            other_actions[action]()
        elif action == 'stream':
            self.tello.streamon()
            frame_read = self.tello.get_frame_read()
            while True:
                img = frame_read.frame
                cv2.imshow("drone", img)
        else:
            raise ValueError(f"Action {action} not recognized")

    def _get_drone_action_testing(self, action):
        if action == 'connect':
            print("self.tello.connect()")
        elif action == 'backward':
            print('self.tello.move_back(30)')
        elif action == 'down':
            print('self.tello.move_down(30)')
        elif action == 'forward':
            print('self.tello.move_forward(30)')
        elif action == 'land':
            print('self.tello.land')
        elif action == 'left':
            print('self.tello.move_left(30)')
        elif action == 'right':
            print('self.tello.move_right(30)')
        elif action == 'takeoff':
            print('self.tello.takeoff')
        elif action == 'up':
            print('self.tello.move_up(30)')
        elif action == 'turn_left':
            print('self.tello.rotate_counter_clockwise(45)')
        elif action == 'turn_right':
            print('self.tello.rotate_clockwise(45)')
        elif action == 'flip':
            print("self.tello.flip('b')")
        elif action == 'keep alive':
            print("self.tello.query_battery()")
        elif action == 'stream':
            print("self.tello.streamon()")
        return "Done"
