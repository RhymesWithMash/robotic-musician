import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from robotic_musician import stdaudio
import math
import pygame
import time
import tkinter as tk
from tkinter import ttk
import threading


class Music(Node):
    # Initializes node, GUI, and pygame mixer.
    def __init__(self):
        super().__init__('music')
        self.sps = 44100
        self.now = time.time()
        self.then = time.time() - 1
        self.song_file = open("odear.txt", "r")
        self.text = "Select a Song!"

        self.subscriber = self.create_subscription(Int32, 'gesture_topic', self.play_music, 10)
        
        self.channel = pygame.mixer.Channel(0)
        self.current_sound = None

        self.get_logger().info("Music node initialized.")

        gui_thread = threading.Thread(target=self.setup_gui, daemon=True)
        gui_thread.start()

    # Configures the tkinter GUI
    def setup_gui(self):
        self.window = tk.Tk()
        self.window.title("Pick Your Song")
        self.window.geometry("400x300")
        self.window.configure(bg="#e6ecf0")

        # Configure modern style for buttons
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.TButton",
            font=("Helvetica", 12, "bold"),
            padding=12,
            background="#4CAF50", 
            foreground="white",
            borderwidth=0,
            relief="flat",
            anchor="center",
        )
        style.map(
            "Custom.TButton",
            background=[
                ("active", "#45a049"),  
                ("pressed", "#3d8b40"),  
            ],
            foreground=[("active", "white"), ("pressed", "white")],
            relief=[("pressed", "sunken"), ("!pressed", "flat")],
            shiftrelief=[("pressed", 2)],
        )

        # Frame for buttons
        frame = ttk.Frame(self.window, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Message label to display button outputs

        self.message_label = ttk.Label(
            frame,
            text= self.text,
            font=("Helvetica", 11),
            foreground="#333333",
            background="#e6ecf0",
            anchor="center",
            padding=10,
        )
        self.message_label.grid(row=3, column=1, pady=20, sticky="ew")

        # Buttons
        ttk.Button(
            frame,
            text="Odear",
            command=self.button1,
            style="Custom.TButton",
        ).grid(row=0, column=1, pady=15, sticky="ew")
        ttk.Button(
            frame,
            text="Saints",
            command=self.button2,
            style="Custom.TButton",
        ).grid(row=1, column=1, pady=15, sticky="ew")
        ttk.Button(
            frame,
            text="Beethoven",
            command=self.button3,
            style="Custom.TButton",
        ).grid(row=2, column=1, pady=15, sticky="ew")

        # Shadow effect for depth
        shadow = tk.Label(self.window, bg="#d3dce6", bd=0)
        shadow.place(relx=0.5, rely=0.5, anchor="center", width=320, height=240)
        frame.lift()

        self.window.mainloop()

    # Callback functions for tkinter GUI for switching songs
    def button1(self):
        self.song_file = open("odear.txt", "r")
        self.get_logger().info("O Dear Chosen")
        self.text = "O Dear Chosen"
    def button2(self):
        self.song_file = open("saints.txt", "r")
        self.get_logger().info("Saints chosen")
        self.text = "Saints Chosen"
    def button3(self):
        self.song_file = open("beethoven.txt", "r")
        self.get_logger().info("Beethoven chosen")
        self.text = "Beethoven Chosen"

    # Main function, run on callback from subscription.
    # Synthesizes music loading instructions from txt files.
    # Takes in a subscription message and parses it for a beat message.
    def play_music(self, beat):
        self.then = self.now
        self.now = time.time()
        duration_of_last_beat = self.now - self.then

        beat = int(beat.data)

        # Read the next beat from file
        line = self.song_file.readline()
        if line == "":
            self.get_logger().info("Song finished. Once again, from the top...")
            self.song_file.seek(0)
            line = self.song_file.readline()

        tones = line.split()
        duration = (1 / len(tones)) * duration_of_last_beat
        tones_hz = [440 * math.pow(2, int(n) / 12.0) for n in tones]

        N = int(self.sps * duration) # Find duration of tone in samples
        samples = []
        for i in range(len(tones_hz)):
            tone = tones_hz[i]
            if i == len(tones_hz) - 1: # if it's the last tone in a beat
                note_samples = [math.sin(2 * math.pi * j * tone / self.sps) for j in range(int(self.sps * 10))]
            else:
                note_samples = [math.sin(2 * math.pi * j * tone / self.sps) for j in range(N)]
            samples.extend(note_samples)

        N = int(self.sps * 10)
        
        last_note_samples = [math.sin(2 * math.pi * j * tones_hz[-1] / self.sps) for j in range(N)]
        samples.extend(last_note_samples)

        self.current_sound = stdaudio.make_sound(samples)
        self.channel.play(self.current_sound)

def main(args=None):
    rclpy.init(args=args)
    node = Music()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()
