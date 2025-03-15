import sys
import os
import threading
import time
import random
import speech_recognition as sr
from openai import OpenAI
from gtts import gTTS
import pygame
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QMovie, QPixmap, QImage, QFont

# Suppress macOS secure coding warning
os.environ['QT_MAC_WANTS_LAYER'] = '1'

# Set your OpenAI API key here
client = OpenAI(api_key="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")

# Ambient music file (ensure the file exists and is in .wav format)
AMBIENT_MUSIC = "ambient_music.wav"

# List of comforting sentences to say while waiting for the OpenAI response
COMFORTING_SENTENCES = [
    "I'm here to comfort you.",
    "Please give me a moment to think.",
    "You're not alone; I'm here for you.",
    "Let me find the best way to help you.",
    "Take a deep breath; I'm processing your request.",
    "I'm listening carefully to what you're saying.",
    "Your feelings are important to me.",
    "I'm here to support you through this.",
    "Let me think of the best response for you.",
    "I'm here to help you feel better.",
    "You're doing great; let me think for a moment.",
    "I'm here to make things easier for you.",
    "I'm processing your thoughts; please hold on.",
    "I'm here to provide you with the best support.",
    "Let me find the right words for you.",
    "I'm here to help you through this moment.",
    "I'm thinking of the best way to respond.",
    "Your well-being is my priority.",
    "I'm here to help you feel understood.",
    "Let me take a moment to understand your feelings."
]

# Webcam feed thread
class WebcamThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)  # Signal to update the webcam feed

    def run(self):
        cap = cv2.VideoCapture(0)  # Open the default webcam
        while True:
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.change_pixmap_signal.emit(convert_to_qt_format)  # Emit the frame
            time.sleep(0.03)  # Add a small delay to reduce CPU usage

class Worker(QObject):
    response_signal = pyqtSignal(str)  # Signal to emit chatbot response

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = True  # Always listening

    def listen_and_respond(self):
        while self.is_listening:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)

            try:
                user_input = self.recognizer.recognize_google(audio)
                self.process_response(user_input)
            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
            except sr.RequestError:
                print("Speech recognition service failed.")

    def process_response(self, user_input):
        # Say a random comforting sentence while waiting for the OpenAI response
        comforting_sentence = random.choice(COMFORTING_SENTENCES)
        self.play_response(comforting_sentence)

        # Start streaming the OpenAI response
        response_stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a mental health assistant. Provide supportive and empathetic responses. Be concise!"},
                {"role": "user", "content": user_input}
            ],
            stream=True  # Enable streaming
        )

        # Collect the full response
        full_response = ""
        for chunk in response_stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content

        # Convert the full response to speech and play it
        self.play_response(full_response)

    def play_response(self, text):
        # Use gTTS to generate audio
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")

        # Play the audio using pygame
        pygame.mixer.music.load("response.mp3")
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

class VoiceChatbotApp(QMainWindow):
    def __init__(self, stacked_widget, main_app):
        super().__init__()
        self.stacked_widget = stacked_widget  # Store the stacked widget
        self.main_app = main_app  # Store the main application reference
        self.init_ui()
        self.ambient_music_playing = False
        self.init_audio()

        # Worker thread for listening and responding
        self.worker = Worker()
        self.worker_thread = threading.Thread(target=self.worker.listen_and_respond, daemon=True)

        # Start listening automatically
        self.worker_thread.start()

        # Webcam thread
        self.webcam_thread = WebcamThread()
        self.webcam_thread.change_pixmap_signal.connect(self.update_webcam_feed)
        self.webcam_thread.start()

    def init_ui(self):
        self.setWindowTitle("Mental Health Chatbot")
        self.setGeometry(100, 100, 1000, 700)  # Adjusted window size
        self.setStyleSheet("""
            background-color: #1e1e2f;
            color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title label
        title_label = QLabel("AI Mental Health Companion")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #ffffff;
            padding: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Robot GIF
        self.robot_label = QLabel(self)
        self.robot_movie = QMovie("robot.gif")  # Ensure "robot.gif" is in the same directory
        self.robot_label.setMovie(self.robot_movie)
        self.robot_movie.start()
        self.robot_label.setFixedSize(350, 350)  # Reduced size
        self.robot_label.setAlignment(Qt.AlignCenter)
        self.robot_label.setStyleSheet("""
            border: 2px solid #444;
            border-radius: 150px;
            background-color: #2c2c3e;
        """)
        main_layout.addWidget(self.robot_label, alignment=Qt.AlignCenter)

        # Webcam feed
        self.webcam_label = QLabel(self)
        self.webcam_label.setFixedSize(350, 350)  # Reduced size
        self.webcam_label.setStyleSheet("""
            border: 2px solid #444;
            border-radius: 15px;
            background-color: #2c2c3e;
        """)
        self.webcam_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.webcam_label, alignment=Qt.AlignCenter)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # Ambient music button
        self.music_button = QPushButton("🎵 Play Ambient Music")
        self.music_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.music_button.clicked.connect(self.toggle_ambient_music)
        button_layout.addWidget(self.music_button)

        # Back button
        self.back_button = QPushButton("🏠 Back to Home")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.back_button.clicked.connect(self.go_back)
        button_layout.addWidget(self.back_button)

        main_layout.addLayout(button_layout)

        # Set layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def init_audio(self):
        pygame.mixer.init()
        if os.path.exists(AMBIENT_MUSIC):
            pygame.mixer.music.load(AMBIENT_MUSIC)
        else:
            print("Warning: Ambient music file not found!")

    def toggle_ambient_music(self):
        if self.ambient_music_playing:
            pygame.mixer.music.pause()
            self.music_button.setText("🎵 Play Ambient Music")
            self.ambient_music_playing = False
        else:
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.music_button.setText("⏸️ Pause Ambient Music")
            self.ambient_music_playing = True

    def update_webcam_feed(self, image):
        """Update the webcam feed with the latest frame."""
        self.webcam_label.setPixmap(QPixmap.fromImage(image).scaled(
            self.webcam_label.width(), self.webcam_label.height(), Qt.KeepAspectRatio
        ))

    def go_back(self):
        """Navigate back to the homepage."""
        self.stacked_widget.setCurrentWidget(self.main_app.home_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceChatbotApp(None, None)
    window.show()
    sys.exit(app.exec_())