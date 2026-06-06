from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mysql

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

    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO tasks (student_id, title, description) VALUES (%s, %s, %s)',
                (student_id, title, description))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Task submitted successfully"}), 201

@tasks_bp.route('/my-tasks', methods=['GET'])
@jwt_required()
def get_my_tasks():
    student_id = get_jwt_identity()
    cur = mysql.connection.cursor()
    cur.execute('SELECT task_id, title, description, submitted_at, status FROM tasks WHERE student_id=%s ORDER BY submitted_at DESC',
                (student_id,))
    tasks = cur.fetchall()
    cur.close()
    result = [{"task_id": t[0], "title": t[1], "description": t[2], "submitted_at": str(t[3]), "status": t[4]} for t in tasks]
    return jsonify({"tasks": result, "total": len(result)}), 200

@tasks_bp.route('/admin/all', methods=['GET'])
def get_all_tasks():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT t.task_id, s.name, s.roll_number, t.title, t.description, t.submitted_at, t.status
                   FROM tasks t JOIN students s ON t.student_id = s.student_id
                   ORDER BY t.submitted_at DESC""")
    tasks = cur.fetchall()
    cur.close()
    result = [{"task_id": t[0], "student_name": t[1], "roll_number": t[2], "title": t[3], "description": t[4], "submitted_at": str(t[5]), "status": t[6]} for t in tasks]
    return jsonify({"tasks": result, "total": len(result)}), 200

@tasks_bp.route('/admin/update/<int:task_id>', methods=['PATCH'])
def update_task_status(task_id):
    data = request.get_json()
    status = data.get('status')

    if status not in ['Pending', 'Reviewed', 'Approved']:
        return jsonify({"error": "Status must be Pending, Reviewed or Approved"}), 400

    cur = mysql.connection.cursor()
    cur.execute('UPDATE tasks SET status=%s WHERE task_id=%s', (status, task_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": f"Task {task_id} updated to {status}"}), 200
