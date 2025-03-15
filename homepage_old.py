# homepage.py

import sys
import requests
import random
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout, QSpacerItem,
    QSizePolicy, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

def get_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=5)
        response.raise_for_status()
        quote_data = response.json()
        return quote_data[0]['q']
    except requests.RequestException as e:
        print(f"Error fetching quote: {e}")
        return "Take time to do what makes your soul happy."

def get_quote2(keyword="strength"):
    try:
        response = requests.get(f"https://stoicismquote.com/api/v1/quote/search?keyword={keyword}", timeout=5)
        response.raise_for_status()
        quote_data = response.json()
        quotes = quote_data.get("quotes", [])
        if not quotes:
            return "Take time to do what makes your soul happy."
        random_quote = random.choice(quotes)
        return random_quote["quote"]
    except requests.RequestException as e:
        print(f"Error fetching quote: {e}")
        return "Take time to do what makes your soul happy."

class UserHomePage(QWidget):
    def __init__(self, username, stacked_widget, main_app):
        """
        Accepts a `username` so we can greet the user by name. 
        """
        super().__init__()
        self.username = username
        self.stacked_widget = stacked_widget
        self.main_app = main_app

        self.setWindowTitle("Serenity - Home")
        self.setFixedSize(1280, 832)
        self.setStyleSheet("background-color: #D0F8CE;")

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        # Background
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)
        pixmap = QPixmap("green_bg.jpg")  # Place "green_bg.jpg" in same folder
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                self.width(),
                self.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.bg_label.setPixmap(pixmap)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())

        # Semi-transparent frame
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 16px;
            }
        """)
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)

        h_container = QHBoxLayout()
        h_container.addStretch()
        h_container.addWidget(self.content_frame)
        h_container.addStretch()

        self.main_layout.addStretch()
        self.main_layout.addLayout(h_container)
        self.main_layout.addStretch()

        # Top Bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        # Greet with dynamic username
        hello_label = QLabel(f"Hello, {self.username}")
        hello_label.setFont(QFont("SF Pro", 26, QFont.Bold))
        hello_label.setStyleSheet("color: #2E7D32;")  # Dark green

        self.profile_icon = QLabel()
        self.profile_icon.setFixedSize(50, 50)
        self.profile_icon.setStyleSheet("border-radius: 25px;")

        # Attempt to load profile_pic.png
        pic = QPixmap("profile_pic.png")  # Place "profile_pic.png" in same folder
        if not pic.isNull():
            pic = pic.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.profile_icon.setPixmap(pic)
        else:
            # fallback green circle
            self.profile_icon.setStyleSheet("""
                background-color: #66BB6A;
                border-radius: 25px;
            """)

        # Make profile icon clickable
        self.profile_icon.mousePressEvent = self.go_to_profile

        top_bar.addWidget(hello_label)
        top_bar.addStretch()
        top_bar.addWidget(self.profile_icon)
        self.content_layout.addLayout(top_bar)

        # Quote Label
        self.quote_label = QLabel(get_quote())
        self.quote_label.setFont(QFont("SF Pro", 20, QFont.StyleItalic))
        self.quote_label.setWordWrap(True)
        self.quote_label.setAlignment(Qt.AlignCenter)
        self.quote_label.setStyleSheet("""
            background-color: #FFFFFF;
            padding: 20px;
            border-radius: 12px;
            color: #2F2F2F;
            font-style: italic;
        """)
        self.content_layout.addWidget(self.quote_label)

        # Buttons Grid
        self.buttons_grid = QGridLayout()
        self.buttons_grid.setSpacing(15)
        for col in range(4):
            self.buttons_grid.setColumnStretch(col, 1)

        # Row 1
        self.new_quote_btn = self.create_feature_button("New Quote", "#9B59B6", "#8E44AD", self.update_quote)
        self.buttons_grid.addWidget(self.new_quote_btn, 0, 0)

        self.reflection_btn = self.create_feature_button("Daily Reflection", "#3498DB", "#2980B9", self.main_app.show_reflection_page)
        self.buttons_grid.addWidget(self.reflection_btn, 0, 1)

        self.chatbot_btn = self.create_feature_button("AI Companion", "#2ECC71", "#27AE60", self.main_app.show_chatbot_page)
        self.buttons_grid.addWidget(self.chatbot_btn, 0, 2)

        self.mood_tracker_btn = self.create_feature_button("Mood Tracker", "#E67E22", "#D35400", self.main_app.show_mood_tracker_page)
        self.buttons_grid.addWidget(self.mood_tracker_btn, 0, 3)

        # Row 2
        self.counsellor_btn = self.create_feature_button("Find a Counsellor", "#9B59B6", "#8E44AD", self.main_app.show_counsellor_page)
        self.buttons_grid.addWidget(self.counsellor_btn, 1, 0)

        self.chat_btn = self.create_feature_button("Chat with Buddies", "#1ABC9C", "#16A085", self.main_app.show_chat_page)
        self.buttons_grid.addWidget(self.chat_btn, 1, 1)

        self.textchat_btn = self.create_feature_button("GUIDANCE BOT", "#1ABC9C", "#16A085", self.main_app.show_chat_page2)
        self.buttons_grid.addWidget(self.textchat_btn, 1, 2)

        self.content_layout.addLayout(self.buttons_grid)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.content_layout.addItem(spacer)

        self.bg_label.lower()

    def set_username(self, new_username):
        """
        If we want to update the username after the page is created.
        """
        self.username = new_username

    def create_feature_button(self, text, bg_color, hover_color, slot):
        btn = QPushButton(text)
        btn.setFont(QFont("SF Pro", 16, QFont.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: #FFFFFF;
                padding: 15px;
                border-radius: 10px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)
        btn.clicked.connect(slot)
        return btn

    def update_quote(self):
        new_quote = get_quote()
        self.quote_label.setText(new_quote)

    def go_to_profile(self, event):
        if self.main_app:
            self.main_app.show_profile_page()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        pixmap = QPixmap("green_bg.jpg")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                self.width(),
                self.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.bg_label.setPixmap(pixmap)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # Example usage:
    window = UserHomePage("Shaurya Shekhawat", None, None)
    window.show()
    sys.exit(app.exec_())
