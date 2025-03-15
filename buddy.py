import sys
import sqlite3
from openai import OpenAI  # OpenAI API
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QListWidget, QHBoxLayout, QMessageBox, QStackedWidget, QLineEdit, QTabWidget
)
from PyQt5.QtCore import Qt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# OpenAI API Key (replace with your key)
client = OpenAI(api_key="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")

# Database setup
def create_database():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    bio TEXT NOT NULL,
                    interests TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user1_id INTEGER NOT NULL,
                    user2_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS community_chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

# Insert dummy data into the database
def insert_dummy_data():
    users = [
        ("Alice", "I love hiking and reading.", "hiking, reading, yoga"),
        ("Bob", "I enjoy coding and playing guitar.", "coding, music, gaming"),
        ("Charlie", "I'm a foodie and love traveling.", "food, travel, photography"),
        ("Diana", "I'm passionate about fitness and health.", "fitness, health, nutrition"),
        ("Eve", "I love painting and gardening.", "art, gardening, nature")
    ]
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.executemany('''INSERT INTO users (name, bio, interests) VALUES (?, ?, ?)''', users)

    # Insert dummy chat history
    chats = [
        (1, 2, "Hi Bob, how are you?", "2023-10-01 10:00:00"),
        (2, 1, "Hey Alice, I'm good! How about you?", "2023-10-01 10:05:00"),
        (1, 2, "I'm doing great, thanks!", "2023-10-01 10:10:00"),
        (1, 3, "Hi Charlie, what's up?", "2023-10-02 11:00:00"),
        (3, 1, "Not much, just planning my next trip!", "2023-10-02 11:05:00"),
        (1, 4, "Hey Diana, how's your fitness journey going?", "2023-10-03 12:00:00"),
        (4, 1, "It's going great! Just hit a new PR at the gym.", "2023-10-03 12:05:00")
    ]
    c.executemany('''INSERT INTO chats (user1_id, user2_id, message, timestamp)
                     VALUES (?, ?, ?, ?)''', chats)

    # Insert dummy community chat history
    community_chats = [
        (1, "Hey everyone, how's it going?", "2023-10-01 10:00:00"),
        (2, "Hi Alice! I'm doing well, how about you?", "2023-10-01 10:05:00"),
        (3, "Hello all! What's everyone up to?", "2023-10-02 11:00:00"),
        (4, "Just finished a workout, feeling great!", "2023-10-03 12:00:00"),
        (5, "Anyone into gardening? I need some tips!", "2023-10-04 13:00:00")
    ]
    c.executemany('''INSERT INTO community_chats (user_id, message, timestamp)
                     VALUES (?, ?, ?)''', community_chats)
    conn.commit()
    conn.close()

# Fetch all users except the current user
def fetch_users(current_user_id):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id != ?", (current_user_id,))
    users = c.fetchall()
    conn.close()
    return users

# Perform similarity search
def find_similar_users(current_user_profile, all_users):
    # Combine bio and interests for similarity calculation
    profiles = [f"{user[2]} {user[3]}" for user in all_users]
    profiles.insert(0, f"{current_user_profile[2]} {current_user_profile[3]}")

    # Use TF-IDF and cosine similarity
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(profiles)
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Get top 3 similar users
    top_indices = similarities.argsort()[-3:][::-1]
    top_users = [all_users[i] for i in top_indices]
    return top_users

# Fetch chat history between two users
def fetch_chat_history(user1_id, user2_id):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute('''SELECT * FROM chats WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)
                 ORDER BY timestamp''', (user1_id, user2_id, user2_id, user1_id))
    chat_history = c.fetchall()
    conn.close()
    return chat_history

# Fetch community chat history
def fetch_community_chat_history():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute('''SELECT users.name, community_chats.message, community_chats.timestamp
                 FROM community_chats
                 JOIN users ON community_chats.user_id = users.id
                 ORDER BY community_chats.timestamp''')
    chat_history = c.fetchall()
    conn.close()
    return chat_history

# Save a new message to the database
def save_message(user1_id, user2_id, message):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''INSERT INTO chats (user1_id, user2_id, message, timestamp)
                 VALUES (?, ?, ?, ?)''', (user1_id, user2_id, message, timestamp))
    conn.commit()
    conn.close()

# Save a new community message to the database
def save_community_message(user_id, message):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''INSERT INTO community_chats (user_id, message, timestamp)
                 VALUES (?, ?, ?)''', (user_id, message, timestamp))
    conn.commit()
    conn.close()

# Generate a random conversation starter using OpenAI API
def generate_conversation_starter():
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Generate a concise engaging prompt/conversation start for a mental health community chat. MAX 12 WORDS!!"}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating conversation starter: {e}")
        return "Let's get the conversation started! How's everyone doing today?"

# Main application window
class ChatApp(QMainWindow):
    def __init__(self, stacked_widget, main_app):
        super().__init__()
        self.stacked_widget = stacked_widget  # Store the stacked widget
        self.main_app = main_app  # Store the main application reference
        create_database()
        insert_dummy_data()
        self.current_user_id = 1  # Replace with the logged-in user's ID
        self.current_user_profile = self.fetch_user_profile(self.current_user_id)
        self.init_ui()

    def fetch_user_profile(self, user_id):
        conn = sqlite3.connect("chat.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        profile = c.fetchone()
        conn.close()
        return profile

    def init_ui(self):
        self.setWindowTitle("Chat with Buddies")
        self.setGeometry(100, 100, 1200, 800)

        # Main layout
        main_layout = QHBoxLayout()

        # Left panel for buddy list and search
        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(10, 10, 10, 10)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search users...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #ccc;
            }
        """)
        self.search_bar.textChanged.connect(self.search_users)
        left_panel.addWidget(self.search_bar)

        # Title
        title = QLabel("Top 3 Buddies")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000;")
        left_panel.addWidget(title)

        # Find similar users
        all_users = fetch_users(self.current_user_id)
        self.similar_users = find_similar_users(self.current_user_profile, all_users)

        # Display top 3 similar users
        self.buddy_list = QListWidget()
        self.buddy_list.setStyleSheet("""
            QListWidget {
                font-size: 16px;
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 10px;
                color: #000000;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }
            QListWidget::item:hover {
                background-color: #3498db;
                color: white;
            }
        """)
        for user in self.similar_users:
            self.buddy_list.addItem(f"{user[1]} - {user[3]}")
        left_panel.addWidget(self.buddy_list)

        # Back button
        back_button = QPushButton("Back to Home")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        back_button.clicked.connect(self.go_back)
        left_panel.addWidget(back_button)

        # Add left panel to main layout
        main_layout.addLayout(left_panel, 1)

        # Right panel for chat interface
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
            }
            QTabBar::tab {
                font-size: 16px;
                padding: 20px;  /* Increase padding for larger tabs */
                border-radius: 5px;
                background-color: #f0f0f0;  /* Light gray for inactive tabs */
                color: #000000;  /* Black text for inactive tabs */
            }
            QTabBar::tab:selected {
                background-color: #3498db;  /* Blue for active tab */
                color: white;  /* White text for active tab */
            }
            QTabBar {
                background-color: transparent;  /* Transparent background */
            }
        """)
        self.tabs.setUsesScrollButtons(False)  # Disable scroll buttons
        self.tabs.setElideMode(Qt.ElideNone)  # Prevent text eliding
        self.tabs.setDocumentMode(True)  # Remove unnecessary borders
        self.tabs.tabBar().setExpanding(True)  # Stretch tabs to fill space

        # Buddy Chat Tab
        self.buddy_chat_tab = QWidget()
        self.init_buddy_chat_tab()
        self.tabs.addTab(self.buddy_chat_tab, "Buddy Chat")

        # Community Chat Tab
        self.community_chat_tab = QWidget()
        self.init_community_chat_tab()
        self.tabs.addTab(self.community_chat_tab, "Community Chat")

        # Add tabs to main layout
        main_layout.addWidget(self.tabs, 2)

        # Set layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Connect buddy selection to chat display
        self.buddy_list.itemClicked.connect(self.load_chat_history)

        # Load chat history for the first buddy by default
        if self.similar_users:
            self.buddy_list.setCurrentRow(0)  # Select the first buddy
            self.load_chat_history()

    def init_buddy_chat_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                background-color: #ffffff;
                border-radius: 10px;
                padding: 10px;
                color: #000000;
            }
        """)
        layout.addWidget(self.chat_display)

        # Message input
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                background-color: #ffffff;
                border-radius: 10px;
                padding: 10px;
                color: #000000;
            }
        """)
        layout.addWidget(self.message_input)

        # Send button
        send_button = QPushButton("Send")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

        self.buddy_chat_tab.setLayout(layout)

    def init_community_chat_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Community chat display
        self.community_chat_display = QTextEdit()
        self.community_chat_display.setReadOnly(True)
        self.community_chat_display.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                background-color: #ffffff;
                border-radius: 10px;
                padding: 10px;
                color: #000000;
            }
        """)
        layout.addWidget(self.community_chat_display)

        # Conversation starter
        self.conversation_starter_label = QLabel()
        self.conversation_starter_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")
        self.conversation_starter_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.conversation_starter_label)

        # Generate conversation starter button
        generate_starter_button = QPushButton("Generate Conversation Starter")
        generate_starter_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        generate_starter_button.clicked.connect(self.generate_conversation_starter)
        layout.addWidget(generate_starter_button)

        # Community message input
        self.community_message_input = QTextEdit()
        self.community_message_input.setPlaceholderText("Type your message here...")
        self.community_message_input.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                background-color: #ffffff;
                border-radius: 10px;
                padding: 10px;
                color: #000000;
            }
        """)
        layout.addWidget(self.community_message_input)

        # Send community message button
        send_community_button = QPushButton("Send to Community")
        send_community_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        send_community_button.clicked.connect(self.send_community_message)
        layout.addWidget(send_community_button)

        self.community_chat_tab.setLayout(layout)

        # Load community chat history
        self.load_community_chat_history()

    def search_users(self):
        search_text = self.search_bar.text().lower()
        all_users = fetch_users(self.current_user_id)
        self.buddy_list.clear()
        for user in all_users:
            if search_text in user[1].lower() or search_text in user[3].lower():
                self.buddy_list.addItem(f"{user[1]} - {user[3]}")

    def load_chat_history(self):
        selected_item = self.buddy_list.currentItem()
        if not selected_item:
            return

        selected_buddy_name = selected_item.text().split(" - ")[0]
        try:
            selected_buddy = next(user for user in self.similar_users if user[1] == selected_buddy_name)
            self.selected_buddy_id = selected_buddy[0]

            # Fetch and display chat history
            chat_history = fetch_chat_history(self.current_user_id, self.selected_buddy_id)
            self.chat_display.clear()
            for chat in chat_history:
                sender = "You" if chat[1] == self.current_user_id else selected_buddy_name
                self.chat_display.append(f"{sender}: {chat[3]}\n")
        except StopIteration:
            QMessageBox.warning(self, "Error", "Selected buddy not found in the list.")

    def send_message(self):
        message = self.message_input.toPlainText()
        if not message:
            QMessageBox.warning(self, "Error", "Please type a message before sending.")
            return

        # Save message to database
        save_message(self.current_user_id, self.selected_buddy_id, message)

        # Update chat display
        self.chat_display.append(f"You: {message}\n")
        self.message_input.clear()

    def load_community_chat_history(self):
        chat_history = fetch_community_chat_history()
        self.community_chat_display.clear()
        for chat in chat_history:
            self.community_chat_display.append(f"{chat[0]}: {chat[1]}\n")

    def generate_conversation_starter(self):
        starter = generate_conversation_starter()
        self.conversation_starter_label.setText(f"{starter}")

    def send_community_message(self):
        message = self.community_message_input.toPlainText()
        if not message:
            QMessageBox.warning(self, "Error", "Please type a message before sending.")
            return

        # Save message to database
        save_community_message(self.current_user_id, message)

        # Update community chat display
        self.community_chat_display.append(f"You: {message}\n")
        self.community_message_input.clear()

    def go_back(self):
        """Navigate back to the homepage."""
        self.stacked_widget.setCurrentWidget(self.main_app.home_page)

# Main application
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget()
        create_database()
        insert_dummy_data()
        self.setCentralWidget(self.stacked_widget)

        # Home page
        self.home_page = QWidget()
        home_layout = QVBoxLayout()
        home_layout.addWidget(QLabel("Welcome to Buddy Finder"))
        start_button = QPushButton("Start Chatting")
        start_button.clicked.connect(self.start_chatting)
        home_layout.addWidget(start_button)
        self.home_page.setLayout(home_layout)

        # Chat page
        self.chat_page = ChatApp(self.stacked_widget, self)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.chat_page)

        self.setWindowTitle("Buddy Finder")
        self.setGeometry(100, 100, 1200, 800)

    def start_chatting(self):
        self.stacked_widget.setCurrentWidget(self.chat_page)

if __name__ == "__main__":
    create_database()
    insert_dummy_data()  # Comment this line after first run to avoid duplicate data

    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())