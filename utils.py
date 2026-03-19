import os
from functools import wraps

from flask import abort, current_app, flash, redirect, request, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login", next=request.url))
            if current_user.role not in roles:
                abort(403)
            if current_user.is_blacklisted or not current_user.is_active_user:
                flash("Your account is inactive. Please contact the placement cell.", "danger")
                return redirect(url_for("auth.logout"))
            return view_func(*args, **kwargs)

        return wrapper

    return decorator


def approved_company_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if current_user.company_profile.approval_status != "Approved":
            flash("Your company account is awaiting admin approval.", "warning")
            return redirect(url_for("company.dashboard"))
        return view_func(*args, **kwargs)

    return wrapper


def save_resume(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    filename = secure_filename(file_storage.filename)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file_storage.save(file_path)
    return filename