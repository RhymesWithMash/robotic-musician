# Robot Musician: TurtleBot4 Conductor

## Overview
This project uses a laptop's webcam to track a conductor's hand movements via a camera and translate them into musical performance. The system uses OpenCV and MediaPipe for gesture recognition and Pygame for audio synthesis.

## Dependencies
- ROS 2 Humble: [Installation Guide](https://docs.ros.org/en/humble/Installation.html)
- OpenCV: `pip install opencv-python`
- MediaPipe: `pip install mediapipe`
- Pygame: `pip install pygame`

## Installation
1. Install ROS 2 Humble.
2. Set up a ROS 2 workspace:
   ```bash
   mkdir -p ~/ros2_ws/src
   cd ~/ros2_ws/src
   ```
3. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/robot-musician.git
   ```
4. Build and source:
   ```bash
   cd ~/ros2_ws
   colcon build
   source install/setup.bash
   ```

## Running
1. Launch TurtleBot4:
   ```bash
   ros2 launch launch/launch.xml
   ```

## Known Issues
- Hand tracking may not be reliable in low-light conditions or with backgrounds similar to the hand.
- May have unknown system-specific issues.

## Music File Format
- The robot reads music from a .txt file where each line in the file represents a beat. Numbers on the lines represent notes to be played, where each additional number above 0 represents one semitone above A4. Multiple numbers on one line will be split into even subdivisions.