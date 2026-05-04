from flask import Blueprint, request, jsonify
from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user
import secrets
from datetime import datetime, timedelta
from models import Opportunity
from flask import session

main = Blueprint('main', __name__)


# ===== LOGIN =====
@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    # 🔥 GENERIC ERROR (IMPORTANT)
    if not user or not check_password_hash(user.password, password):
        return jsonify({
            'status': 'error',
            'error': 'Invalid email or password'
        })

    login_user(user)

    return jsonify({'status': 'success'})


# ===== SIGNUP =====
@main.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')

    # 🔥 BASIC VALIDATION (required)
    if not full_name or not email or not password:
        return jsonify({'status': 'error', 'error': 'All fields are required'})

    if len(password) < 8:
        return jsonify({'status': 'error', 'error': 'Password must be at least 8 characters'})

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'status': 'error', 'error': 'User already exists'})

    hashed_password = generate_password_hash(password)

    new_user = User(
        full_name=full_name,
        email=email,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'status': 'success'})


# ===== FORGOT PASSWORD =====
@main.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()

    if user:
        token = secrets.token_urlsafe(32)
        expiry = datetime.utcnow() + timedelta(hours=1)

        user.reset_token = token
        user.reset_token_expiry = expiry
        db.session.commit()

        reset_link = f"http://127.0.0.1:5000/reset-password/{token}"

        print("\n🔥 RESET LINK:", reset_link)

    # 🔥 ALWAYS SAME RESPONSE (privacy)
    return jsonify({
        'status': 'success',
        'message': 'If the email exists, a reset link has been sent.'
    })


# ===== RESET PASSWORD =====
@main.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    data = request.get_json()
    new_password = data.get('password')

    user = User.query.filter_by(reset_token=token).first()

    if not user or user.reset_token_expiry < datetime.utcnow():
        return jsonify({
            'status': 'error',
            'error': 'Invalid or expired link'
        })

    user.password = generate_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expiry = None

    db.session.commit()

    return jsonify({'status': 'success'})


# ===== PROTECTED ROUTE =====
@main.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return jsonify({
        'status': 'success',
        'message': 'Welcome to dashboard',
        'user': current_user.email
    })


# ===== LOGOUT =====
@main.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'status': 'success', 'message': 'Logged out'})

@main.route('/opportunities', methods=['GET'])
@login_required
def get_opportunities():
    opportunities = Opportunity.query.filter_by(user_id=current_user.id).all()

    result = []
    for opp in opportunities:
        result.append({
            'id': opp.id,
            'name': opp.name,
            'duration': opp.duration,
            'start_date': opp.start_date,
            'description': opp.description,
            'skills': opp.skills,
            'category': opp.category,
            'future_opportunities': opp.future_opportunities,
            'max_applicants': opp.max_applicants
        })

    return jsonify({'status': 'success', 'data': result})

@main.route('/opportunities', methods=['POST'])
@login_required
def create_opportunity():
    data = request.get_json()

    # REQUIRED FIELDS
    required_fields = [
        'name', 'duration', 'start_date',
        'description', 'skills',
        'category', 'future_opportunities'
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                'status': 'error',
                'error': f'{field} is required'
            })

    new_opp = Opportunity(
        user_id=current_user.id,
        name=data['name'],
        duration=data['duration'],
        start_date=data['start_date'],
        description=data['description'],
        skills=data['skills'],
        category=data['category'],
        future_opportunities=data['future_opportunities'],
        max_applicants=data.get('max_applicants')
    )

    db.session.add(new_opp)
    db.session.commit()

    return jsonify({'status': 'success'})

@main.route('/opportunities/<int:id>', methods=['GET'])
def get_opportunity(id):
    opp = Opportunity.query.get(id)

    if not opp:
        return jsonify({'status': 'error', 'error': 'Not found'})

    return jsonify({
        'status': 'success',
        'data': {
            'id': opp.id,
            'name': opp.name,
            'duration': opp.duration,
            'start_date': opp.start_date,
            'description': opp.description,
            'skills': opp.skills,
            'category': opp.category,
            'future_opportunities': opp.future_opportunities,
            'max_applicants': opp.max_applicants
        }
    })

@main.route('/opportunities/<int:id>', methods=['PUT'])
@login_required
def update_opportunity(id):
    data = request.get_json()

    opp = Opportunity.query.get(id)
    if not opp:
        return jsonify({'status': 'error', 'error': 'Not found'})

    # 🔐 ownership check (IMPORTANT)
    if opp.user_id != current_user.id:
        return jsonify({'status': 'error', 'error': 'Unauthorized'})

    opp.name = data.get('name')
    opp.duration = data.get('duration')
    opp.start_date = data.get('start_date')
    opp.description = data.get('description')
    opp.skills = data.get('skills')
    opp.category = data.get('category')
    opp.future_opportunities = data.get('future_opportunities')
    opp.max_applicants = data.get('max_applicants')

    db.session.commit()

    return jsonify({'status': 'success'})


@main.route('/opportunities/<int:id>', methods=['DELETE'])
@login_required
def delete_opportunity(id):
    opp = Opportunity.query.get(id)

    if not opp:
        return jsonify({'status': 'error', 'error': 'Not found'})

    # 🔐 ownership check (CRITICAL)
    if opp.user_id != current_user.id:
        return jsonify({'status': 'error', 'error': 'Unauthorized'})

    db.session.delete(opp)
    db.session.commit()

    return jsonify({'status': 'success'})