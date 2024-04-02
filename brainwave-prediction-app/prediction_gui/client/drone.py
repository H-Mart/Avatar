from djitellopy import Tello

tello = Tello()


def execute_drone_action(action: str):
    translation_distance = 30
    rotation_angle = 45

    translation_actions = {
        'backward': tello.move_back,
        'down': tello.move_down,
        'forward': tello.move_forward,
        'left': tello.move_left,
        'right': tello.move_right,
        'up': tello.move_up,
    }

    rotation_actions = {
        'turn_left': tello.rotate_counter_clockwise,
        'turn_right': tello.rotate_clockwise,
    }

    other_actions = {
        'connect': tello.connect,
        'land': tello.land,
        'takeoff': tello.takeoff,
        'flip': tello.flip_back,
        'keep alive': tello.query_battery,
    }

    if action in translation_actions:
        translation_actions[action](translation_distance)
    elif action in rotation_actions:
        rotation_actions[action](rotation_angle)
    elif action in other_actions:
        other_actions[action]()
    elif action == 'stream':
        tello.streamon()
        frame_read = tello.get_frame_read()
        while True:
            img = frame_read.frame
            cv2.imshow("drone", img)
    else:
        raise ValueError(f"Action {action} not recognized")
#
#
# def get_drone_action_testing(action):
#     if action == 'connect':
#         print("tello.connect()")
#     elif action == 'backward':
#         print('tello.move_back(30)')
#     elif action == 'down':
#         print('tello.move_down(30)')
#     elif action == 'forward':
#         print('tello.move_forward(30)')
#     elif action == 'land':
#         print('tello.land')
#     elif action == 'left':
#         print('tello.move_left(30)')
#     elif action == 'right':
#         print('tello.move_right(30)')
#     elif action == 'takeoff':
#         print('tello.takeoff')
#     elif action == 'up':
#         print('tello.move_up(30)')
#     elif action == 'turn_left':
#         print('tello.rotate_counter_clockwise(45)')
#     elif action == 'turn_right':
#         print('tello.rotate_clockwise(45)')
#     elif action == 'flip':
#         print("tello.flip('b')")
#     elif action == 'keep alive':
#         print("tello.query_battery()")
#     elif action == 'stream':
#         print("tello.streamon()")
#     return "Done"
