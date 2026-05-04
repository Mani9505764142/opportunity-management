from flask import Flask, render_template
from flask_login import LoginManager
from models import db, User

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 🔥 IMPORTANT (must be inside function)
    from routes import main
    app.register_blueprint(main)

    return app   # ✅ THIS LINE IS CRITICAL


# 🔥 create app instance
app = create_app()


# ===== ROUTE =====
@app.route('/')
def home():
    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)