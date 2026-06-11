from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db
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
    db = get_db()
    with db.cursor() as cur:
        cur.execute('SELECT * FROM attendance WHERE student_id=%s AND date=%s',
                    (student_id, today))
        existing = cur.fetchone()

    if existing:
        return jsonify({"error": "Attendance already marked for today"}), 400

    with db.cursor() as cur:
        cur.execute('INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s)',
                    (student_id, today, status))
    db.commit()
    return jsonify({"message": f"Attendance marked as {status} for {today}"}), 201

@attendance_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    student_id = get_jwt_identity()
    db = get_db()
    with db.cursor() as cur:
        cur.execute('SELECT date, status, marked_at FROM attendance WHERE student_id=%s ORDER BY date DESC',
                    (student_id,))
        records = cur.fetchall()

    result = [{"date": str(r['date']), "status": r['status'], "marked_at": str(r['marked_at'])} for r in records]
    return jsonify({"history": result, "total_records": len(result)}), 200

@attendance_bp.route('/percentage', methods=['GET'])
@jwt_required()
def get_percentage():
    student_id = get_jwt_identity()
    month = request.args.get('month')
    if not month:
        month = date.today().strftime('%Y-%m')

    db = get_db()

    with db.cursor() as cur:
        cur.execute("""SELECT COUNT(*) as cnt FROM attendance
                       WHERE student_id=%s AND DATE_FORMAT(date,'%%Y-%%m')=%s""",
                    (student_id, month))
        total = cur.fetchone()['cnt']

    with db.cursor() as cur:
        cur.execute("""SELECT COUNT(*) as cnt FROM attendance
                       WHERE student_id=%s AND DATE_FORMAT(date,'%%Y-%%m')=%s
                       AND status='Present'""",
                    (student_id, month))
        present = cur.fetchone()['cnt']

    with db.cursor() as cur:
        cur.execute("""SELECT COUNT(*) as cnt FROM attendance
                       WHERE student_id=%s AND DATE_FORMAT(date,'%%Y-%%m')=%s
                       AND status='Late'""",
                    (student_id, month))
        late = cur.fetchone()['cnt']

    with db.cursor() as cur:
        cur.execute("""SELECT COUNT(*) as cnt FROM attendance
                       WHERE student_id=%s AND DATE_FORMAT(date,'%%Y-%%m')=%s
                       AND status='Absent'""",
                    (student_id, month))
        absent = cur.fetchone()['cnt']

    percentage = round((present / total * 100), 2) if total > 0 else 0

    return jsonify({
        "month": month,
        "total_days": total,
        "present": present,
        "late": late,
        "absent": absent,
        "percentage": percentage
    }), 200
