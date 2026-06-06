from flask import Blueprint, request, jsonify
from app import mysql

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/students', methods=['GET'])
def get_all_students():
    cur = mysql.connection.cursor()
    cur.execute('SELECT student_id, name, email, roll_number, created_at FROM students')
    students = cur.fetchall()
    cur.close()
    result = [{"student_id": s[0], "name": s[1], "email": s[2], "roll_number": s[3], "created_at": str(s[4])} for s in students]
    return jsonify({"students": result, "total": len(result)}), 200

@admin_bp.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM students WHERE student_id=%s', (student_id,))
    student = cur.fetchone()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    cur.execute('DELETE FROM attendance WHERE student_id=%s', (student_id,))
    cur.execute('DELETE FROM tasks WHERE student_id=%s', (student_id,))
    cur.execute('DELETE FROM students WHERE student_id=%s', (student_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Student deleted successfully"}), 200

@admin_bp.route('/attendance', methods=['GET'])
def get_all_attendance():
    month = request.args.get('month')
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    cur = mysql.connection.cursor()

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
    cur.close()
    result = [{"name": r[0], "roll_number": r[1], "date": str(r[2]), "status": r[3], "marked_at": str(r[4])} for r in records]
    return jsonify({"attendance": result, "total": len(result)}), 200

@admin_bp.route('/analytics', methods=['GET'])
def get_analytics():
    cur = mysql.connection.cursor()

    cur.execute('SELECT COUNT(*) FROM students')
    total_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM attendance WHERE status='Present'")
    total_present = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM attendance WHERE status='Absent'")
    total_absent = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM attendance WHERE status='Late'")
    total_late = cur.fetchone()[0]

    cur.execute("""SELECT s.name,
                   COUNT(a.attendance_id) as total,
                   SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) as present
                   FROM students s
                   LEFT JOIN attendance a ON s.student_id = a.student_id
                   GROUP BY s.student_id, s.name""")
    student_stats = cur.fetchall()
    cur.close()

    students_data = []
    for s in student_stats:
        total = s[1] or 0
        present = int(s[2] or 0)
        percentage = round((present / total * 100), 2) if total > 0 else 0
        students_data.append({
            "name": s[0],
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
