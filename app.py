from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretpsop'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///psop.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# MODELE
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='posts')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

# REJESTRACJA
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash("Użytkownik już istnieje!")
            return redirect(url_for('register'))
        db.session.add(User(username=username, password=generate_password_hash(password)))
        db.session.commit()
        flash("Rejestracja zakończona! Zaloguj się.")
        return redirect(url_for('login'))
    return render_template('index.html', page='register')

# LOGOWANIE
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash("Nieprawidłowy login lub hasło!")
    return render_template('index.html', page='login')

# WYLOGOWANIE
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# STRONA GŁÓWNA Z POSTAMI
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        content = request.form['content']
        if content:
            db.session.add(Post(content=content, user_id=current_user.id))
            db.session.commit()
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('index.html', page='home', posts=posts, current_user=current_user)

if __name__ == '__main__':
    app.run(debug=True)
