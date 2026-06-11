from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import pymysql
import pymysql.cursors

mysql_conn = None

def get_db():
    from flask import current_app, g
    if 'db' not in g:
        g.db = pymysql.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB'],
            port=int(current_app.config['MYSQL_PORT']),
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    jwt = JWTManager(app)
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

    @app.teardown_appcontext
    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    @app.route('/')
    def index():
        return {"message": "Attendance System API is running"}

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
