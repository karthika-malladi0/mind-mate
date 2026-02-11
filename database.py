from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

# ==================== USER MODEL ====================


class User(db.Model):
    """User account model"""
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    access_key = db.Column(db.String(255), nullable=False, unique=True)
    full_name = db.Column(db.String(120))
    bio = db.Column(db.Text)
    theme = db.Column(db.String(20), default='light')  # light or dark

    # Relationships
    checkins = db.relationship(
        'CheckIn', backref='user', lazy=True, cascade='all, delete-orphan')
    journal_entries = db.relationship(
        'JournalEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user',
                            lazy=True, cascade='all, delete-orphan')
    meditations = db.relationship(
        'MeditationSession', backref='user', lazy=True, cascade='all, delete-orphan')
    habits = db.relationship('Habit', backref='user',
                             lazy=True, cascade='all, delete-orphan')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.access_key}>'

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat()
        }

# ==================== CHECK-IN MODEL ====================


class CheckIn(db.Model):
    """Daily mood check-in model"""
    __tablename__ = 'checkins'

    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey(
        'users.id'), nullable=False, index=True)

    mood = db.Column(db.Integer)  # 1-10
    mood_emoji = db.Column(db.String(10))
    stress_level = db.Column(db.Integer)  # 1-10
    sleep_hours = db.Column(db.Float)
    sleep_quality = db.Column(db.Integer)  # 1-10
    notes = db.Column(db.Text)

    exercise_minutes = db.Column(db.Integer, default=0)
    water_intake = db.Column(db.Integer, default=0)
    social_interaction = db.Column(db.String(50))

    check_in_date = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CheckIn {self.check_in_date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'mood': self.mood,
            'mood_emoji': self.mood_emoji,
            'stress_level': self.stress_level,
            'sleep_hours': self.sleep_hours,
            'sleep_quality': self.sleep_quality,
            'date': self.check_in_date.isoformat(),
            'notes': self.notes
        }

# ==================== JOURNAL MODEL ====================


class JournalEntry(db.Model):
    """Therapy journal entry model"""
    __tablename__ = 'journal_entries'

    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey(
        'users.id'), nullable=False, index=True)

    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    mood_at_time = db.Column(db.Integer)  # 1-10
    tags = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<JournalEntry {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'mood': self.mood_at_time,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# ==================== GOAL MODEL ====================


class Goal(db.Model):
    """Wellness goal tracking model"""
    __tablename__ = 'goals'

    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey(
        'users.id'), nullable=False, index=True)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # exercise, sleep, meditation, social
    target = db.Column(db.String(255))

    status = db.Column(db.String(20), default='in_progress')
    progress_percentage = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    target_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Goal {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'progress': self.progress_percentage,
            'status': self.status
        }

# ==================== MEDITATION MODEL ====================


class MeditationSession(db.Model):
    """Meditation session tracking model"""
    __tablename__ = 'meditations'

    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey(
        'users.id'), nullable=False, index=True)

    duration_minutes = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50))  # breathing, body_scan, visualization
    description = db.Column(db.Text)
    mood_before = db.Column(db.Integer)  # 1-10
    mood_after = db.Column(db.Integer)   # 1-10

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'duration': self.duration_minutes,
            'type': self.type,
            'mood_improvement': (self.mood_after - self.mood_before) if self.mood_before else 0
        }

# ==================== HABIT MODEL ====================


class Habit(db.Model):
    """Habit tracking model"""
    __tablename__ = 'habits'

    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey(
        'users.id'), nullable=False, index=True)

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # exercise, sleep, eating, social
    frequency = db.Column(db.String(20))  # daily, weekly
    target = db.Column(db.String(255))

    status = db.Column(db.String(20), default='active')
    current_streak = db.Column(db.Integer, default=0)
    best_streak = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_logged = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'current_streak': self.current_streak,
            'best_streak': self.best_streak
        }

# ==================== RESOURCE MODEL ====================


class WellnessResource(db.Model):
    """Crisis helplines and wellness resources model"""
    __tablename__ = 'wellness_resources'

    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(255))
    category = db.Column(db.String(50))  # crisis, counseling, support
    country = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'category': self.category
        }


def init_db(app):
    """Initialize database with app"""
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully!")
