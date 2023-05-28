from flask import render_template, Blueprint, flash, g, redirect, request, session, url_for

auth = Blueprint('auth', __name__, url_prefix='/auth')

from myblog.models.users import User
from werkzeug.security import check_password_hash, generate_password_hash
from myblog import db

#Registrar un usuario
@auth.route('/register', methods=('GET','POST'))
def register():
    if request.method == 'POST':
        username=request.form.get('username')
        password=request.form.get('password')

        user=User(username, generate_password_hash(password))
        error=None
        if not username:
            error='Se requiere nombre de usuario'
        elif not password:
            error='Se requiere contrasena'

        user_name=User.query.filter_by(username=username).first()
        if user_name==None:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        else:
            error=f'El usuario {username} ya esta registrado'
        flash(error)
    return render_template('auth/register.html')

    #Iniciar sesion
@auth.route('/login', methods=('GET','POST'))
def login():
    if request.method == 'POST':
        username=request.form.get('username')
        password=request.form.get('password')

        error=None

        user=User.query.filter_by(username=username).first()
        if user == None:
            error='Nombre de usuario incorrecto'
        elif not check_password_hash(user.password, password):
            error='La contrasena es incorrecta'

        if error is None:
            session.clear()
            session['user_id']=user.id
            return redirect(url_for('blog.index'))

        flash(error)
    return render_template('auth/login.html')

#Hacer seguimiento de la sesion de usuario
@auth.before_app_request
def load_logged_in_user():
    user_id=session.get('user_id')
    if user_id == None:
        g.user = None
    else:
        g.user = User.query.get_or_404(user_id)

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('blog.index'))

import functools

#Es necesario estar logueado para pasar algunas vistas
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            print('redirect auth.login')
            return redirect(url_for('auth.login'))
        print('autenticado')
        return view(**kwargs)
    return wrapped_view