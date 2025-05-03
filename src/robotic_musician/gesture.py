import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
import cv2
import mediapipe as mp
import time

class Gesture(Node):
    def __init__(self):
        super().__init__('gesture')

        self.publisher_ = self.create_publisher(Int32, 'gesture_topic', 10)

        self.cap = cv2.VideoCapture(0)

        self.beat_state = 3
        self.x_norm = 0.0
        self.y_norm = 0.0
        self.y_history = []
        self.x_history = []
        self.y_velocity_history = []
        self.x_velocity_history = []
        self.last_y_delta = 0.0
        self.last_x_delta = 0.0
        self.current_beat = 4

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7)
        self.mp_drawing = mp.solutions.drawing_utils

        # debouncing
        self.last_beat_time = 0
        self.beat_cooldown = 0.33 # seconds between accepted beats
        self.get_logger().info("Gesture node initialized.")
        
        self.timer = self.create_timer(0.015, self.process_frame)  # 60 FPS
        
    # Main function for processing openCV frames.
    # Recognizes gesures and publishes integers 1-4 to the \gesture_topic publisher
    # in time with the conductor's gestures.
    def process_frame(self):
        ret, frame = self.cap.read()

        frame = cv2.flip(frame, 1)  # mirror the cam
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame) # process the frame

        if results.multi_hand_landmarks and results.multi_handedness: 
            for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_label = hand_handedness.classification[0].label  # determines which hand is in frame

                if hand_label != 'Right':
                    continue  # skip if it's not the right hand

                index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # normalized coordinates (0–1)
                self.x_norm = index_tip.x
                self.y_norm = index_tip.y

                # smooth y with moving average
                self.y_history.append(self.y_norm)
                if len(self.y_history) > 3:
                    self.y_history.pop(0)
                smoothed_y = sum(self.y_history) / len(self.y_history)
                # same for x
                self.x_history.append(self.x_norm)
                if len(self.x_history) > 3:
                    self.x_history.pop(0)
                smoothed_x = sum(self.x_history) / len(self.x_history)

                # calculate x and y velocity
                last_smoothed_y = getattr(self, "last_smoothed_y", smoothed_y)
                last_smoothed_x = getattr(self, "last_smoothed_x", smoothed_x)
                y_delta = smoothed_y - last_smoothed_y
                x_delta = smoothed_x - last_smoothed_x

                # append latest velocity
                self.x_velocity_history.append(x_delta)
                self.y_velocity_history.append(y_delta)
                if len(self.x_velocity_history) > 3:
                    self.x_velocity_history.pop(0)
                if len(self.y_velocity_history) > 3:
                    self.y_velocity_history.pop(0)

                # compute smoothed deltas
                smoothed_x_delta = sum(self.x_velocity_history) / len(self.x_velocity_history)
                smoothed_y_delta = sum(self.y_velocity_history) / len(self.y_velocity_history)

                delta_deadzone = 0.02

                y_sign_changed_U = (y_delta > -delta_deadzone and smoothed_y_delta < -delta_deadzone)
                y_sign_changed_D = (y_delta < delta_deadzone and smoothed_y_delta > delta_deadzone) # if the smoothed y velocity has gone from positive to negative or negative to positive
                x_sign_changed_L = (x_delta > -delta_deadzone and smoothed_x_delta < -delta_deadzone)
                x_sign_changed_R = (x_delta < delta_deadzone and smoothed_x_delta > delta_deadzone) # if the smoothed x velocity has gone from positive to negative or negative to positive

                now = time.time()
                if not (now - self.last_beat_time) < self.beat_cooldown:
                    # Beat detection logic
                    beat_type = None
                    if y_sign_changed_D:
                        if self.beat_state == 3:
                            self.beat_state = 0  # from up to down
                            beat_type = 1
                    elif x_sign_changed_L:
                        if self.beat_state == 0:
                            self.beat_state = 1  # from down to left
                            beat_type = 2
                    elif x_sign_changed_R:
                        if self.beat_state == 1:
                            self.beat_state = 2  # from left to right
                            beat_type = 3
                    elif y_sign_changed_U:
                        if self.beat_state == 2:
                            self.beat_state = 3  # from right to up
                            beat_type = 4
                    else:
                        beat_type = None  # no valid transition

                    if beat_type: # if transition detected
                        self.get_logger().info(f"Beat {beat_type}")
                        cv2.putText(frame, str(beat_type), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3, cv2.LINE_AA)
                        msg = Int32()
                        msg.data = beat_type
                        self.publisher_.publish(msg)
                        self.last_beat_time = now
                        self.current_beat = beat_type

                # update "last" values
                self.last_y_delta = smoothed_y_delta
                self.last_smoothed_y = smoothed_y
                self.last_x_delta = smoothed_x_delta
                self.last_smoothed_x = smoothed_x

                # convert to pixel coordinates (just for drawing)
                h, w, _ = frame.shape
                x_pixel = int(self.x_norm * w)
                y_pixel = int(self.y_norm * h)
                x_smooth_pixel = int(smoothed_x * w)
                y_smooth_pixel = int(smoothed_y * h)

                if len(self.x_history) >= 2: # draw a history line
                    for i in range(1, len(self.x_history)):
                        x1 = int(self.x_history[i - 1] * w)
                        y1 = int(self.y_history[i - 1] * h)
                        x2 = int(self.x_history[i] * w)
                        y2 = int(self.y_history[i] * h)
                        cv2.line(frame, (x1, y1), (x2, y2), (0, 180, 255), 2)
                cv2.putText(frame, str(self.current_beat), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3, cv2.LINE_AA)

                if self.current_beat == 1:
                    start_point = (100, 125) # leftward arrow
                    end_point = (50, 125)
                    red = 255
                    green = 0
                    blue = 0
                elif self.current_beat == 2:
                    start_point = (50, 125) # rightward arrow
                    end_point = (100, 125) 
                    red = 0
                    green = 255
                    blue = 0
                elif self.current_beat == 3:
                    start_point = (75, 150) # upward arrow
                    end_point = (75, 100)
                    red = 0
                    green = 0
                    blue = 255
                elif self.current_beat == 4:
                    start_point = (75, 100) # downward arrow
                    end_point = (75, 150)
                    red = 255
                    green = 244
                    blue = 79
                cv2.arrowedLine(frame, start_point, end_point, (red, green, blue), 5, tipLength=0.3)

                cv2.putText(frame, str(self.current_beat), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (red, green, blue), 3, cv2.LINE_AA)


                # draw a dot at the tip of the index finger
                cv2.circle(frame, (x_pixel, y_pixel), 10, (0, 255, 0), -1)
                # draw dot for smoothed data
                cv2.circle(frame, (x_smooth_pixel, y_smooth_pixel), 10, (0, 0, 255), -1)

        cv2.imshow('Gesture Detection', frame)  # open window
        cv2.waitKey(1)  # ensures GUI updates correctly (was having issues before)

    
def main(args = None):
    rclpy.init(args = args)
    node = Gesture() 
    try:
        rclpy.spin(node) # create and spin up node
    except KeyboardInterrupt:
        pass
    finally:
        node.cap.release() # after node finishes, release the camera (so other applications can use it)
        cv2.destroyAllWindows() # clean up any opencv windows
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown() # clean up node and shutdown

if __name__ == '__main__':
    main()