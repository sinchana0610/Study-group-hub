# app.py
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-change-this'   # change for production or use env var
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studyhub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# association table (many-to-many: users <-> groups)
membership = db.Table('membership',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('study_group.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_groups = db.relationship('StudyGroup', backref='creator', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class StudyGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)
    meeting_at = db.Column(db.DateTime, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    members = db.relationship('User', secondary=membership, backref=db.backref('groups', lazy='dynamic'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=60)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CreateGroupForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=120)])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=80)])
    date = StringField('Meeting Date', render_kw={"type":"date"})
    time = StringField('Meeting Time', render_kw={"type":"time"})
    description = TextAreaField('Description', validators=[Length(max=1000)])
    submit = SubmitField('Create Group')

# Routes
@app.route('/')
def index():
    groups = StudyGroup.query.order_by(StudyGroup.id.desc()).all()
    return render_template('index.html', groups=groups)

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter((User.username==form.username.data) | (User.email==form.email.data)).first():
            flash('Username or email already taken.', 'danger')
            return render_template('register.html', form=form)
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Registration successful. You are now logged in.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/create_group', methods=['GET','POST'])
@login_required
def create_group():
    form = CreateGroupForm()
    if form.validate_on_submit():
        meeting_at = None
        if form.date.data and form.time.data:
            try:
                meeting_at = datetime.datetime.fromisoformat(f"{form.date.data}T{form.time.data}")
            except Exception:
                meeting_at = None
        grp = StudyGroup(
            title=form.title.data,
            subject=form.subject.data,
            description=form.description.data,
            meeting_at=meeting_at,
            creator_id=current_user.id
        )
        grp.members.append(current_user)  # creator automatically joins
        db.session.add(grp)
        db.session.commit()
        flash('Study group created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_group.html', form=form)

@app.route('/group/<int:group_id>', methods=['GET','POST'])
def group_detail(group_id):
    grp = StudyGroup.query.get_or_404(group_id)
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('You must be logged in to join or leave groups.', 'warning')
            return redirect(url_for('login'))
        action = request.form.get('action')
        if action == 'join':
            if current_user not in grp.members:
                grp.members.append(current_user)
                db.session.commit()
                flash('You joined the group.', 'success')
        elif action == 'leave':
            if current_user in grp.members:
                grp.members.remove(current_user)
                db.session.commit()
                flash('You left the group.', 'info')
        return redirect(url_for('group_detail', group_id=group_id))
    return render_template('group.html', group=grp)

@app.route('/profile')
@login_required
def profile():
    created = current_user.created_groups
    joined = current_user.groups
    return render_template('profile.html', created=created, joined=joined)

if __name__ == '__main__':
    app.run(debug=True)
