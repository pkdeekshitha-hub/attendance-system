from flask import Blueprint, jsonify, send_file
from app import mysql
import pandas as pd
import io
from datetime import datetime

export_bp = Blueprint('export', __name__)

@export_bp.route('/attendance', methods=['GET'])
def export_attendance():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT s.name, s.roll_number, s.email, a.date, a.status, a.marked_at
                   FROM attendance a JOIN students s ON a.student_id = s.student_id
                   ORDER BY a.date DESC""")
    records = cur.fetchall()
    cur.close()

    df = pd.DataFrame(records, columns=['Name', 'Roll Number', 'Email', 'Date', 'Status', 'Marked At'])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
    output.seek(0)

    filename = f'attendance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return send_file(output, download_name=filename, as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@export_bp.route('/attendance/<int:student_id>', methods=['GET'])
def export_student_attendance(student_id):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT s.name, s.roll_number, s.email, a.date, a.status, a.marked_at
                   FROM attendance a JOIN students s ON a.student_id = s.student_id
                   WHERE a.student_id = %s
                   ORDER BY a.date DESC""", (student_id,))
    records = cur.fetchall()

    cur.execute('SELECT name FROM students WHERE student_id = %s', (student_id,))
    student = cur.fetchone()
    cur.close()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    df = pd.DataFrame(records, columns=['Name', 'Roll Number', 'Email', 'Date', 'Status', 'Marked At'])

    total = len(df)
    present = len(df[df['Status'] == 'Present'])
    absent = len(df[df['Status'] == 'Absent'])
    late = len(df[df['Status'] == 'Late'])
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

    filename = f'{student[0]}_attendance_{datetime.now().strftime("%Y%m%d")}.xlsx'
    return send_file(output, download_name=filename, as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@export_bp.route('/report', methods=['GET'])
def get_full_report():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT s.name, s.roll_number,
                   COUNT(a.attendance_id) as total,
                   SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) as present,
                   SUM(CASE WHEN a.status='Absent' THEN 1 ELSE 0 END) as absent,
                   SUM(CASE WHEN a.status='Late' THEN 1 ELSE 0 END) as late
                   FROM students s
                   LEFT JOIN attendance a ON s.student_id = a.student_id
                   GROUP BY s.student_id, s.name, s.roll_number""")
    records = cur.fetchall()
    cur.close()

    result = []
    for r in records:
        total = r[2] or 0
        present = r[3] or 0
        absent = r[4] or 0
        late = r[5] or 0
        percentage = round((present / total * 100), 2) if total > 0 else 0
        result.append({
            "name": r[0],
            "roll_number": r[1],
            "total_days": total,
            "present": present,
            "absent": absent,
            "late": late,
            "percentage": percentage
        })

    return jsonify({"report": result, "total_students": len(result)}), 200
