from functools import wraps   # 🔹 add this import at the top with other imports
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from database import (
    db, User, CheckIn, JournalEntry, Goal,
    MeditationSession, Habit, WellnessResource, init_db
)
from config import config
import csv
from io import StringIO

# Don't need load_dotenv() - we'll use defaults
# load_dotenv()  # Comment this out

# ==================== CREATE APP ====================
app = Flask(__name__)
# Use development config by default
app.config.from_object(config['development'])
db.init_app(app)


# ==================== SESSION HELPERS ====================


def get_current_user():
    """Get current logged-in user"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


def login_required_redirect(f):
    """Redirect to login if not authenticated OR user missing in DB"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()

        # Session exists but user record missing (DB reset etc.)
        if not user:
            session.clear()
            return redirect('/')

        return f(*args, **kwargs)
    return decorated_function


def login_required_api(f):
    """Return JSON error if user not logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            session.clear()
            return jsonify({'error': 'Not logged in'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ==================== AUTHENTICATION ====================


@app.route('/')
def index():
    """Login page"""
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('login.html')


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login with access key"""
    try:
        data = request.get_json()
        access_key = data.get('access_key', '').strip()
        full_name = data.get('full_name', '').strip()

        if not access_key:
            return jsonify({'error': '❌ Access key required'}), 400

        # Check if user exists
        user = User.query.filter_by(access_key=access_key).first()

        if not user:
            # Create new user
            user = User(
                access_key=access_key,
                full_name=full_name if full_name else 'User'
            )
            db.session.add(user)
            db.session.commit()

        # Set session
        session['user_id'] = user.id
        session['full_name'] = user.full_name

        return jsonify({
            'message': '✅ Welcome!',
            'redirect': '/dashboard'
        }), 200
    except Exception as e:
        return jsonify({'error': f'❌ Error: {str(e)}'}), 500


@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect('/')

# ==================== DASHBOARD ====================


@app.route('/dashboard')
@login_required_redirect
def dashboard():
    """Main dashboard"""
    user = get_current_user()

    if not user:
        return redirect('/')  # send back to login safely

    today = datetime.utcnow().date()
    today_checkin = CheckIn.query.filter_by(
        user_id=user.id,
        check_in_date=today
    ).first()

    all_checkins = CheckIn.query.filter_by(user_id=user.id).order_by(
        CheckIn.check_in_date.desc()
    ).all()

    mood_streak = calculate_streak(user.id)
    avg_mood = calculate_avg_mood(user.id, 7)
    wellness_score = calculate_wellness_score(user.id)

    return render_template('dashboard.html',
                           user=user,
                           today_checkin=today_checkin,
                           mood_streak=mood_streak,
                           avg_mood=avg_mood,
                           wellness_score=wellness_score,
                           recent_checkins=all_checkins[:7])

# ==================== CHECK-IN ROUTES ====================


@app.route('/checkin')
@login_required_redirect
def checkin_page():
    """Check-in page"""
    user = get_current_user()
    today = datetime.utcnow().date()
    today_checkin = CheckIn.query.filter_by(
        user_id=user.id,
        check_in_date=today
    ).first()

    suggestions = get_ai_suggestions(user.id)

    return render_template('checkin.html',
                           today_checkin=today_checkin,
                           suggestions=suggestions)


@app.route('/api/checkin', methods=['POST'])
def create_checkin():
    """Create daily check-in"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        data = request.get_json()
        today = datetime.utcnow().date()

        checkin = CheckIn.query.filter_by(
            user_id=user.id,
            check_in_date=today
        ).first()

        if not checkin:
            checkin = CheckIn(user_id=user.id, check_in_date=today)

        checkin.mood = data.get('mood')
        checkin.mood_emoji = get_mood_emoji(data.get('mood'))
        checkin.stress_level = data.get('stress_level')
        checkin.sleep_hours = data.get('sleep_hours')
        checkin.sleep_quality = data.get('sleep_quality')
        checkin.notes = data.get('notes', '')
        checkin.exercise_minutes = data.get('exercise_minutes', 0)
        checkin.water_intake = data.get('water_intake', 0)
        checkin.social_interaction = data.get('social_interaction')

        db.session.add(checkin)
        db.session.commit()

        music = get_music_recommendation(checkin.mood)
        activity = get_activity_suggestion(checkin.mood, checkin.stress_level)

        return jsonify({
            'message': '✅ Check-in saved!',
            'checkin': checkin.to_dict(),
            'music': music,
            'activity': activity
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/checkin/history')
def checkin_history():
    """Get check-in history"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow().date() - timedelta(days=days)

    checkins = CheckIn.query.filter(
        CheckIn.user_id == user.id,
        CheckIn.check_in_date >= start_date
    ).order_by(CheckIn.check_in_date.desc()).all()

    return jsonify([c.to_dict() for c in checkins])


@app.route('/api/checkin/<checkin_id>', methods=['DELETE'])
def delete_checkin(checkin_id):
    """Delete a check-in"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        checkin = CheckIn.query.get(checkin_id)

        if not checkin or checkin.user_id != user.id:
            return jsonify({'error': 'Not found'}), 404

        db.session.delete(checkin)
        db.session.commit()

        return jsonify({'message': '🗑️ Deleted!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== JOURNAL ROUTES ====================


@app.route('/journal')
@login_required_redirect
def journal():
    """Journal page"""
    user = get_current_user()
    page = request.args.get('page', 1, type=int)

    entries = JournalEntry.query.filter_by(user_id=user.id).order_by(
        JournalEntry.created_at.desc()
    ).paginate(page=page, per_page=10)

    return render_template('journal.html', entries=entries)


@app.route('/api/journal', methods=['POST'])
@login_required_api
def create_journal():
    """Create journal entry"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        data = request.get_json()

        entry = JournalEntry(
            user_id=user.id,
            title=data.get('title', 'Untitled'),
            content=data.get('content'),
            mood_at_time=data.get('mood'),
            tags=data.get('tags', '')
        )

        db.session.add(entry)
        db.session.commit()

        return jsonify({
            'message': '📝 Saved!',
            'entry': entry.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/journal/<entry_id>', methods=['PUT'])
@login_required_api
def update_journal(entry_id):
    """Update journal entry"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        entry = JournalEntry.query.get(entry_id)

        if not entry or entry.user_id != user.id:
            return jsonify({'error': 'Not found'}), 404

        data = request.get_json()
        entry.title = data.get('title', entry.title)
        entry.content = data.get('content', entry.content)
        entry.mood_at_time = data.get('mood', entry.mood_at_time)
        entry.tags = data.get('tags', entry.tags)
        entry.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': '✅ Updated!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/journal/<entry_id>', methods=['DELETE'])
@login_required_api
def delete_journal(entry_id):
    """Delete journal entry"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        entry = JournalEntry.query.get(entry_id)

        if not entry or entry.user_id != user.id:
            return jsonify({'error': 'Not found'}), 404

        db.session.delete(entry)
        db.session.commit()

        return jsonify({'message': '🗑️ Deleted!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/journal/history')
@login_required_api
def journal_history():
    """Get all journal entries"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    entries = JournalEntry.query.filter_by(user_id=user.id).order_by(
        JournalEntry.created_at.desc()
    ).all()

    return jsonify([e.to_dict() for e in entries])

# ==================== ANALYTICS ====================


@app.route('/analytics')
@login_required_redirect
def analytics():
    """Analytics page"""
    user = get_current_user()
    return render_template('analytics.html', user=user)


@app.route('/api/analytics/mood-trend')
def mood_trend():
    """Mood trend data"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow().date() - timedelta(days=days)

    checkins = CheckIn.query.filter(
        CheckIn.user_id == user.id,
        CheckIn.check_in_date >= start_date
    ).order_by(CheckIn.check_in_date).all()

    return jsonify({
        'labels': [str(c.check_in_date) for c in checkins],
        'moods': [c.mood for c in checkins],
        'stress': [c.stress_level for c in checkins],
        'sleep': [c.sleep_hours for c in checkins]
    })


@app.route('/api/analytics/sleep-analysis')
def sleep_analysis():
    """Sleep analysis"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow().date() - timedelta(days=days)

    checkins = CheckIn.query.filter(
        CheckIn.user_id == user.id,
        CheckIn.check_in_date >= start_date,
        CheckIn.sleep_hours != None
    ).all()

    if not checkins:
        return jsonify({
            'avg_sleep': 0,
            'avg_quality': 0,
            'recommendation': 'Start tracking sleep!'
        })

    avg_sleep = sum(c.sleep_hours for c in checkins) / len(checkins)
    qualities = [c.sleep_quality for c in checkins if c.sleep_quality]
    avg_quality = sum(qualities) / len(qualities) if qualities else 0

    recommendation = get_sleep_recommendation(avg_sleep, avg_quality)

    return jsonify({
        'avg_sleep': round(avg_sleep, 1),
        'avg_quality': round(avg_quality, 1),
        'recommendation': recommendation
    })


@app.route('/api/analytics/summary')
def analytics_summary():
    """Analytics summary"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    all_checkins = CheckIn.query.filter_by(user_id=user.id).all()

    if not all_checkins:
        return jsonify({
            'total_checkins': 0,
            'avg_mood': 0,
            'avg_stress': 0,
            'avg_sleep': 0,
            'streak': 0
        })

    moods = [c.mood for c in all_checkins if c.mood]
    stresses = [c.stress_level for c in all_checkins if c.stress_level]
    sleeps = [c.sleep_hours for c in all_checkins if c.sleep_hours]

    return jsonify({
        'total_checkins': len(all_checkins),
        'avg_mood': round(sum(moods) / len(moods), 1) if moods else 0,
        'avg_stress': round(sum(stresses) / len(stresses), 1) if stresses else 0,
        'avg_sleep': round(sum(sleeps) / len(sleeps), 1) if sleeps else 0,
        'streak': calculate_streak(user.id)
    })

# ==================== GOALS ====================


@app.route('/goals')
@login_required_redirect
def goals():
    """Goals page"""
    user = get_current_user()
    user_goals = Goal.query.filter_by(
        user_id=user.id).order_by(Goal.created_at.desc()).all()
    return render_template('goals.html', goals=user_goals)


@app.route('/api/goals', methods=['POST'])
def create_goal():
    """Create goal"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        data = request.get_json()

        goal = Goal(
            user_id=user.id,
            title=data.get('title'),
            description=data.get('description'),
            category=data.get('category'),
            target=data.get('target'),
            target_date=datetime.fromisoformat(
                data.get('target_date')) if data.get('target_date') else None
        )

        db.session.add(goal)
        db.session.commit()

        return jsonify({'message': '🎯 Goal created!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/goals/<goal_id>', methods=['PUT'])
def update_goal(goal_id):
    """Update goal"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        goal = Goal.query.get(goal_id)

        if not goal or goal.user_id != user.id:
            return jsonify({'error': 'Not found'}), 404

        data = request.get_json()
        goal.progress_percentage = data.get(
            'progress', goal.progress_percentage)
        goal.status = data.get('status', goal.status)

        if goal.status == 'completed':
            goal.completed_at = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': '✅ Updated!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/goals/<goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    """Delete goal"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        goal = Goal.query.get(goal_id)

        if not goal or goal.user_id != user.id:
            return jsonify({'error': 'Not found'}), 404

        db.session.delete(goal)
        db.session.commit()

        return jsonify({'message': '🗑️ Deleted!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== MEDITATION ====================


@app.route('/meditation')
@login_required_redirect
def meditation():
    """Meditation page"""
    user = get_current_user()

    meditations = [
        {
            'id': 1,
            'name': '5-Min Breathing',
            'duration': 5,
            'type': 'breathing',
            'description': 'Calm your anxiety',
            'guide': 'Inhale 4, hold 4, exhale 4'
        },
        {
            'id': 2,
            'name': '10-Min Body Scan',
            'duration': 10,
            'type': 'body_scan',
            'description': 'Progressive relaxation',
            'guide': 'Scan from head to toe'
        },
        {
            'id': 3,
            'name': '15-Min Visualization',
            'duration': 15,
            'type': 'visualization',
            'description': 'Calm visualization',
            'guide': 'Visualize a peaceful place'
        }
    ]

    return render_template('meditation.html', meditations=meditations)


@app.route('/api/meditation/session', methods=['POST'])
def log_meditation():
    """Log meditation"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        data = request.get_json()

        med = MeditationSession(
            user_id=user.id,
            duration_minutes=data.get('duration'),
            type=data.get('type'),
            mood_before=data.get('mood_before'),
            mood_after=data.get('mood_after')
        )

        db.session.add(med)
        db.session.commit()

        improvement = med.mood_after - med.mood_before if med.mood_before else 0

        return jsonify({
            'message': '🧘 Logged!',
            'improvement': improvement
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/meditation/history')
def meditation_history():
    """Get meditation history"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    sessions = MeditationSession.query.filter_by(user_id=user.id).order_by(
        MeditationSession.created_at.desc()
    ).all()

    return jsonify([s.to_dict() for s in sessions])

# ==================== HABITS ====================


@app.route('/habits')
@login_required_redirect
def habits():
    """Habits page"""
    user = get_current_user()
    user_habits = Habit.query.filter_by(user_id=user.id).all()
    return render_template('habits.html', habits=user_habits)


@app.route('/api/habits', methods=['POST'])
def create_habit():
    """Create habit"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        data = request.get_json()

        habit = Habit(
            user_id=user.id,
            name=data.get('name'),
            description=data.get('description'),
            category=data.get('category'),
            frequency=data.get('frequency'),
            target=data.get('target')
        )

        db.session.add(habit)
        db.session.commit()

        return jsonify({'message': '✅ Habit created!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/habits/<habit_id>/log', methods=['POST'])
def log_habit(habit_id):
    """Log habit completion"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        habit = Habit.query.get(habit_id)

        if not habit or habit.user_id != user.id:
            return jsonify({'error': 'Not found'}), 404

        habit.last_logged = datetime.utcnow()
        habit.current_streak += 1

        if habit.current_streak > habit.best_streak:
            habit.best_streak = habit.current_streak

        db.session.commit()

        return jsonify({
            'message': '🔥 Great job!',
            'streak': habit.current_streak
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/habits/<habit_id>', methods=['DELETE'])
def delete_habit(habit_id):
    """Delete habit"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        habit = Habit.query.get(habit_id)

        if not habit or habit.user_id != user.id:
            return jsonify({'error': 'Not found'}), 404

        db.session.delete(habit)
        db.session.commit()

        return jsonify({'message': '🗑️ Deleted!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== MUSIC ====================


@app.route('/music')
@login_required_redirect
def music():
    """Music recommendations"""
    user = get_current_user()

    playlists = [
        {
            'name': '😊 Happy Vibes',
            'mood': 'happy',
            'songs': 25,
            'description': 'Uplifting and energetic music',
            'url': '#'
        },
        {
            'name': '😔 Chill Mood',
            'mood': 'calm',
            'songs': 30,
            'description': 'Relaxing and soothing music',
            'url': '#'
        },
        {
            'name': '💪 Energetic',
            'mood': 'energetic',
            'songs': 20,
            'description': 'High-energy motivational songs',
            'url': '#'
        },
        {
            'name': '🎯 Focus',
            'mood': 'focus',
            'songs': 35,
            'description': 'Concentration-boosting music',
            'url': '#'
        }
    ]

    return render_template('music.html', playlists=playlists)

# ==================== RESOURCES ====================


@app.route('/resources')
@login_required_redirect
def resources():
    """Crisis resources"""
    user = get_current_user()

    crisis_resources = WellnessResource.query.filter_by(
        category='crisis',
        is_active=True
    ).all()

    return render_template('resources.html', resources=crisis_resources)

# ==================== SETTINGS ====================


@app.route('/settings')
@login_required_redirect
def settings():
    """Settings page"""
    user = get_current_user()
    return render_template('settings.html', user=user)


@app.route('/api/settings/theme', methods=['PUT'])
def update_theme():
    """Update theme"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        data = request.get_json()
        user.theme = data.get('theme', 'light')
        db.session.commit()

        return jsonify({'message': '✅ Updated!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== DATA EXPORT ====================


@app.route('/api/export/csv')
def export_csv():
    """Export as CSV"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        checkins = CheckIn.query.filter_by(
            user_id=user.id).order_by(CheckIn.check_in_date).all()

        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(['Date', 'Mood', 'Stress',
                        'Sleep (hrs)', 'Sleep Quality', 'Notes'])
        for c in checkins:
            writer.writerow([
                c.check_in_date,
                c.mood,
                c.stress_level,
                c.sleep_hours,
                c.sleep_quality,
                c.notes
            ])

        response = output.getvalue()
        return response, 200, {
            'Content-Disposition': 'attachment; filename=mind_mate_data.csv',
            'Content-Type': 'text/csv'
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== HELPERS ====================


def get_mood_emoji(mood_score):
    """Convert mood to emoji"""
    if not mood_score:
        return '😐'
    if mood_score <= 2:
        return '😢'
    elif mood_score <= 4:
        return '😟'
    elif mood_score <= 6:
        return '😐'
    elif mood_score <= 8:
        return '😊'
    else:
        return '😄'


def calculate_streak(user_id):
    """Calculate mood streak"""
    today = datetime.utcnow().date()
    streak = 0

    for i in range(1, 366):
        check_date = today - timedelta(days=i-1)
        if CheckIn.query.filter_by(user_id=user_id, check_in_date=check_date).first():
            streak += 1
        else:
            break

    return streak


def calculate_avg_mood(user_id, days=7):
    """Calculate average mood"""
    start_date = datetime.utcnow().date() - timedelta(days=days)

    checkins = CheckIn.query.filter(
        CheckIn.user_id == user_id,
        CheckIn.check_in_date >= start_date
    ).all()

    moods = [c.mood for c in checkins if c.mood]
    return round(sum(moods) / len(moods), 1) if moods else 0


def calculate_wellness_score(user_id):
    """Calculate wellness score"""
    today = datetime.utcnow().date()
    checkin = CheckIn.query.filter_by(
        user_id=user_id, check_in_date=today).first()

    if not checkin:
        return 0

    score = 0
    if checkin.mood:
        score += checkin.mood * 10
    if checkin.sleep_hours and checkin.sleep_hours >= 7:
        score += 20
    if checkin.stress_level and checkin.stress_level <= 5:
        score += 20
    if checkin.exercise_minutes >= 30:
        score += 20

    return min(score // 3, 100)


def get_music_recommendation(mood):
    """Get music based on mood"""
    if not mood:
        return {'name': 'Feel Good Mix', 'url': '#'}

    if mood <= 3:
        return {'name': '😔 Comfort Music', 'url': '#'}
    elif mood <= 5:
        return {'name': '😐 Chill Vibes', 'url': '#'}
    else:
        return {'name': '😊 Happy Playlist', 'url': '#'}


def get_activity_suggestion(mood, stress):
    """Get activity suggestion"""
    if stress and stress >= 7:
        return 'Take a 10-minute meditation 🧘'
    elif mood and mood <= 3:
        return 'Try yoga 🧘‍♀️'
    elif mood and mood >= 8:
        return 'Go for a workout! 💪'
    else:
        return 'Take a relaxing walk 🚶‍♀️'


def get_ai_suggestions(user_id):
    """Get AI suggestions"""
    recent_checkins = CheckIn.query.filter_by(user_id=user_id).order_by(
        CheckIn.check_in_date.desc()
    ).limit(7).all()

    if not recent_checkins:
        return []

    suggestions = []
    moods = [c.mood for c in recent_checkins if c.mood]
    sleeps = [c.sleep_hours for c in recent_checkins if c.sleep_hours]
    stresses = [c.stress_level for c in recent_checkins if c.stress_level]

    if moods and sum(moods) / len(moods) <= 4:
        suggestions.append('😔 Try meditation today!')

    if sleeps and sum(sleeps) / len(sleeps) < 7:
        suggestions.append('😴 Increase sleep to 8 hours!')

    if stresses and sum(stresses) / len(stresses) >= 7:
        suggestions.append('😰 Try breathing exercises!')

    return suggestions[:3]


def get_sleep_recommendation(avg_sleep, avg_quality):
    """Get sleep recommendation"""
    if avg_sleep < 6:
        return '⚠️ Get 7-9 hours!'
    elif avg_sleep > 9:
        return '💤 Try 7-8 hours.'
    elif avg_quality < 5:
        return '😴 Try meditation before bed.'
    else:
        return '✅ Great sleep routine!'

# ==================== ADMIN ====================


@app.route('/admin/seed-resources')
def seed_resources():
    """Seed resources"""
    if WellnessResource.query.first():
        return jsonify({'message': 'Already seeded'}), 200

    resources = [
        WellnessResource(
            name='National Suicide Prevention Lifeline',
            description='24/7 free support',
            phone='1-800-273-8255',
            website='https://suicidepreventionlifeline.org',
            category='crisis',
            country='USA'
        ),
        WellnessResource(
            name='Crisis Text Line',
            description='Text HOME to 741741',
            phone='741741',
            website='https://www.crisistextline.org',
            category='crisis',
            country='USA'
        ),
        WellnessResource(
            name='International Association for Suicide Prevention',
            description='Global resources',
            website='https://www.iasp.info/resources/Crisis_Centres',
            category='crisis',
            country='Global'
        ),
        WellnessResource(
            name='NAMI Helpline',
            description='Mental health support',
            phone='1-800-950-NAMI',
            website='https://www.nami.org',
            category='support',
            country='USA'
        )
    ]

    for resource in resources:
        db.session.add(resource)

    db.session.commit()

    return jsonify({'message': '✅ Seeded!'}), 200

# ==================== ERRORS ====================


@app.errorhandler(404)
def not_found(e):
    """404 error"""
    return render_template('error.html', error='Page not found', code=404), 404


@app.errorhandler(500)
def server_error(e):
    """500 error"""
    return render_template('error.html', error='Server error', code=500), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database initialized - In Memory!")
    app.run(debug=True, host='0.0.0.0', port=5000)
