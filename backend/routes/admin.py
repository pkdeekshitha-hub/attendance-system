from flask import Blueprint, request, jsonify
from app import get_db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/students', methods=['GET'])
def get_all_students():
    db = get_db()
    with db.cursor() as cur:
        cur.execute('SELECT student_id, name, email, roll_number, created_at FROM students')
        students = cur.fetchall()

    result = [{"student_id": s['student_id'], "name": s['name'], "email": s['email'],
               "roll_number": s['roll_number'], "created_at": str(s['created_at'])} for s in students]
    return jsonify({"students": result, "total": len(result)}), 200

@admin_bp.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute('SELECT * FROM students WHERE student_id=%s', (student_id,))
        student = cur.fetchone()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    with db.cursor() as cur:
        cur.execute('DELETE FROM attendance WHERE student_id=%s', (student_id,))
        cur.execute('DELETE FROM tasks WHERE student_id=%s', (student_id,))
        cur.execute('DELETE FROM students WHERE student_id=%s', (student_id,))
    db.commit()
    return jsonify({"message": "Student deleted successfully"}), 200

@admin_bp.route('/attendance', methods=['GET'])
def get_all_attendance():
    month = request.args.get('month')
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    db = get_db()

    with db.cursor() as cur:
        if from_date and to_date:
            cur.execute("""SELECT s.name, s.roll_number, a.date, a.status, a.marked_at
                           FROM attendance a JOIN students s ON a.student_id = s.student_id
                           WHERE a.date BETWEEN %s AND %s
                           ORDER BY a.date DESC""", (from_date, to_date))
        elif month:
            cur.execute("""SELECT s.name, s.roll_number, a.date, a.status, a.marked_at
                           FROM attendance a JOIN students s ON a.student_id = s.student_id
                           WHERE DATE_FORMAT(a.date,'%%Y-%%m') = %s
                           ORDER BY a.date DESC""", (month,))
        else:
            cur.execute("""SELECT s.name, s.roll_number, a.date, a.status, a.marked_at
                           FROM attendance a JOIN students s ON a.student_id = s.student_id
                           ORDER BY a.date DESC""")
        records = cur.fetchall()

    result = [{"name": r['name'], "roll_number": r['roll_number'], "date": str(r['date']),
               "status": r['status'], "marked_at": str(r['marked_at'])} for r in records]
    return jsonify({"attendance": result, "total": len(result)}), 200

@admin_bp.route('/analytics', methods=['GET'])
def get_analytics():
    db = get_db()

    with db.cursor() as cur:
        cur.execute('SELECT COUNT(*) as cnt FROM students')
        total_students = cur.fetchone()['cnt']

    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) as cnt FROM attendance WHERE status='Present'")
        total_present = cur.fetchone()['cnt']

    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) as cnt FROM attendance WHERE status='Absent'")
        total_absent = cur.fetchone()['cnt']

    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) as cnt FROM attendance WHERE status='Late'")
        total_late = cur.fetchone()['cnt']

    with db.cursor() as cur:
        cur.execute("""SELECT s.name,
                       COUNT(a.attendance_id) as total,
                       SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) as present
                       FROM students s
                       LEFT JOIN attendance a ON s.student_id = a.student_id
                       GROUP BY s.student_id, s.name""")
        student_stats = cur.fetchall()

    students_data = []
    for s in student_stats:
        total = s['total'] or 0
        present = int(s['present'] or 0)
        percentage = round((present / total * 100), 2) if total > 0 else 0
        students_data.append({
            "name": s['name'],
            "total_days": total,
            "present": present,
            "percentage": percentage
        })

    return jsonify({
        "total_students": total_students,
        "total_present": total_present,
        "total_absent": total_absent,
        "total_late": total_late,
        "student_stats": students_data
    }), 200
