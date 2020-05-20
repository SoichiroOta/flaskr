# project/server/user/views.py


from flask import (
    render_template, Blueprint, url_for, redirect,
    flash, abort, request, jsonify, session
)
from flask_login import login_user, logout_user, login_required

from project.server import db
from project.server.models import User
from project.server.user.forms import LoginForm, RegisterForm


user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        session['user_id'] = user.id

        flash("Thank you for registering.", "success")
        return redirect(url_for("entry.show_entries"))

    return render_template("user/register.html", form=form)


@user_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user, authenticated = User.authenticate(
                db.session.query,
                form.email.data,
                form.password.data
            )
            if authenticated:
                login_user(user)
                session['user_id'] = user.id
                flash("You are logged in. Welcome!", "success")
                return redirect(url_for('entry.show_entries'))
            else:
                flash("Invalid email and/or password.", "danger")
                return render_template("user/login.html", form=form)
    return render_template("user/login.html", title="Please Login", form=form)


@user_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    flash("You were logged out. Bye!", "success")
    return redirect(url_for("main.home"))


@user_blueprint.route("/users/")
@login_required
def members():
    users = User.query.all()
    return render_template("user/members.html", users=users)


@user_blueprint.route('/users/<int:user_id>/')
@login_required
def detail(user_id):
    user = User.query.get(user_id)
    return render_template('user/detail.html', user=user)


@user_blueprint.route('/users/<int:user_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.password = request.form['password']
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user.detail', user_id=user_id))
    return render_template('user/edit.html', user=user)


@user_blueprint.route('/users/create/', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        user = User(name=request.form['name'],
                    email=request.form['email'],
                    password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user.members'))
    return render_template('user/edit.html')


@user_blueprint.route('/users/<int:user_id>/delete/', methods=['DELETE'])
@login_required
def delete(user_id):
    user = User.query.get(user_id)
    if user is None:
        response = jsonify({'status': 'Not Found'})
        response.status_code = 404
        return response
    db.session.delete(user)
    db.session.commit()
    return jsonify({'status': 'OK'})
