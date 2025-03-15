import sys
import sqlite3
import requests
import random
from openai import OpenAI
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout, QSpacerItem, QSizePolicy, QHBoxLayout, QMessageBox,
    QToolButton, QMenu, QAction, QDialog
)
from PyQt5.QtGui import QFont, QPixmap, QDesktopServices
from PyQt5.QtCore import Qt, QUrl
import regex as re

# OpenAI API Key (Replace with your actual API key)
client = OpenAI(api_key="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")

def extract_url(text):
    """
    Extracts the first URL from the given text using regex.
    """
    # Regex pattern to match URLs
    url_pattern = r'https?://[^\s]+'
    match = re.search(url_pattern, text)
    if match:
        return match.group(0)  # Return the first matched URL
    return None  # Return None if no URL is found

# Function to Fetch Mental Health Quotes from ZenQuotes API
def get_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=5)
        response.raise_for_status()
        quote_data = response.json()
        return quote_data[0]['q']  # Extracting the quote text
    except requests.RequestException as e:
        print(f"Error fetching quote: {e}")
        return "Take time to do what makes your soul happy."  # Default quote if API fails

# Function to Get a YouTube Video Recommendation Using OpenAI
def get_youtube_video():
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Use GPT-4 for better recommendations
            messages=[
                {"role": "system", "content": "You are a helpful assistant that recommends mental health-related YouTube videos."},
                {"role": "user", "content": "Recommend a YouTube video link for improving mental health and provide a brief description Max 20 word output!!"}
            ]
        )
        recommendation = response.choices[0].message.content.strip()
        return recommendation
    except Exception as e:
        print(f"Error fetching YouTube recommendation: {e}")
        return "https://www.youtube.com/watch?v=1qJ2C1QEl_Y"  # Fallback video link

# Function to Get a Spotify Song Recommendation Using OpenAI
def get_spotify_song():
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Use GPT-4 for better recommendations
            messages=[
                {"role": "system", "content": "You are a helpful assistant that recommends mental health-related Spotify songs."},
                {"role": "user", "content": "Recommend a Spotify song link for relaxation and mental well-being and provide a brief description. Max 20 word output!!!"}
            ]
        )
        recommendation = response.choices[0].message.content.strip()
        return recommendation
    except Exception as e:
        print(f"Error fetching Spotify recommendation: {e}")
        return "https://open.spotify.com/track/5XGf7i7gYkVBQ5eqhHtYjv"  # Fallback song link

# Profile Dialog to Display User Information
class ProfileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Profile")
        self.setGeometry(300, 100, 400, 400)
        self.setStyleSheet("""
            background-color: #fce4ec;  /* Light pink background */
            color: #880e4f;  /* Dark pink text */
        """)

        layout = QVBoxLayout()

        # Display Dummy User Information
        self.name_label = QLabel("Name: Vedanth")
        self.name_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(self.name_label)

        self.milestone_label = QLabel("Mental Health Milestone: 30 Days Streak! 🎉")
        self.milestone_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.milestone_label)

        self.hobbies_label = QLabel("Hobbies: Reading, Hiking, Painting")
        self.hobbies_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.hobbies_label)

        self.stressors_label = QLabel("Stressors: Work Deadlines, Financial Worries")
        self.stressors_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.stressors_label)

        self.relaxors_label = QLabel("Relaxors: Meditation, Listening to Music, Yoga")
        self.relaxors_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.relaxors_label)

        self.days_label = QLabel("Days on App: 45 Days")
        self.days_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.days_label)

        # Close Button
        close_button = QPushButton("Close")
        close_button.setFont(QFont("Arial", 14))
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #e91e63;  /* Pink button */
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c2185b;  /* Darker pink on hover */
            }
        """)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

class UserHomePage(QWidget):
    def __init__(self, username, stacked_widget, main_app):
        super().__init__()
        self.setWindowTitle("Serenity - Home")
        self.setGeometry(300, 100, 800, 600)
        self.setStyleSheet("""
            background-color: #fce4ec;  /* Light pink background */
            color: #880e4f;  /* Dark pink text */
        """)
        self.stacked_widget = stacked_widget
        self.main_app = main_app  # Reference to the main application
        self.username = username

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Top Bar Layout (for welcome label, profile button, and hamburger menu)
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setAlignment(Qt.AlignLeft)  # Align items to the left

        # Welcome Label
        welcome_label = QLabel(f"Welcome, {self.username}!")
        welcome_label.setFont(QFont("Arial", 24, QFont.Bold))
        welcome_label.setStyleSheet("color: #880e4f;")  # Dark pink text
        top_bar_layout.addWidget(welcome_label)

        # Add a spacer to push the profile button and hamburger menu to the right
        top_bar_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Profile Button
        self.profile_button = QPushButton("Profile")
        self.profile_button.setFont(QFont("Arial", 14))
        self.profile_button.setStyleSheet("""
            QPushButton {
                background-color: #e91e63;  /* Pink button */
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c2185b;  /* Darker pink on hover */
            }
        """)
        self.profile_button.clicked.connect(self.show_profile)
        top_bar_layout.addWidget(self.profile_button)

        # Hamburger Menu
        self.hamburger_menu = QToolButton()
        self.hamburger_menu.setText("☰")  # Hamburger icon
        self.hamburger_menu.setFont(QFont("Arial", 20))
        self.hamburger_menu.setStyleSheet("""
            QToolButton {
                background-color: #e91e63;  /* Pink button */
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 20px;
            }
            QToolButton:hover {
                background-color: #c2185b;  /* Darker pink on hover */
            }
        """)
        self.hamburger_menu.setPopupMode(QToolButton.InstantPopup)

        # Create a menu for the hamburger button
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;  /* White background */
                color: #880e4f;  /* Dark pink text */
                padding: 10px;
                border-radius: 5px;
            }
            QMenu::item {
                padding: 10px;
            }
            QMenu::item:selected {
                background-color: #fce4ec;  /* Light pink on selection */
            }
        """)

        # Add actions to the menu
        actions = [
            ("SoulSync 🌅", self.main_app.show_reflection_page),
            ("MindMate 🧠", self.main_app.show_chatbot_page),
            ("MoodMap 📊", self.main_app.show_mood_tracker_page),
            ("Guiding Light 🤝", self.main_app.show_counsellor_page),
            ("SafeCircle 🤗", self.main_app.show_chat_page),
            ("NeuroCare 🤖", self.main_app.show_chat_page2),
        ]
        for text, callback in actions:
            action = QAction(text, self)
            action.triggered.connect(callback)
            menu.addAction(action)

        self.hamburger_menu.setMenu(menu)
        top_bar_layout.addWidget(self.hamburger_menu)

        # Add top bar layout to main layout
        main_layout.addLayout(top_bar_layout)

        # Header Image
        header_label = QLabel(self)
        header_pixmap = QPixmap("header.png")  # Load the image
        if not header_pixmap.isNull():
            # Scale the image to fit the width of the window and increase height
            header_label.setPixmap(header_pixmap.scaled(self.width(), 300, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            header_label.setAlignment(Qt.AlignCenter)
            header_label.setStyleSheet("margin: 0; padding: 0;")  # Remove any default margins or padding
            main_layout.addWidget(header_label)

        # Quote Section with New Quote Button
        quote_layout = QHBoxLayout()
        self.quote_label = QLabel(get_quote())
        self.quote_label.setFont(QFont("Arial", 16))
        self.quote_label.setWordWrap(True)
        self.quote_label.setStyleSheet("""
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            color: #880e4f;  /* Dark pink text */
            font-style: italic;
        """)
        quote_layout.addWidget(self.quote_label)

        self.new_quote_btn = QPushButton("New Quote")
        self.new_quote_btn.setFont(QFont("Arial", 14))
        self.new_quote_btn.setStyleSheet("""
            QPushButton {
                background-color: #e91e63;  /* Pink button */
                color: white;
                padding: 15px;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c2185b;  /* Darker pink on hover */
            }
        """)
        self.new_quote_btn.clicked.connect(self.update_quote)
        quote_layout.addWidget(self.new_quote_btn)
        main_layout.addLayout(quote_layout)

        # YouTube Video Recommendation Section
        youtube_layout = QHBoxLayout()
        self.youtube_recommendation = QLabel("Loading recommendation...")
        self.youtube_recommendation.setFont(QFont("Arial", 14))
        self.youtube_recommendation.setWordWrap(True)
        self.youtube_recommendation.setStyleSheet("""
            background-color: #ffffff;
            padding: 15px;
            border-radius: 10px;
            color: #880e4f;  /* Dark pink text */
        """)
        youtube_layout.addWidget(self.youtube_recommendation, 4)

        self.youtube_button = QPushButton("Watch Video")
        self.youtube_button.setFont(QFont("Arial", 14))
        self.youtube_button.setStyleSheet("""
            QPushButton {
                background-color: #e91e63;  /* Pink button */
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c2185b;  /* Darker pink on hover */
            }
        """)
        self.youtube_button.clicked.connect(self.open_youtube_video)
        youtube_layout.addWidget(self.youtube_button)
        main_layout.addLayout(youtube_layout, 1)

        # Spotify Song Recommendation Section
        spotify_layout = QHBoxLayout()
        self.spotify_recommendation = QLabel("Loading recommendation...")
        self.spotify_recommendation.setFont(QFont("Arial", 14))
        self.spotify_recommendation.setWordWrap(True)
        self.spotify_recommendation.setStyleSheet("""
            background-color: #ffffff;
            padding: 15px;
            border-radius: 10px;
            color: #880e4f;  /* Dark pink text */
        """)
        spotify_layout.addWidget(self.spotify_recommendation, 4)

        self.spotify_button = QPushButton("Listen on Spotify")
        self.spotify_button.setFont(QFont("Arial", 14))
        self.spotify_button.setStyleSheet("""
            QPushButton {
                background-color: #e91e63;  /* Pink button */
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c2185b;  /* Darker pink on hover */
            }
        """)
        self.spotify_button.clicked.connect(self.open_spotify_song)
        spotify_layout.addWidget(self.spotify_button, 1)
        main_layout.addLayout(spotify_layout)

        # Load Recommendations
        self.load_recommendations()

        # Add spacer to push everything to the top
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer)

        self.setLayout(main_layout)

    def show_profile(self):
        """
        Show the user's profile in a dialog.
        """
        profile_dialog = ProfileDialog(self)
        profile_dialog.exec_()

    def load_recommendations(self):
        """Fetch and display YouTube and Spotify recommendations."""
        youtube_recommendation = get_youtube_video()
        self.youtube_recommendation.setText(youtube_recommendation)

        spotify_recommendation = get_spotify_song()
        self.spotify_recommendation.setText(spotify_recommendation)

    def open_youtube_video(self):
        """Open the recommended YouTube video in the default browser."""
        # Extract the URL from the recommendation text
        url = extract_url(self.youtube_recommendation.text())
        if url:
            QDesktopServices.openUrl(QUrl(url))
        else:
            QMessageBox.warning(self, "Error", "No valid URL found in the recommendation.")

    def open_spotify_song(self):
        """Open the recommended Spotify song in the default browser."""
        # Extract the URL from the recommendation text
        url = extract_url(self.spotify_recommendation.text())
        if url:
            QDesktopServices.openUrl(QUrl(url))
        else:
            QMessageBox.warning(self, "Error", "No valid URL found in the recommendation.")

    def update_quote(self):
        new_quote = get_quote()
        self.quote_label.setText(new_quote)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UserHomePage("Vedanth", None, None)
    window.show()
    sys.exit(app.exec_())