# 🧠 MindMate – Mental Wellness Tracker

MindMate is a full-stack mental wellness web application that helps users track their moods, maintain journaling habits, build daily streaks, and visualize emotional trends over time.

This project was built for a college hackathon using **Flask (Python)** for the backend and **HTML, CSS, JavaScript, and Chart.js** for the frontend.

---

## ✨ Features

- 🔐 User Authentication (Register / Login / Logout)
- 😊 Daily Mood Check-ins
- 📈 Analytics Dashboard with Mood Charts
- 🔥 Streak Tracking System
- 💡 Wellness Suggestions Based on Mood
- 📓 Personal Journal with History
- 🗑 Delete Journal Entries & Mood History
- 🎨 Clean, Responsive User Interface

---

## 🛠 Tech Stack

| Layer       | Technology Used |
|------------|-----------------|
| Backend     | Flask (Python)  |
| Database    | SQLite          |
| Frontend    | HTML, CSS, JavaScript |
| Charts      | Chart.js        |
| Styling     | Bootstrap + Custom CSS |

---

## 📂 Project Structure
mindmate/
│
├── app.py
├── requirements.txt
├── mindmate.db (created automatically)
│
├── templates/
│ ├── index.html
│ ├── dashboard.html
│ ├── journal.html
│ └── login/register pages
│
├── static/
│ ├── css/
│ ├── js/
│ └── images/


---

## ⚙️ How to Run This Project Locally

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/karthika-malladi0/mind-mate.git
cd mind-mate

python -m venv venv

venv\Scripts\activate

source venv/bin/activate

pip install -r requirements.txt

python app.py

Running on http://127.0.0.1:5000

🗄 Database

The app uses SQLite.
The database file is automatically created the first time you run the app.

🧠 Key Learning Outcomes

This project demonstrates:

Backend route handling with Flask

Database design and CRUD operations

API communication using JavaScript Fetch

Data visualization with Chart.js

User session management

Full-stack integration

🚀 Future Improvements

Cloud deployment

AI-based mood analysis

Email or notification reminders

Mobile-friendly version

👨‍💻 Developed For

College Hackathon Project – Built as a beginner-friendly full-stack mental wellness tracking system.




