import time

from flask import render_template, redirect, url_for, flash, request, jsonify, session, Response
from flask_login import login_user, login_required, current_user, logout_user
from wtforms import BooleanField
from flask_socketio import emit, send
from asyncio import sleep, create_task, run

from Automator.forms import NormalForm, CustomForm, LoginForm, RegisterForm
from Automator import *
from Automator.models import User
from joint import *
from exceptions import *


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
@login_required
def home_page():
    SavedEdits.clear()
    sheet = request.args.get("sheet")
    users = request.args.get("users")
    if sheet is not None:
        if sheet == "":
            flash(["Please select a sheet"], category="danger")
            return redirect(url_for('home_page'))
        elif len(users) == 0:
            flash(["Please select at least one user"], category="danger")
            return redirect(url_for('home_page'))
        else:
            selectedUsers = []
            for id in users:
                selectedUsers.append(User.query.get(id).userCode)
            try:
                result = mainjoint(sheet, selectedUsers, "", Authentication.credentials, Authentication.service,
                          Authentication.drive_service, {})
            except Exception as e:
                flash(["An un expected error occured"], category="danger")
                print(e)
                return redirect(url_for('home_page'))

            if result[0] == "age":
                flash([f"The DOB format is wrong, {result[1]} in {result[2]} row={result[3]}. Try fixing it in the custom lead tab"], category="danger")
            elif result[0] == "shoe":
                flash([f"The Shoe Size is wrong / missing, {result[1]} in {result[2]} row={result[3]}. Try fixing it in the custom lead tab"], category="danger")
            elif result[0] == "lcode":
                flash([f"The LCode for {result[4]} is missing, {result[1]} in {result[2]} row={result[3]}. Try fixing it in the custom lead tab"], category="danger")
            elif result[0] == "mid":
                flash([f"The Medicare ID formate is invalid, {result[1]} in {result[2]} row={result[3]}. Try fixing it in the custom lead tab"], category="danger")
            elif result[0] == "state":
                flash([f"The State is invalid, {result[1]} in {result[2]} row={result[3]}. Try fixing it in the custom lead tab"], category="danger")
            elif result[0] == "zipcode":
                flash(["The Zipcode is invalid"])
            else:
                flash(["Done"], category="success")
            return redirect(url_for('home_page'))

    return render_template('home.html', User=User)


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
@login_required
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
                userCode = request.args.get("userCode")
                if User.query.filter_by(userCode=userCode).first():
                    flash(["User Code already in use, please choose a different one"], category="danger")
                else:
                    user.userCode = userCode
            else:
                user.confirmation = "rejected"
            db.session.commit()
        return redirect(url_for("request_page"))

    return render_template("requests.html", users=User)


@app.route("/users", methods=['GET', 'POST'])
@login_required
def users_page():
    if request.method == "GET" and request.args.get("admin"):
        id = request.args.get("user")
        user = User.query.get(id)
        print(id)
        if request.args.get("admin") == "true":
            user.is_admin = True
        else:
            user.is_admin = False

        if request.args.get("userCode") and request.args.get("userCode").strip() != "":
            userCode = request.args.get("userCode")
            if User.query.filter_by(userCode=userCode).first():
                flash(["User Code already in use, please choose a different one"], category="danger")
            else:
                user.userCode = userCode
        db.session.commit()
        return redirect(url_for("users_page"))

    elif request.method == "GET" and request.args.get("delete"):
        id = request.args.get("user")
        user = User.query.get(id)
        User.query.filter_by(id=id).delete()
        db.session.commit()
        return redirect(url_for("users_page"))

    return render_template("users.html", users=User)
