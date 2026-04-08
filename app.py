from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'twoj-mega-klucz-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modele bazy danych
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    # Przekazujemy 'view', aby plik HTML wiedział, co wyświetlić
    return render_template('index.html', view='feed', user=user, posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username'].strip()
        pwd = request.form['password']
        if User.query.filter_by(username=user).first():
            flash('Ta nazwa jest już zajęta!', 'error')
        else:
            new_user = User(username=user, password_hash=generate_password_hash(pwd))
            db.session.add(new_user)
            db.session.commit()
            flash('Konto stworzone! Zaloguj się.', 'success')
            return redirect(url_for('login'))
    return render_template('index.html', view='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        flash('Błędne dane logowania.', 'error')
    return render_template('index.html', view='login')

@app.route('/add_post', methods=['POST'])
def add_post():
    if 'user_id' in session:
        content = request.form.get('content')
        if content:
            db.session.add(Post(content=content, user_id=session['user_id']))
            db.session.commit()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Flask szuka folderu 'templates', więc go stworzymy jeśli nie istnieje
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True)
