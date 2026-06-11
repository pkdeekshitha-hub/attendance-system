
   from flask import Blueprint, jsonify, send_file
from app import get_db
import pandas as pd
import io
from datetime import datetime

export_bp = Blueprint('export', __name__)

@export_bp.route('/attendance', methods=['GET'])
def export_attendance():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""SELECT s.name, s.roll_number, s.email, a.date, a.status, a.marked_at
                       FROM attendance a JOIN students s ON a.student_id = s.student_id
                       ORDER BY a.date DESC""")
        records = cur.fetchall()

    df = pd.DataFrame(records)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
    output.seek(0)

    filename = f'attendance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return send_file(output, download_name=filename, as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@export_bp.route('/attendance/<int:student_id>', methods=['GET'])
def export_student_attendance(student_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""SELECT s.name, s.roll_number, s.email, a.date, a.status, a.marked_at
                       FROM attendance a JOIN students s ON a.student_id = s.student_id
                       WHERE a.student_id = %s
                       ORDER BY a.date DESC""", (student_id,))
        records = cur.fetchall()

    with db.cursor() as cur:
        cur.execute('SELECT name FROM students WHERE student_id = %s', (student_id,))
        student = cur.fetchone()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    df = pd.DataFrame(records)

    total = len(df)
    present = len(df[df['status'] == 'Present']) if total > 0 else 0
    absent = len(df[df['status'] == 'Absent']) if total > 0 else 0
    late = len(df[df['status'] == 'Late']) if total > 0 else 0
    percentage = round((present / total * 100), 2) if total > 0 else 0

    summary = pd.DataFrame([{
        'Total Days': total,
        'Present': present,
        'Absent': absent,
        'Late': late,
        'Percentage': f'{percentage}%'
    }])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
        summary.to_excel(writer, index=False, sheet_name='Summary')
    output.seek(0)

    filename = f'{student["name"]}_attendance_{datetime.now().strftime("%Y%m%d")}.xlsx'
    return send_file(output, download_name=filename, as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@export_bp.route('/report', methods=['GET'])
def get_full_report():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""SELECT s.name, s.roll_number,
                       COUNT(a.attendance_id) as total,
                       SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) as present,
                       SUM(CASE WHEN a.status='Absent' THEN 1 ELSE 0 END) as absent,
                       SUM(CASE WHEN a.status='Late' THEN 1 ELSE 0 END) as late
                       FROM students s
                       LEFT JOIN attendance a ON s.student_id = a.student_id
                       GROUP BY s.student_id, s.name, s.roll_number""")
        records = cur.fetchall()

    result = []
    for r in records:
        total = r['total'] or 0
        present = int(r['present'] or 0)
        absent = int(r['absent'] or 0)
        late = int(r['late'] or 0)
        percentage = round((present / total * 100), 2) if total > 0 else 0
        result.append({
            "name": r['name'],
            "roll_number": r['roll_number'],
            "total_days": total,
            "present": present,
            "absent": absent,
            "late": late,
            "percentage": percentage
        })

    return jsonify({"report": result, "total_students": len(result)}), 200
