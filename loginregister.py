import sys
import sqlite3
import smtplib
from email.message import EmailMessage
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QFormLayout, QComboBox, QTextEdit, QStackedWidget, QApplication
from PyQt5.QtGui import QFont, QPixmap, QColor, QPalette, QLinearGradient
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve

# Database Setup
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    country TEXT,
    user_type TEXT,
    hobbies TEXT,
    stressors TEXT,
    relaxation TEXT
)
""")
conn.commit()

# Email Sending Function
def send_welcome_email(user_email, user_name):
    sender_email = "vedanth.aggarwal@gmail.com"  # Replace with your email
    sender_password = "sosn sqso pncz uzjc"  # Replace with your app password

    msg = EmailMessage()
    msg.set_content(f"Welcome to Serenity, {user_name}!\n\nWe're excited to have you on board. Explore and find your peace.")
    msg["Subject"] = "Welcome to Serenity"
    msg["From"] = sender_email
    msg["To"] = user_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Welcome email sent!")
    except Exception as e:
        print("Error sending email:", e)

# Custom Styling with QSS
style = """
    QWidget {
        background-color: #F5F5F5;
        color: #333333;
        font-family: 'Segoe UI', sans-serif;
    }
    QLabel {
        font-size: 18px;
        font-weight: bold;
        color: #444444;
    }
    QLineEdit, QTextEdit, QComboBox {
        background: #FFFFFF;
        color: #333333;
        border: 2px solid #DDDDDD;
        border-radius: 5px;
        padding: 10px;
        font-size: 16px;
    }
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
        border-color: #6A5ACD;
    }
    QPushButton {
        background-color: #6A5ACD;
        color: white;
        font-size: 18px;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
    }
    QPushButton:hover {
        background-color: #7B68EE;
    }
    QPushButton:pressed {
        background-color: #483D8B;
    }
    QStackedWidget {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6A5ACD, stop:1 #7B68EE);
    }
"""

class WelcomePage(QWidget):
    def __init__(self, stacked_widget, main_app):
        super().__init__()
        self.setWindowTitle("Welcome to Serenity")

        self.setGeometry(300, 100, 800, 600)
        self.setStyleSheet(style)

        self.stacked_widget = stacked_widget
        self.main_app = main_app  # Reference to the main application
        layout = QVBoxLayout()
        
        # Header Image
        self.header_label = QLabel(self)
        self.header_label.setPixmap(QPixmap("cover.jpg").scaled(800, 300, Qt.KeepAspectRatioByExpanding))
        self.header_label.setAlignment(Qt.AlignCenter)
        
        # Title - Very Big Font
        title = QLabel("Serenity")
        title.setFont(QFont("Segoe UI", 300, QFont.Bold))  # Increased font size to 72
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #6A5ACD; margin-top: 20px; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);")
        
        # Tagline
        tagline = QLabel("Find your peace, embrace your journey.")
        tagline.setFont(QFont("Segoe UI", 24))
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet("color: #666666; margin-bottom: 30px;")
        
        # Buttons
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.show_login)
        self.login_btn.setFixedSize(200, 50)
        
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.show_register)
        self.register_btn.setFixedSize(200, 50)
        
        # Layout
        layout.addWidget(self.header_label)
        layout.addWidget(title)
        layout.addWidget(tagline)
        layout.addSpacing(20)
        layout.addWidget(self.login_btn, alignment=Qt.AlignCenter)
        layout.addWidget(self.register_btn, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        
        self.setLayout(layout)
    
    def show_login(self):
        self.stacked_widget.setCurrentIndex(1)
    
    def show_register(self):
        self.stacked_widget.setCurrentIndex(2)

# Registration Window
class RegisterWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setWindowTitle("Register - Serenity")
        self.setGeometry(300, 100, 800, 600)
        self.setStyleSheet(style)
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.country_input = QLineEdit()
        self.user_type = QComboBox()
        self.user_type.addItems(["Student", "Adult"])
        self.hobbies_input = QTextEdit()
        self.stressors_input = QTextEdit()
        self.relaxation_input = QTextEdit()
        
        form_layout.addRow("Full Name:", self.name_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Country:", self.country_input)
        form_layout.addRow("User Type:", self.user_type)
        form_layout.addRow("Hobbies:", self.hobbies_input)
        form_layout.addRow("Stressors:", self.stressors_input)
        form_layout.addRow("Relaxation Methods:", self.relaxation_input)
        
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.register_user)
        self.register_btn.setFixedSize(200, 50)
        
        layout.addLayout(form_layout)
        layout.addWidget(self.register_btn, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def register_user(self):
        full_name = self.name_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        country = self.country_input.text()
        user_type = self.user_type.currentText()
        hobbies = self.hobbies_input.toPlainText()
        stressors = self.stressors_input.toPlainText()
        relaxation = self.relaxation_input.toPlainText()
        
        if not full_name or not email or not password:
            QMessageBox.warning(self, "Error", "Please fill in all required fields.")
            return
        
        try:
            cursor.execute("INSERT INTO users (full_name, email, password, country, user_type, hobbies, stressors, relaxation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (full_name, email, password, country, user_type, hobbies, stressors, relaxation))
            conn.commit()
            send_welcome_email(email, full_name)
            QMessageBox.information(self, "Success", "Account created successfully! Check your email.")
            self.stacked_widget.setCurrentIndex(0)
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Email already registered.")

class LoginWindow(QWidget):
    def __init__(self, stacked_widget, main_app):
        super().__init__()
        self.setWindowTitle("Login - Serenity")
        self.setGeometry(300, 100, 800, 600)
        self.setStyleSheet(style)
        self.stacked_widget = stacked_widget
        self.main_app = main_app  # Reference to the main application

        layout = QVBoxLayout()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.login_user)
        self.login_btn.setFixedSize(200, 50)

        layout.addStretch(1)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        layout.addSpacing(20)
        layout.addWidget(self.login_btn, alignment=Qt.AlignCenter)
        layout.addStretch(1)

        self.setLayout(layout)

    def login_user(self):
        email = self.email_input.text()
        password = self.password_input.text()
        
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        
        if user:
            QMessageBox.information(self, "Login Successful", "Welcome back!")
            self.main_app.show_homepage(user[1])  # Pass the username to the homepage
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials.")

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serenity")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet(style)

        self.stacked_widget = QStackedWidget()
        self.welcome_page = WelcomePage(self.stacked_widget, self)
        self.login_page = LoginWindow(self.stacked_widget, self)
        self.register_page = RegisterWindow(self.stacked_widget)

        self.stacked_widget.addWidget(self.welcome_page)
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.register_page)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    def show_homepage(self, username):
        # Placeholder for homepage functionality
        QMessageBox.information(self, "Welcome", f"Hello, {username}! You are now on the homepage.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())