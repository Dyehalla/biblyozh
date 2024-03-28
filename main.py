from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user

from data import db_session
from data.forms import LoginForm, RegisterForm
from data.models import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'biblyozh_must_be_completed_at_any_cost'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect("/")
        form.login.data = ''
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            form.login.data = ''
            return render_template('register.html',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.login.data).first():
            form.login.data = ''
            return render_template('register.html',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            login=form.login.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/db.db")
    app.run(debug=True)


if __name__ == '__main__':
    main()
