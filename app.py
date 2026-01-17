from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, GameForm
from models import db, User, Game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    form: RegisterForm = RegisterForm()
    if form.validate_on_submit():
        existing_user: User | None = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already exists", "danger")
            return redirect(url_for("register"))
        new_user: User = User(
            username=form.username.data,
            password=generate_password_hash(form.password.data)
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("Account created successfully", "success")
        return redirect(url_for("home"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully", "success")
            return redirect(url_for("home"))
        flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for("home"))

@app.route("/")
def home():
    games = Game.query.all()
    return render_template("home.html", games=games)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_game():
    form = GameForm()
    if form.validate_on_submit():
        game = Game(
            title=form.title.data,
            genre=form.genre.data,
            description=form.description.data
        )
        db.session.add(game)
        db.session.commit()
        flash("Game added successfully", "success")
        return redirect(url_for("home"))
    return render_template("add_game.html", form=form)


@app.route("/game/<int:game_id>")
def game_detail(game_id):
    game = Game.query.get_or_404(game_id)
    return render_template("game_detail.html", game=game)

@app.route("/admin")
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    games = Game.query.all()
    return render_template("admin.html", games=games)


@app.route("/delete/<int:game_id>")
@login_required
def delete_game(game_id):
    if not current_user.is_admin:
        abort(403)
    game = Game.query.get_or_404(game_id)
    db.session.delete(game)
    db.session.commit()
    flash("Game deleted successfully", "success")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)