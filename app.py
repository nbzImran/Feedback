from flask import Flask, redirect, render_template, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Base, engine, Feedback
from forms import RegisterForms, LoginForm, feedbackForm
from sqlalchemy.orm import sessionmaker
from flask import session as flask_session


# Initilize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Secret_key'

Base.metadata.create_all(engine)

# Set up Sqlalchemy session
Session = sessionmaker(bind=engine)
session = Session()


@app.route('/')
def home():
    return redirect(url_for('register'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForms()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            password=hashed_password,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
        )
        session.add(new_user)
        session.commit()
        flask_session['username'] = new_user.username #store the username
        flash('User registered Successfully!', 'Success')
        return redirect(url_for('user_profile', username=new_user.username))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = session.query(User).filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            flask_session['username'] = user.username # store the username
            flash('Login successful!', 'success')
            return redirect(url_for('user_profile', username=user.username))
        else:
            flash('Username and password do not match!', 'danger')

    return render_template('login.html', form=form)



@app.route('/logout')
def logout():
    flask_session.clear()
    flash("Logged out successfully.", 'success')
    return redirect(url_for('home'))

@app.route('/users/<username>')
def user_profile(username):
    if 'username' not in flask_session or flask_session['username'] != username:
        flash('Unauthrices acess!.', 'danger')
        return redirect(url_for('login'))
    user = session.query(User).filter_by(username=username).first()
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('home'))
    
    feedback = session.query(Feedback).filter_by(username=username).all()
    return render_template('user_profile.html', user=user, feedback=feedback)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    if 'username' not in flask_session or flask_session['username'] != username:
        flash('unauthorized action!', 'danger')
        return redirect(url_for('login'))
    
    user = session.query(User).filter_by(username=username).first()
    if user:
        session.delete(user)
        session.commit()
        session.clear()
        flash("User and all feedbakc deleted successfully.", "success")
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('home'))


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if 'username' not in flask_session or flask_session['username'] != username:
        flash('Unauthorized access!.', 'danger')
        return redirect(url_for('login'))
    
    form = feedbackForm()

    if form.validate_on_submit():
        new_feedback = Feedback(
            title=form.title.data,
            content=form.content.data,
            username=username
        )
        session.add(new_feedback)
        session.commit()
        flash('Feedback added.', 'success')
        return redirect(url_for('user_profile', username=username))
    return render_template('add_feedback.html', form=form)


@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    feedback = session.query(Feedback).get(feedback_id)
    if not feedback or feedback.username != flask_session.get('username'):
        flash("Unauthurized Access!", "danger")
        return redirect(url_for('login'))
    
    form = feedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        session.commit()
        flash("feedback Updated.", "success")
        return redirect(url_for('user_profile', username=feedback.username))
    return render_template('edit_feedback.html', form=form, feedback=feedback)

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = session.query(Feedback).get(feedback_id)
    if not feedback or feedback.username != flask_session.get('username'):
        flash('Unautherized action!', 'danger')
        return redirect(url_for('login'))
    
    session.delete(feedback)
    session.commit()
    flash('Feedback deleted!', 'success')
    return redirect(url_for('user_profile', username=feedback.username))



if __name__ == '__main__':
    app.run(debug=True)