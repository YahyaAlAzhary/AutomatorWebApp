from datetime import timedelta

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, current_user, logout_user

from Automator.forms import NormalForm, CustomForm, LoginForm, RegisterForm, RequestForm
from joint import *
from Automator import *
from Automator.models import User


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
@login_required
def home_page():
    form = NormalForm()

    if form.validate_on_submit():
        selected_choices = []
        for field in form:
            if field.type == "BooleanField":
                selected_choices.append(field.label.text.lower())
        SavedInfo.set(form.sheet.data, selected_choices)
        result = mainjoint(SavedInfo.sheet, SavedInfo.users, "", Authentication.credentials,
                           Authentication.service, Authentication.drive_service, SavedEdits.edits)
        if result:
            if result[0] == "age":
                flash(["Invalid DOB, try running a custom lead with the corrected patdob"], category="danger")
            elif result[0] == "shoe":
                flash(["Missing shoe size, try running a custom lead with the corrected patdob"], category="danger")
        else:
            flash(["Done"], category="success")
        SavedInfo.clear()
        SavedEdits.clear()

    if form.errors != {} and form.is_submitted():
        for err_msg in form.errors.values():
            if err_msg.__contains__("CSRF"):
                render_template('home.html', form=form)
            else:
                flash(err_msg, category="danger")

    return render_template('home.html', form=form)


@app.route("/custom", methods=['GET', 'POST'])
@login_required
def custom_page():
    form = CustomForm()

    if form.validate_on_submit():
        if form.run.data:
            SavedInfo.set(form.sheet.data, [""])
            result = mainjoint(SavedInfo.sheet, SavedInfo.users, int(form.row.data), Authentication.credentials,
                               Authentication.service, Authentication.drive_service, SavedEdits.edits)
            if result:
                if result[0] == "age":
                    flash(["Invalid DOB, try running a custom lead with the corrected patdob"], category="danger")
                elif result[0] == "shoe":
                    flash(["Missing shoe size, try running a custom lead with the corrected patdob"], category="danger")
                else:
                    flash(["Done"], category="success")
                    SavedEdits.clear()
                    SavedInfo.clear()

    if form.is_submitted() and form.submitField.data:
        if not form.fields.data:
            flash(["Please choose a field to update"], category="danger")
        elif form.fieldUpdate.data.strip() == "":
            flash(["Please enter the value for the updated field"], category="danger")
        else:
            SavedEdits.addEdit(value=form.fieldUpdate.data.strip(), field=form.fields.data)

    if form.errors != {} and form.is_submitted():
        for err_msg in form.errors.values():
            flash(err_msg, category="danger")

    return render_template('custom.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            if attempted_user.confirmation == 'pending':
                flash(["Please wait for an admin to approve your registration"], category='primary')
            elif attempted_user.confirmation == 'rejected':
                flash(["Your account registration was rejected by the Admin"], category='danger')
            else:
                login_user(attempted_user, remember=False)
                flash([f"You are now logged in as {attempted_user.username}"], category="success")
                return redirect(url_for("home_page"))
        else:
            flash(["User and password do not match! Please try again"], category="danger")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout_page():
    logout_user()
    return redirect(url_for("login_page"))


@app.route("/inacitvelogout")
def inactivity_logout():
    if current_user.is_authenticated:
        logout_user()
        flash(["Session expired, please Log in again"], category="primary")
    return redirect(url_for("login_page"))


@app.route("/register", methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        newUser = User(username=form.username.data, password=form.password.data, confirmation="pending")
        db.session.add(newUser)
        db.session.commit()
        flash(["Please wait for an admin to approve your registration"], category="primary")
        return redirect(url_for("login_page"))

    if form.errors != {} and form.is_submitted():
        for err_msg in form.errors.values():
            flash(err_msg, category="danger")

    return render_template("register.html", form=form)


@app.route("/requests", methods=['GET', 'POST'])
@login_required
def request_page():
    if request.method == "GET" and request.args.get("admin"):
        if (not request.args.get("userCode") or request.args.get("userCode").strip() == "") and request.args.get(
                "reject") == "false":
            flash(["Please enter a User Code"], category="danger")
        else:
            id = request.args.get("user")
            user = User.query.get(id)

            if request.args.get("reject") == "false":
                user.confirmation = "accepted"
                if request.args.get("admin") == "true":
                    user.is_admin = True
                else:
                    user.is_admin = False
                user.userCode = request.args.get("userCode")
            else:
                user.confirmation = "rejected"
            db.session.commit()

    return render_template("requests.html", users=User)
