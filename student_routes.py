from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from .extensions import db
from .models import Application, PlacementDrive
from .utils import role_required, save_resume

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.route("/dashboard")
@role_required("student")
def dashboard():
    profile = current_user.student_profile
    approved_drives = (
        PlacementDrive.query.filter_by(status="Approved")
        .order_by(PlacementDrive.application_deadline.asc())
        .all()
    )
    applications = (
        Application.query.filter_by(student_id=profile.id)
        .order_by(Application.application_date.desc())
        .all()
    )
    applied_drive_ids = {application.drive_id for application in applications}
    history = [application for application in applications if application.status in {"Selected", "Rejected"}]

    return render_template(
        "student/dashboard.html",
        profile=profile,
        approved_drives=approved_drives,
        applications=applications,
        applied_drive_ids=applied_drive_ids,
        history=history,
    )


@student_bp.route("/profile", methods=["GET", "POST"])
@role_required("student")
def profile():
    profile = current_user.student_profile
    if request.method == "POST":
        try:
            profile.cgpa = float(request.form.get("cgpa", profile.cgpa))
            profile.graduation_year = int(request.form.get("graduation_year", profile.graduation_year))
        except ValueError:
            flash("Please enter valid academic details.", "danger")
            return redirect(url_for("student.profile"))

        profile.full_name = request.form.get("full_name", "").strip()
        profile.contact_number = request.form.get("contact_number", "").strip()
        profile.department = request.form.get("department", "").strip()
        profile.skills = request.form.get("skills", "").strip()

        uploaded_resume = request.files.get("resume")
        filename = save_resume(uploaded_resume)
        if filename:
            profile.resume_filename = filename

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("student.profile"))

    return render_template("student/profile.html", profile=profile)


@student_bp.route("/drive/<int:drive_id>/apply", methods=["POST"])
@role_required("student")
def apply_for_drive(drive_id):
    profile = current_user.student_profile
    drive = PlacementDrive.query.filter_by(id=drive_id, status="Approved").first_or_404()

    existing = Application.query.filter_by(student_id=profile.id, drive_id=drive.id).first()
    if existing:
        flash("You have already applied for this placement drive.", "warning")
        return redirect(url_for("student.dashboard"))

    application = Application(student=profile, drive=drive, status="Applied")
    db.session.add(application)
    db.session.commit()
    flash("Application submitted successfully.", "success")
    return redirect(url_for("student.dashboard"))