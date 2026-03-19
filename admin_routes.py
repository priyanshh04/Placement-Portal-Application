from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import or_

from .extensions import db
from .models import Application, CompanyProfile, PlacementDrive, StudentProfile, User
from .utils import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@role_required("admin")
def dashboard():
    student_query = request.args.get("student_query", "").strip()
    company_query = request.args.get("company_query", "").strip()

    students = StudentProfile.query
    companies = CompanyProfile.query

    if student_query:
        students = students.filter(
            or_(
                StudentProfile.full_name.ilike(f"%{student_query}%"),
                StudentProfile.roll_number.ilike(f"%{student_query}%"),
                StudentProfile.contact_number.ilike(f"%{student_query}%"),
            )
        )

    if company_query:
        companies = companies.filter(CompanyProfile.company_name.ilike(f"%{company_query}%"))

    stats = {
        "students": StudentProfile.query.count(),
        "companies": CompanyProfile.query.count(),
        "drives": PlacementDrive.query.count(),
        "applications": Application.query.count(),
    }

    pending_companies = CompanyProfile.query.filter_by(approval_status="Pending").all()
    pending_drives = PlacementDrive.query.filter_by(status="Pending").order_by(PlacementDrive.created_at.desc()).all()
    drives = PlacementDrive.query.order_by(PlacementDrive.created_at.desc()).all()
    applications = Application.query.order_by(Application.application_date.desc()).all()

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        students=students.order_by(StudentProfile.full_name.asc()).all(),
        companies=companies.order_by(CompanyProfile.company_name.asc()).all(),
        pending_companies=pending_companies,
        pending_drives=pending_drives,
        drives=drives,
        applications=applications,
        student_query=student_query,
        company_query=company_query,
    )


@admin_bp.route("/company/<int:company_id>/approval", methods=["POST"])
@role_required("admin")
def update_company_approval(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    action = request.form.get("action")
    company.approval_status = "Approved" if action == "approve" else "Rejected"
    db.session.commit()
    flash("Company approval status updated.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/drive/<int:drive_id>/approval", methods=["POST"])
@role_required("admin")
def update_drive_approval(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    action = request.form.get("action")
    drive.status = "Approved" if action == "approve" else "Rejected"
    db.session.commit()
    flash("Placement drive status updated.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/user/<int:user_id>/toggle-status", methods=["POST"])
@role_required("admin")
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        flash("Admin account cannot be deactivated here.", "warning")
        return redirect(url_for("admin.dashboard"))
    user.is_active_user = not user.is_active_user
    db.session.commit()
    flash("User active status updated.", "info")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/user/<int:user_id>/toggle-blacklist", methods=["POST"])
@role_required("admin")
def toggle_blacklist(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        flash("Admin account cannot be blacklisted.", "warning")
        return redirect(url_for("admin.dashboard"))
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    flash("User blacklist status updated.", "info")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/user/<int:user_id>/delete", methods=["POST"])
@role_required("admin")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        flash("Admin account cannot be deleted.", "warning")
        return redirect(url_for("admin.dashboard"))
    db.session.delete(user)
    db.session.commit()
    flash("User removed successfully.", "success")
    return redirect(url_for("admin.dashboard"))