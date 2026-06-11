from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_task():
    student_id = get_jwt_identity()
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')

    if not title:
        return jsonify({"error": "Title is required"}), 400

    db = get_db()
    with db.cursor() as cur:
        cur.execute('INSERT INTO tasks (student_id, title, description) VALUES (%s, %s, %s)',
                    (student_id, title, description))
    db.commit()
    return jsonify({"message": "Task submitted successfully"}), 201

@tasks_bp.route('/my-tasks', methods=['GET'])
@jwt_required()
def get_my_tasks():
    student_id = get_jwt_identity()
    db = get_db()
    with db.cursor() as cur:
        cur.execute('SELECT task_id, title, description, submitted_at, status FROM tasks WHERE student_id=%s ORDER BY submitted_at DESC',
                    (student_id,))
        tasks = cur.fetchall()

    result = [{"task_id": t['task_id'], "title": t['title'], "description": t['description'],
               "submitted_at": str(t['submitted_at']), "status": t['status']} for t in tasks]
    return jsonify({"tasks": result, "total": len(result)}), 200

@tasks_bp.route('/admin/all', methods=['GET'])
def get_all_tasks():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""SELECT t.task_id, s.name, s.roll_number, t.title, t.description, t.submitted_at, t.status
                       FROM tasks t JOIN students s ON t.student_id = s.student_id
                       ORDER BY t.submitted_at DESC""")
        tasks = cur.fetchall()

    result = [{"task_id": t['task_id'], "student_name": t['name'], "roll_number": t['roll_number'],
               "title": t['title'], "description": t['description'],
               "submitted_at": str(t['submitted_at']), "status": t['status']} for t in tasks]
    return jsonify({"tasks": result, "total": len(result)}), 200

@tasks_bp.route('/admin/update/<int:task_id>', methods=['PATCH'])
def update_task_status(task_id):
    data = request.get_json()
    status = data.get('status')

    if status not in ['Pending', 'Reviewed', 'Approved']:
        return jsonify({"error": "Status must be Pending, Reviewed or Approved"}), 400

    db = get_db()
    with db.cursor() as cur:
        cur.execute('UPDATE tasks SET status=%s WHERE task_id=%s', (status, task_id))
    db.commit()
    return jsonify({"message": f"Task {task_id} updated to {status}"}), 200
