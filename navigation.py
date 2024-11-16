from flask import Blueprint, render_template, session, url_for, redirect, flash
from forms import LoginForm, InsertUser, RegisterForm



navigation = Blueprint('access', __name__)


@navigation.route('/')
def home():
    login_form = LoginForm()
    return render_template('index.html', form=login_form)

@navigation.route('/homepage')
def homepage():
    if not session.get('logged_in'):  # Verifica se l'utente è autenticato
        flash('Devi effettuare il login per accedere a questa pagina.')
        return render_template('index.html', form=LoginForm())
    return render_template('homepage.html')

@navigation.route('/view_add_user', methods=['GET'])
def view_add_user():
    insert_form = InsertUser()
    return render_template('add_user.html', form=insert_form)

@navigation.route('/view_register_user', methods=['GET'])
def view_register():
    register_form = RegisterForm()
    return render_template('register_user.html', form=register_form)