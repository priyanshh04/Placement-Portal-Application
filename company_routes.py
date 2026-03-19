from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .extensions import db
from .models import Application, CompanyProfile, PlacementDrive
from .utils import approved_company_required, role_required

company_bp = Blueprint("company", __name__, url_prefix="/company")


@company_bp.route("/dashboard", methods=["GET", "POST"])
@role_required("company")
def dashboard():
    company = request_company()

    if request.method == "POST":
        if company.approval_status != "Approved":
            flash("Only approved companies can create placement drives.", "warning")
            return redirect(url_for("company.dashboard"))

        try:
            deadline = datetime.strptime(request.form.get("application_deadline"), "%Y-%m-%d").date()
            openings = int(request.form.get("openings", "1"))
        except (TypeError, ValueError):
            flash("Please enter a valid deadline and openings count.", "danger")
            return redirect(url_for("company.dashboard"))

        drive = PlacementDrive(
            company=company,
            job_title=request.form.get("job_title", "").strip(),
            job_description=request.form.get("job_description", "").strip(),
            eligibility_criteria=request.form.get("eligibility_criteria", "").strip(),
            application_deadline=deadline,
            location=request.form.get("location", "").strip(),
            package_offered=request.form.get("package_offered", "").strip(),
            openings=openings,
            status="Pending",
        )
        db.session.add(drive)
        db.session.commit()
        flash("Placement drive created and sent for admin approval.", "success")
        return redirect(url_for("company.dashboard"))

    drives = (
        PlacementDrive.query.filter_by(company_id=company.id)
        .order_by(PlacementDrive.created_at.desc())
        .all()
    )
    applicant_counts = {drive.id: len(drive.applications) for drive in drives}
    return render_template(
        "company/dashboard.html",
        company=company,
        drives=drives,
        applicant_counts=applicant_counts,
    )


@company_bp.route("/profile", methods=["GET", "POST"])
@role_required("company")
def profile():
    company = request_company()

    if request.method == "POST":
        new_company_name = request.form.get("company_name", "").strip()
        existing_company = CompanyProfile.query.filter(
            CompanyProfile.company_name == new_company_name,
            CompanyProfile.id != company.id,
        ).first()
        if existing_company:
            flash("That company name is already in use.", "danger")
            return redirect(url_for("company.profile"))

        company.company_name = new_company_name
        company.hr_contact = request.form.get("hr_contact", "").strip()
        company.website = request.form.get("website", "").strip()
        company.description = request.form.get("description", "").strip()
        if company.approval_status == "Rejected":
            company.approval_status = "Pending"
        db.session.commit()
        flash("Company profile updated successfully.", "success")
        return redirect(url_for("company.profile"))

    return render_template("company/profile.html", company=company)


@company_bp.route("/drive/<int:drive_id>/edit", methods=["GET", "POST"])
@role_required("company")
@approved_company_required
def edit_drive(drive_id):
    company = request_company()
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()

    if request.method == "POST":
        try:
            drive.application_deadline = datetime.strptime(
                request.form.get("application_deadline"), "%Y-%m-%d"
            ).date()
            drive.openings = int(request.form.get("openings", "1"))
        except (TypeError, ValueError):
            flash("Please enter a valid deadline and openings count.", "danger")
            return redirect(url_for("company.edit_drive", drive_id=drive.id))

        drive.job_title = request.form.get("job_title", "").strip()
        drive.job_description = request.form.get("job_description", "").strip()
        drive.eligibility_criteria = request.form.get("eligibility_criteria", "").strip()
        drive.location = request.form.get("location", "").strip()
        drive.package_offered = request.form.get("package_offered", "").strip()
        if drive.status == "Rejected":
            drive.status = "Pending"
        db.session.commit()
        flash("Placement drive updated.", "success")
        return redirect(url_for("company.dashboard"))

    return render_template("company/edit_drive.html", drive=drive)


@company_bp.route("/drive/<int:drive_id>/close", methods=["POST"])
@role_required("company")
@approved_company_required
def close_drive(drive_id):
    company = request_company()
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()
    drive.status = "Closed"
    db.session.commit()
    flash("Placement drive closed.", "info")
    return redirect(url_for("company.dashboard"))


@company_bp.route("/drive/<int:drive_id>/delete", methods=["POST"])
@role_required("company")
@approved_company_required
def delete_drive(drive_id):
    company = request_company()
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()
    db.session.delete(drive)
    db.session.commit()
    flash("Placement drive deleted.", "info")
    return redirect(url_for("company.dashboard"))


@company_bp.route("/drive/<int:drive_id>/applications")
@role_required("company")
@approved_company_required
def drive_applications(drive_id):
    company = request_company()
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()
    applications = Application.query.filter_by(drive_id=drive.id).order_by(Application.application_date.desc()).all()
    return render_template("company/applications.html", drive=drive, applications=applications)


@company_bp.route("/application/<int:application_id>/status", methods=["POST"])
@role_required("company")
@approved_company_required
def update_application_status(application_id):
    application = Application.query.get_or_404(application_id)
    company = request_company()
    if application.drive.company_id != company.id:
        flash("You cannot update this application.", "danger")
        return redirect(url_for("company.dashboard"))

    application.status = request.form.get("status", "Applied")
    application.remarks = request.form.get("remarks", "").strip()
    db.session.commit()
    flash("Application status updated.", "success")
    return redirect(url_for("company.drive_applications", drive_id=application.drive_id))


def request_company():
    from flask_login import current_user

    return current_user.company_profile