from flask import Flask
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager
from flask_cors import CORS

mysql = MySQL()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    mysql.init_app(app)
    jwt.init_app(app)
    CORS(app)

    from routes.auth import auth_bp
    from routes.attendance import attendance_bp
    from routes.admin import admin_bp
    from routes.tasks import tasks_bp
    from routes.export import export_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(export_bp, url_prefix='/api/export')

    @app.route('/')
    def index():
        return {"message": "Attendance System API is running"}

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
