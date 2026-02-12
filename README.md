# 🧠 MindMate – Mental Wellness Tracker

MindMate is a full-stack mental wellness web application built using Flask (Python) that allows users to track moods, maintain journals, build habits, follow goals, and improve overall well-being through simple daily check-ins and insights.

This project was developed as a hackathon submission to demonstrate full-stack development skills.

---

# 🚀 Features

- 🔐 User Authentication (Register / Login / Logout)
- 😊 Daily Mood Check-ins
- 📓 Personal Journal
- 🔥 Habit Tracking
- 🎯 Goal Tracking
- 📊 Analytics Dashboard with Charts
- 🧘 Meditation & Relaxation Section
- 🎵 Mood-based Music Suggestions
- 📚 Mental Health Resources
- ⚙️ User Settings Panel
- 🎨 Responsive UI using Bootstrap

---

# 🛠 Tech Stack

**Backend**
- Python
- Flask

**Database**
- SQLite

**Frontend**
- HTML
- CSS
- JavaScript
- Bootstrap
- Chart.js

---

# 📂 Project Structure

```
mindmate/
│
├── app.py
├── config.py
├── database.py
├── requirements.txt
├── mindmate.db
│
├── templates/
│   ├── analytics.html
│   ├── base.html
│   ├── checkin.html
│   ├── dashboard.html
│   ├── error.html
│   ├── goals.html
│   ├── habits.html
│   ├── journal.html
│   ├── login.html
│   ├── meditation.html
│   ├── music.html
│   ├── resources.html
│   └── settings.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   ├── images/
│   └── favicon.ico
```

---

# ⚙️ How to Run This Project

## Step 1: Clone the Repository

```bash
git clone https://github.com/karthika-malladi0/mind-mate.git
cd mindmate
```

---

## Step 2: Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

### Windows:
```bash
venv\Scripts\activate
```

### Mac/Linux:
```bash
source venv/bin/activate
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4: Run the Application

```bash
python app.py
```

You should see:

```
Running on http://127.0.0.1:5000
```

Open that link in your browser.

---

# 🗄 Database Information

This project uses SQLite.

The database file (`mindmate.db`) is already included but will also auto-update when the application runs.

---

# 🧠 What This Project Demonstrates

- Flask backend routing and architecture
- Database design with SQLite
- Full CRUD functionality
- Frontend + Backend integration
- REST-style API calls using JavaScript Fetch
- Data visualization using Chart.js
- User authentication and session handling
- Clean UI with responsive design

---

# 🔮 Improvements (if there are no time constrains)

- Cloud deployment (Render/Heroku/AWS)
- AI-based mood insights
- Email reminders for habits
- Mobile app version

---

# 👨‍💻 Hackathon Submission

MindMate is designed as a beginner-friendly but feature-rich mental wellness platform that showcases practical full-stack development and user-centered design.

