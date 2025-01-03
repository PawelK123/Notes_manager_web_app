from flask import Flask,render_template,url_for,request,flash,redirect
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
import secrets
from datetime import datetime
from flask import session

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://root:y0NKPdQR38RKpAfx@localhost:3306/aplikacja'
app.config['SECRET_KEY'] = secrets.token_hex(16)
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('welcome.html')


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) 
    imie = db.Column(db.String(255), nullable=True) 

class Posty(db.Model):
    __tablename__ = 'posty'  # Określamy nazwę tabeli w bazie danych

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    users_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # Klucz obcy
    tytul = db.Column(db.String(255), nullable=False)
    data = db.Column(db.Date, nullable=False) # Bieżąca data
    tresc = db.Column(db.Text, nullable=False)

    # Relacja z tabelą Users (zakładając, że masz model User)
    user = db.relationship('Users', backref='posty', lazy=True)


@app.route('/notes',methods = ['GET','POST'])
def notes():
    if request.method == "GET":
        users_id = session['user_id']
        user_posts = Posty.query.filter_by(users_id=users_id).all()
        user = Users.query.get(session['user_id'])
        imie = user.imie
        return render_template('notes.html',posts = user_posts,imie = imie)
    else:
        users_id = session['user_id']
        tytul = request.form['title']
        tresc = request.form['tresc']
        data = datetime.now()
        new_post = Posty(tytul=tytul, tresc=tresc,data = data, users_id = users_id)
        db.session.add(new_post)
        db.session.commit()
        user_posts = Posty.query.filter_by(users_id=users_id).all()
        return render_template('notes.html', posts=user_posts)
    

@app.route('/delete',methods = ['POST'])
def delete():
    note_id = request.form['post_id']
    note = Posty.query.get(note_id)
    db.session.delete(note)
    db.session.commit()
    users_id = session['user_id']
    user = Users.query.get(session['user_id'])
    imie = user.imie
    user_posts = Posty.query.filter_by(users_id=users_id).all()
    return render_template('notes.html',posts = user_posts,imie= imie)


@app.route('/run_edit',methods = ['POST','GET'])
def run_edit():
    note_id = request.form['post_id']
    note = Posty.query.get(note_id)
    tytul = note.tytul
    tresc = note.tresc
    users_id = session['user_id']
    user = Users.query.get(session['user_id'])
    imie = user.imie
    user_posts = Posty.query.filter_by(users_id=users_id).all()
    return render_template('edit_note.html', tytul = tytul,tresc = tresc ,posts = user_posts,note_id = note_id, imie = imie)


@app.route('/edit',methods = ['POST'])
def edit():
    note_id = request.form['post_id']
    note = Posty.query.get(note_id)
    db.session.delete(note)
    users_id = session['user_id']
    user = Users.query.get(session['user_id'])
    imie = user.imie
    tytul = request.form['title']
    tresc = request.form['tresc']
    data = datetime.now()
    new_post = Posty(tytul=tytul, tresc=tresc,data = data, users_id = users_id)
    db.session.add(new_post)
    db.session.commit()
    user_posts = Posty.query.filter_by(users_id=users_id).all()
    return render_template('notes.html',posts = user_posts, imie = imie)

    
    


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            user = Users.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password,password):
                    flash("Zalogowano pomyślnie!",'success')
                    session['user_id'] = user.id
                    return redirect(url_for('notes',user_id = user.id))
                else:
                    flash("Podałeś nieprawidłowe hasło", 'danger')
                    return render_template('login.html')
            else:
                flash("Nie ma takiego emaila!", 'danger')
                return render_template('login.html')
            


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    else:
        imie = ""
        if 'email' in request.form and 'password' in request.form:
            password = request.form['password']
            email = request.form['email']
            hashed_password = generate_password_hash(password)
            imie = request.form['imie']
            new_user = Users(email=email, password=hashed_password,imie=imie)
            db.session.add(new_user)
            db.session.commit()  
            flash("Rejestracja zakończona sukcesem", 'success')
            return render_template('login.html')



if __name__ == '__main__':
    app.run(debug=True)