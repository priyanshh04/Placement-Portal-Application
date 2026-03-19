from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from .extensions import db
from .models import CompanyProfile, StudentProfile, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    return render_template("index.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user.role)

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        if user.is_blacklisted or not user.is_active_user:
            flash("Your account is blocked or inactive.", "danger")
            return render_template("auth/login.html")

        if user.role == "company" and user.company_profile.approval_status != "Approved":
            flash("Company login is allowed only after admin approval.", "warning")
            return render_template("auth/login.html")

        login_user(user)
        flash("Welcome back.", "success")
        return redirect_by_role(user.role)

    return render_template("auth/login.html")


@auth_bp.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        roll_number = request.form.get("roll_number", "").strip().upper()
        contact_number = request.form.get("contact_number", "").strip()
        department = request.form.get("department", "").strip()
        cgpa = request.form.get("cgpa", "0").strip()
        graduation_year = request.form.get("graduation_year", "0").strip()
        skills = request.form.get("skills", "").strip()

        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return render_template("auth/register_student.html")

        if StudentProfile.query.filter_by(roll_number=roll_number).first():
            flash("Roll number is already registered.", "danger")
            return render_template("auth/register_student.html")

        try:
            cgpa_value = float(cgpa)
            graduation_year_value = int(graduation_year)
        except ValueError:
            flash("Please enter valid academic details.", "danger")
            return render_template("auth/register_student.html")

        user = User(email=email, role="student")
        user.set_password(password)
        profile = StudentProfile(
            user=user,
            full_name=full_name,
            roll_number=roll_number,
            contact_number=contact_number,
            department=department,
            cgpa=cgpa_value,
            graduation_year=graduation_year_value,
            skills=skills,
        )
        db.session.add_all([user, profile])
        db.session.commit()
        flash("Student account created successfully. You can log in now.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register_student.html")


@auth_bp.route("/register/company", methods=["GET", "POST"])
def register_company():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        company_name = request.form.get("company_name", "").strip()
        hr_contact = request.form.get("hr_contact", "").strip()
        website = request.form.get("website", "").strip()
        description = request.form.get("description", "").strip()

        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return render_template("auth/register_company.html")

        if CompanyProfile.query.filter_by(company_name=company_name).first():
            flash("Company name is already registered.", "danger")
            return render_template("auth/register_company.html")

        user = User(email=email, role="company")
        user.set_password(password)
        profile = CompanyProfile(
            user=user,
            company_name=company_name,
            hr_contact=hr_contact,
            website=website,
            description=description,
            approval_status="Pending",
        )
        db.session.add_all([user, profile])
        db.session.commit()
        flash("Company registration submitted. Please wait for admin approval.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register_company.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


def redirect_by_role(role):
    if role == "admin":
        return redirect(url_for("admin.dashboard"))
    if role == "company":
        return redirect(url_for("company.dashboard"))
    return redirect(url_for("student.dashboard"))