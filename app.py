from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)

# Configurations for session and database
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# if os.path.exists("users.db"):
#     os.remove("users.db")

# Initialize database and session
db = SQLAlchemy(app)
Session(app)

# -------------------------------
# MODELS
# -------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Certificate model
class Certificate(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    generated_by = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to user

    def __repr__(self):
        return f'<Certificate {self.id}>'

# -------------------------------
# ROUTES
# -------------------------------

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))

        return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/generate_certificate/<int:template_id>')
def generate_certificate(template_id):
    if 'username' not in session:
        return redirect(url_for('home'))

    if template_id == 1:
        return redirect(url_for('simple'))
    elif template_id == 2:
        return redirect(url_for('simpcert'))
    elif template_id == 3:
        return redirect(url_for('cert'))
    else:
        return "Template not found", 404

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/template')
def template():
    if 'username' not in session:
        return redirect(url_for('home'))

    templates = [
        {'id': 1, 'image_url': url_for('static', filename='images/template1.jpg')},
        {'id': 2, 'image_url': url_for('static', filename='images/template2.jpg')},
        {'id': 3, 'image_url': url_for('static', filename='images/template3.jpg')},
        {'id': 4, 'image_url': 'https://via.placeholder.com/300x200?text=Template+4'}
    ]
    return render_template('template.html', templates=templates)

@app.route('/simple')
def simple():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('simple.html')

@app.route('/simpcert')
def simpcert():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('simpcert.html')

@app.route('/cert')
def cert():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('cert.html')

@app.route('/features')
def features():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('features.html')

@app.route('/contact')
def contact():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('contact.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('signup.html', error_message='Email already exists. Please log in.')

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('signup.html')

# Save certificate from JS fetch call
@app.route('/save_certificate', methods=['POST'])
def save_certificate():
    data = request.get_json()

    cert_id = data.get('cert_id')
    name = f"{data.get('fname')} {data.get('lname')}"
    course = data.get('course')
    date = data.get('date')
    generated_by = session.get('username')
    user_id = session.get('user_id')

    if not all([cert_id, name, course, date, generated_by, user_id]):
        return jsonify({'success': False, 'message': 'Missing data'}), 400

    new_cert = Certificate(id=cert_id, name=name, course=course, date=date, generated_by=generated_by, user_id=user_id)
    db.session.add(new_cert)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Certificate saved successfully'})

# View certificates by logged-in user
@app.route('/certificates')
def view_certificates():
    if 'username' not in session:
        return redirect(url_for('home'))

    certs = Certificate.query.filter_by(user_id=session.get('user_id')).order_by(Certificate.date.desc()).all()
    return render_template('certificates.html', certificates=certs)

@app.before_request
def before_request():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)