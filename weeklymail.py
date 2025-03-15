import sqlite3
import smtplib
import schedule
import time
import os
from email.message import EmailMessage
from groq import Groq

# Database Connection
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Email Configuration
SENDER_EMAIL = "vedanth.aggarwal@gmail.com"  # Replace with your email
SENDER_PASSWORD = "sosn sqso pncz uzjc"  # Replace with app password

# Groq API Configuration
client = Groq(
    api_key="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",
)

# Function to generate personalized blog content using Groq API
def generate_blog_content(user_data):
    prompt = f"""
    Write a personalized mental health blog post for {user_data['full_name']}. 
    The post should be 3 paragraphs long, include emojis if possible, and provide additional links to resources at the end.

    Here are some details about {user_data['full_name']}:
    - Hobbies: {user_data['hobbies']}
    - Stressors: {user_data['stressors']}
    - Relaxation techniques: {user_data['relaxation']}

    The blog post should address their stressors, suggest relaxation techniques, and incorporate their hobbies to promote mental well-being.
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
        stream=False,
    )

    return chat_completion.choices[0].message.content

# Function to send email
def send_email(recipient_email, recipient_name, blog_content):
    msg = EmailMessage()
    msg.set_content(blog_content)
    msg["Subject"] = "Weekly Wellness: Personalized Mental Health Tips"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {recipient_name} at {recipient_email}")
    except Exception as e:
        print(f"Error sending email to {recipient_email}: {e}")

# Function to fetch users and send emails
def send_weekly_email():
    cursor.execute("SELECT full_name, email, hobbies, stressors, relaxation FROM users")
    users = cursor.fetchall()

    for user in users:
        full_name, email, hobbies, stressors, relaxation = user
        user_data = {
            "full_name": full_name,
            "hobbies": hobbies,
            "stressors": stressors,
            "relaxation": relaxation
        }
        blog_content = generate_blog_content(user_data)
        send_email(email, full_name, blog_content)
        print('done')

# Schedule the function to run every Monday
schedule.every().saturday.at("19:04").do(send_weekly_email)

print("Weekly email scheduler is running...")

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute