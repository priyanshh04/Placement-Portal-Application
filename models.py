from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active_user = db.Column(db.Boolean, default=True, nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student_profile = db.relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    company_profile = db.relationship(
        "CompanyProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return self.is_active_user


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(80), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    skills = db.Column(db.Text)
    resume_filename = db.Column(db.String(255))

    user = db.relationship("User", back_populates="student_profile")
    applications = db.relationship(
        "Application",
        back_populates="student",
        cascade="all, delete-orphan",
    )


class CompanyProfile(db.Model):
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    company_name = db.Column(db.String(150), unique=True, nullable=False)
    hr_contact = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(200))
    description = db.Column(db.Text)
    approval_status = db.Column(db.String(20), default="Pending", nullable=False)

    user = db.relationship("User", back_populates="company_profile")
    drives = db.relationship(
        "PlacementDrive",
        back_populates="company",
        cascade="all, delete-orphan",
    )


class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profiles.id"), nullable=False)
    job_title = db.Column(db.String(120), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.Text, nullable=False)
    application_deadline = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(120))
    package_offered = db.Column(db.String(60))
    openings = db.Column(db.Integer, default=1, nullable=False)
    status = db.Column(db.String(20), default="Pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    company = db.relationship("CompanyProfile", back_populates="drives")
    applications = db.relationship(
        "Application",
        back_populates="drive",
        cascade="all, delete-orphan",
    )


class Application(db.Model):
    __tablename__ = "applications"
    __table_args__ = (
        db.UniqueConstraint("student_id", "drive_id", name="uq_student_drive_application"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default="Applied", nullable=False)
    remarks = db.Column(db.String(255))

    student = db.relationship("StudentProfile", back_populates="applications")
    drive = db.relationship("PlacementDrive", back_populates="applications")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))