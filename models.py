from app import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

# User roles
ROLE_ADMIN = "admin"
ROLE_PROFESSIONAL = "professional"
ROLE_CUSTOMER = "customer"

# User Model
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Hashed password
    role = db.Column(db.String(50), nullable=False)  # admin/professional/customer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    professional = db.relationship('Professional', backref='user', uselist=False)
    customer = db.relationship('Customer', backref='user', uselist=False)

    def __repr__(self):
        return f"<User {self.email}, Role: {self.role}>"

# Professional Model
class Professional(db.Model):
    __tablename__ = 'professionals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fullname = db.Column(db.String(150), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    experience_years = db.Column(db.Integer, nullable=False)
    document_path = db.Column(db.String(200), nullable=False)  # Path to uploaded document
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    ratings = db.relationship('Review', backref='professional', lazy=True)

    def __repr__(self):
        return f"<Professional {self.fullname}, Service: {self.service_name}>"

# Customer Model
class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fullname = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<Customer {self.fullname}>"

# Service Model
class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    base_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Service {self.name}, Base Price: {self.base_price}>"

# Service Request Model
class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=True)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='requested')  # requested/accepted/closed

    customer = db.relationship('Customer', backref='service_requests')
    service = db.relationship('Service', backref='service_requests')
    professional = db.relationship('Professional', backref='service_requests')

    def __repr__(self):
        return f"<ServiceRequest {self.id}, Status: {self.status}>"

# Review Model
class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5 stars
    comments = db.Column(db.Text, nullable=True)

    service_request = db.relationship('ServiceRequest', backref='review')

    def __repr__(self):
        return f"<Review {self.id}, Rating: {self.rating}>"
