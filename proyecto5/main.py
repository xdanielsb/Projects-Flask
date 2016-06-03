import sys
from flask import Flask, render_template, flash, request, url_for, redirect,session
from content_management import Content

from functools import wraps

from dbconect import connection
from wtforms import Form, TextField,validators,PasswordField, TextField ##pip install flask-WTF
from passlib.hash import sha256_crypt ##for encripting password -- pip  install passlib
from MySQLdb import escape_string as thuart ##Evita inyeccion de codigo
import gc

##Render template helps me to return the pages
##flash helps me to show message flashing

##Este codigo me sirve para ver donde estan las librerias de pyhton
##from distutils.sysconfig import get_python_lib
##print(get_python_lib())

TOPIC_DICT=Content()

app = Flask(__name__)
#this is a wrapper
@app.route('/')
def homepage():
    return render_template('main.html')


@app.route('/dashboard/')
def dashboard():
    try:
        return render_template('dashboard.html',TOPIC_DICT = TOPIC_DICT)
    except Exception as e:
        flash("This is the error")
        return render_template('500.html',error=e)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            ##I use args when I dont know how many parameters I going to pass to the function
            ## *args is a tuple of argumets
            ## **args is a dictionary of keywordarguments
            return f(*args, **kwargs)
        else:
            flash("You need to log in first")
            return redirect(url_for("dashboard"))
    return wrap

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been log out!")
    gc.collect()
    return redirect(url_for("login")) ##homepage is the name of the function


##Login
@app.route('/login/', methods = ['GET','POST'])
def login():
    error=""

    try:
        c, conn = connection()
        if request.method == "POST":
            data= c.execute("SELECT * FROM USERS where username=%s", thuart(request.form['username']))
            if int(data)==0: ##Si ese usuario no existe en la BD
                error= "Invalid Credentials, try again"
            else:
                data = c.fetchone()[6] ##Position of the Password in the database

            if(sha256_crypt.verify(request.form['password'],data )):
                session["logged_in"]=True
                session["username"]= request.form['username']
                flash("You are now logged in")
                return redirect(url_for("dashboard"))
            else:
                error= "Invalid Credentials, try again"
        gc.collect()
        return render_template('login.html',error=error)
    except Exception as e:
        #flash(e)
        return render_template('login.html',error=error)


class RegistrationForm(Form):
    ##For this part I user wtforms
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password',[validators.Required(),  validators.EqualTo('confirm', message='Passwords must match' )])
    confirm= PasswordField('confirm',[validators.Required()])

##Register
@app.route('/register/', methods = ['GET','POST'])
def register():
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username= form.username.data ##this username belongs to the class after created
            email= form.email.data ##This camp belongs to the class after created this class and called RegistrationForm
            password =sha256_crypt.encrypt(str(form.password.data))
            settings ="Default Settings"

            c,conn= connection()
            x= c.execute("SELECT * FROM USERS WHERE username= %s ", (thuart(username)))
            if int(x)>0: ##Si ese usuario ya existe en la BD
                flash("that username is already taken, please choose another username")
                return render_template('register.html',form=form)
            else:
                c.execute("INSERT INTO USERS (username,email,password, tracking) values (%s,%s,%s,%s )",(
                            thuart(username), thuart(email), thuart(password),thuart("/introduction-to-flask/") ))
                conn.commit()
                flash("Thanks for registering")
                c.close()
                conn.close()
                gc.collect()
                session["logged_in"]=True
                session["username"]= username
                return redirect (url_for("dashboard") )
        else:
            return render_template('register.html',form=form )
    except Exception as e:
        return str(e)


##ERROR HANDLER
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.errorhandler(405)
def page_not_found(e):
    return render_template('405.html')


if __name__=="__main__":
    app.secret_key = '879sd3$55cDS'
    app.run(debug=True)
