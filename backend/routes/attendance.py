from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mysql
from datetime import date

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/mark', methods=['POST'])
@jwt_required()
def mark_attendance():
    student_id = get_jwt_identity()
    data = request.get_json()
    status = data.get('status', 'Present')

    if status not in ['Present', 'Absent', 'Late']:
        return jsonify({"error": "Status must be Present, Absent or Late"}), 400

    today = date.today()
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM attendance WHERE student_id=%s AND date=%s',
                (student_id, today))
    existing = cur.fetchone()

    if existing:
        return jsonify({"error": "Attendance already marked for today"}), 400

    cur.execute('INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s)',
                (student_id, today, status))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": f"Attendance marked as {status} for {today}"}), 201

@attendance_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    student_id = get_jwt_identity()
    cur = mysql.connection.cursor()
    cur.execute('SELECT date, status, marked_at FROM attendance WHERE student_id=%s ORDER BY date DESC',
                (student_id,))
    records = cur.fetchall()
    cur.close()
    result = [{"date": str(r[0]), "status": r[1], "marked_at": str(r[2])} for r in records]
    return jsonify({"history": result, "total_records": len(result)}), 200

@attendance_bp.route('/percentage', methods=['GET'])
@jwt_required()
def get_percentage():
    student_id = get_jwt_identity()
    month = request.args.get('month')

    if not month:
        month = date.today().strftime('%Y-%m')

    cur = mysql.connection.cursor()
    cur.execute("""SELECT COUNT(*) FROM attendance
                   WHERE student_id=%s AND DATE_FORMAT(date,'%%Y-%%m')=%s""",
                (student_id, month))
    total = cur.fetchone()[0]

    cur.execute("""SELECT COUNT(*) FROM attendance
                   WHERE student_id=%s AND DATE_FORMAT(date,'%%Y-%%m')=%s
                   AND status='Present'""",
                (student_id, month))
    present = cur.fetchone()[0]

    cur.execute("""SELECT COUNT(*) FROM attendance
                   WHERE student_id=%s AND DATE_FORMAT(date,'%%Y-%%m')=%s
                   AND status='Late'""",
                (student_id, month))
    late = cur.fetchone()[0]

    cur.execute("""SELECT COUNT(*) FROM attendance
                   WHERE student_id=%s AND DATE_FORMAT(date,'%%Y-%%m')=%s
                   AND status='Absent'""",
                (student_id, month))
    absent = cur.fetchone()[0]

    percentage = round((present / total * 100), 2) if total > 0 else 0
    cur.close()

    return jsonify({
        "month": month,
        "total_days": total,
        "present": present,
        "late": late,
        "absent": absent,
        "percentage": percentage
    }), 200
