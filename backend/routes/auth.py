from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import bcrypt
from app import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    roll_number = data.get('roll_number')

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        db = get_db()
        with db.cursor() as cur:
            cur.execute('INSERT INTO students (name, email, password, roll_number) VALUES (%s, %s, %s, %s)',
                        (name, email, hashed.decode('utf-8'), roll_number))
        db.commit()
        return jsonify({"message": "Student registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    db = get_db()
    with db.cursor() as cur:
        cur.execute('SELECT * FROM students WHERE email = %s', (email,))
        student = cur.fetchone()

    if student and bcrypt.checkpw(password.encode('utf-8'), student['password'].encode('utf-8')):
        token = create_access_token(identity=str(student['student_id']))
        return jsonify({
            "token": token,
            "student_id": student['student_id'],
            "name": student['name'],
            "email": student['email'],
            "roll_number": student['roll_number']
        }), 200

    return jsonify({"error": "Invalid email or password"}), 401

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    db = get_db()
    with db.cursor() as cur:
        cur.execute('SELECT * FROM admins WHERE email = %s', (email,))
        admin = cur.fetchone()

    if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password'].encode('utf-8')):
        token = create_access_token(identity='admin_' + str(admin['admin_id']))
        return jsonify({
            "token": token,
            "admin_id": admin['admin_id'],
            "name": admin['name'],
            "role": "admin"
        }), 200

    return jsonify({"error": "Invalid admin credentials"}), 401

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    student_id = get_jwt_identity()
    db = get_db()
    with db.cursor() as cur:
        cur.execute('SELECT student_id, name, email, roll_number, created_at FROM students WHERE student_id=%s',
                    (student_id,))
        student = cur.fetchone()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({
        "student_id": student['student_id'],
        "name": student['name'],
        "email": student['email'],
        "roll_number": student['roll_number'],
        "created_at": str(student['created_at'])
    }), 200

@auth_bp.route('/profile/update', methods=['PUT'])
@jwt_required()
def update_profile():
    student_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')
    roll_number = data.get('roll_number')

    if not name:
        return jsonify({"error": "Name is required"}), 400

    db = get_db()
    with db.cursor() as cur:
        cur.execute('UPDATE students SET name=%s, roll_number=%s WHERE student_id=%s',
                    (name, roll_number, student_id))
    db.commit()
    return jsonify({"message": "Profile updated successfully"}), 200

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    student_id = get_jwt_identity()
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({"error": "Both old and new password required"}), 400

    db = get_db()
    with db.cursor() as cur:
        cur.execute('SELECT password FROM students WHERE student_id=%s', (student_id,))
        student = cur.fetchone()

    if not student or not bcrypt.checkpw(old_password.encode('utf-8'), student['password'].encode('utf-8')):
        return jsonify({"error": "Old password is incorrect"}), 401

    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    with db.cursor() as cur:
        cur.execute('UPDATE students SET password=%s WHERE student_id=%s',
                    (hashed.decode('utf-8'), student_id))
    db.commit()
    return jsonify({"message": "Password changed successfully"}), 200
