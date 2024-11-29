

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from .models import db, User, Professional, Customer, Service, ServiceRequest, Review, ROLE_ADMIN, ROLE_PROFESSIONAL, ROLE_CUSTOMER
from datetime import datetime
import os
from flask import Blueprint

main = Blueprint('main', __name__)

app = Flask(__name__, template_folder='app/templates')
login_manager = LoginManager(app)
login_manager.login_view = 'main.login'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper functions
def is_admin():
    return current_user.role == ROLE_ADMIN

def is_professional():
    return current_user.role == ROLE_PROFESSIONAL

def is_customer():
    return current_user.role == ROLE_CUSTOMER

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:  # Replace with hashed password check
            login_user(user)
            if user.role == ROLE_ADMIN:
                return redirect(url_for('admin_dashboard'))
            elif user.role == ROLE_PROFESSIONAL:
                return redirect(url_for('professional_dashboard'))
            elif user.role == ROLE_CUSTOMER:
                return redirect(url_for('customer_dashboard'))
        flash('Invalid credentials!', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Customer Signup
@app.route('/customer/signup', methods=['GET', 'POST'])
def customer_signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        fullname = request.form['fullname']
        address = request.form['address']
        pincode = request.form['pincode']

        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'danger')
            return redirect(url_for('customer_signup'))

        user = User(email=email, password=password, role=ROLE_CUSTOMER)
        db.session.add(user)
        db.session.commit()

        customer = Customer(user_id=user.id, fullname=fullname, address=address, pincode=pincode)
        db.session.add(customer)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('customerSignUp.html')

# Professional Signup
@app.route('/professional/signup', methods=['GET', 'POST'])
def professional_signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        fullname = request.form['fullname']
        service_name = request.form['serviceName']
        experience_years = request.form['experience']
        address = request.form['address']
        pincode = request.form['pincode']
        document = request.files['document']

        # Save uploaded document
        if document:
            filename = secure_filename(document.filename)
            document_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            document.save(document_path)

            user = User(email=email, password=password, role=ROLE_PROFESSIONAL)
            db.session.add(user)
            db.session.commit()

            professional = Professional(
                user_id=user.id,
                fullname=fullname,
                service_name=service_name,
                experience_years=experience_years,
                address=address,
                pincode=pincode,
                document_path=document_path
            )
            db.session.add(professional)
            db.session.commit()

            flash('Registration successful! Wait for admin approval.', 'success')
            return redirect(url_for('login'))
    return render_template('professionalSignUp.html')

# Admin Dashboard
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not is_admin():
        return redirect(url_for('login'))

    services = Service.query.all()
    professionals = Professional.query.all()
    service_requests = ServiceRequest.query.all()

    return render_template(
        'AdminDashboard.html',
        services=services,
        professionals=professionals,
        service_requests=service_requests
    )

@app.route('/admin/service/new', methods=['GET', 'POST'])
@login_required
def new_service():
    if not is_admin():
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        base_price = request.form['base_price']

        service = Service(name=name, description=description, base_price=base_price)
        db.session.add(service)
        db.session.commit()

        flash('Service added successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('newService.html')

# Professional Dashboard
@app.route('/professional/dashboard')
@login_required
def professional_dashboard():
    if not is_professional():
        return redirect(url_for('login'))

    today_services = ServiceRequest.query.filter_by(professional_id=current_user.professional.id, status='requested').all()
    closed_services = ServiceRequest.query.filter_by(professional_id=current_user.professional.id, status='closed').all()

    return render_template(
        'ProfessionalDashboard.html',
        today_services=today_services,
        closed_services=closed_services
    )

# Customer Dashboard
@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    if not is_customer():
        return redirect(url_for('login'))

    services = Service.query.all()
    service_history = ServiceRequest.query.filter_by(customer_id=current_user.customer.id).all()

    return render_template(
        'CustomerDashboard.html',
        services=services,
        service_history=service_history
    )

# Submit Rating
@app.route('/customer/rate', methods=['POST'])
@login_required
def submit_rating():
    if not is_customer():
        return redirect(url_for('login'))

    service_request_id = request.form['service_request_id']
    rating = int(request.form['rating'])
    comments = request.form['comments']

    review = Review(
        service_request_id=service_request_id,
        professional_id=ServiceRequest.query.get(service_request_id).professional_id,
        customer_id=current_user.customer.id,
        rating=rating,
        comments=comments
    )
    db.session.add(review)
    db.session.commit()

    flash('Rating submitted successfully.', 'success')
    return redirect(url_for('customer_dashboard'))
