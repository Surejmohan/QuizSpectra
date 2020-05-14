from flask import Flask,render_template,flash, redirect,url_for,session,logging,request,Response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm 



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'secret'


db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, autoincrement=True)
    Username = db.Column(db.String(50),unique=True, nullable=False,primary_key=True)
    Password = db.Column(db.String(15),nullable=False)
   
    def __init__(self,Username,Password):
        self.Username=Username
        self.Password=Password


class Other(db.Model):
    __tablename__ = 'Other'
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    Branch = db.Column(db.String(15))
    Semester = db.Column(db.String(15))
    Name = db.Column(db.String(25))
    Email = db.Column(db.String(30))
    Phone = db.Column(db.Integer)
    Score = db.Column(db.Integer)
    Username = db.Column(db.String, db.ForeignKey('User.Username'),nullable=False)
   
   
    def __init__(self,Username,Branch,Semester,Name,Email,Phone,Score):
        self.Branch=Branch
        self.Semester=Semester
        self.Name=Name
        self.Email=Email
        self.Phone=Phone
        self.Score=Score
        self.Username=Username
   
    
#Quiz Table
class Quiz(db.Model):
    __tablename__ = 'Quiz'
    Quest_No = db.Column(db.Integer, primary_key=True,autoincrement=True)
    Question = db.Column(db.String(80))
    Choice1 = db.Column(db.String(50))
    Choice2 = db.Column(db.String(50))
    Choice3 = db.Column(db.String(50))
    Choice4 = db.Column(db.String(50))
    Answer = db.Column(db.Integer)

    def __init__(self,Question,Choice1,Choice2,Choice3,Choice4,Answer):
        self.Question=Question
        self.Choice1=Choice1
        self.Choice2=Choice2
        self.Choice3=Choice3
        self.Choice4=Choice4
        self.Answer=Answer 


@app.route('/')
def index():
     return render_template('index.html')


@app.route('/register', methods=['POST'])
def Register():
    if request.method == 'POST':
        Username = request.form['username']
        Password = request.form['password']
        Confpassword = request.form['password2']
        Branch = request.form['branch']
        Semester = request.form['semester']
        Name = request.form['name']
        Email = request.form['email']
        Phone = request.form['phone']

        exists = User.query.filter_by(Username=Username).first()
        if not exists:
            exist = Other.query.filter_by(Email=Email).first()
            if not exist:
                if(Password == Confpassword):

                    user = User(Username=Username,Password=Password)
                    db.session.add(user)

                    other = Other(Branch=Branch,Semester=Semester,Name=Name,Email=Email,Phone=Phone,Username=Username,Score=-1)
                    db.session.add(other)

                    db.session.commit()
                    flash('You have Successfully Registered! please login ','success')
                    return redirect(url_for('index'))

                else:
                    flash('Password and Confirm password not matched','error')
                    return redirect(url_for('index'))
            else:
                flash('Email already taken,try something else ','error')
                return redirect(url_for('index'))
        
        else:
            
            flash('Username already taken,try something else','error')
            return redirect(url_for('index'))
        



@app.route("/user/login",methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        session.permanent = True       
        Username = request.form['username']
        Password = request.form['password']
        
        login = User.query.filter_by(Username=Username, Password=Password).first()

        if login:
            session["user"] = Username
            flash(Username +' Logged in','success')
            return redirect(url_for('Quiz_start'))

        elif Username == 'Admin' or Password == 'Administartor':
            session["admin"] = "Admin"
            flash('Admin Logged in','success')
            return redirect(url_for('Admindashboard'))
                
        else:
            flash('User is Not Registerd','error')
            return redirect(url_for('index'))


@app.route('/users/logout')
def Logout():
    session.clear()
    flash('Logged out','success')
    return redirect(url_for('index'))




@app.route('/quiz')
def Quiz_start():

    if "user" in session:
        User = session["user"]
        quiz = Quiz.query.filter_by(Quest_No = 1).first()
        if(quiz == None):
            session.clear()
            flash('Some thing has happend !You can take the Quiz after Sometime','error')
            return redirect(url_for('index'))
        user = Other.query.filter_by(Username = session["user"]).first()
        if(user.Score == -1):
            user.Score = 0
            db.session.add(user)
            db.session.commit()
            print(quiz)
            return render_template('quiz.html',User= User,quiz=quiz)
        else:
            session.clear()
            flash('You have  Completed Your Quiz! or Get Time Out','error')
        
            return redirect(url_for('index'))
    else:
        flash('Invalid Access','error')
        return redirect(url_for('index'))



@app.route('/quiz/next',methods=['POST'])
def Quiz_next():
    
    if "user" in session:
        User = session["user"]
        if request.method == 'POST':     
            questno = request.form['questno']
            ans = request.form['ans']

            print(ans)
            if(int(questno) == 10):
                session.clear()
                flash('You have Finished Your Quiz Successfully','success')
                return redirect(url_for('index'))
            check = Quiz.query.filter_by(Quest_No = questno).first()
            print(check.Answer)
            if(check.Answer == int(ans)):
                user = Other.query.filter_by(Username = session["user"]).first()
                user.Score = user.Score + 1
                db.session.add(user)
                db.session.commit()
            quiz = Quiz.query.filter_by(Quest_No = int(questno)+1).first()
            if(quiz == None):
                erro = Other.query.filter_by(Username = session["user"]).first()
                erro.Score = -1
                db.session.add(erro)
                db.session.commit()
                session.clear()
                flash('Some thing has happend !You can take the Quiz after Sometime','error')
                return redirect(url_for('index'))
            print(quiz)
            return render_template('quiz.html',User= User,quiz=quiz)
    else:
        flash('Invalid Access','error')
        return redirect(url_for('index'))



@app.route('/Admin')
def Admindashboard():
    if "admin" in session:
        User = session["admin"]
        return render_template('admin.html',User=User)
    else:
        flash('Invalid Access','error')
        return redirect(url_for('index'))



@app.route('/Admin/addquiz',methods=['GET', 'POST'])
def AddQuiz():
    if "admin" in session:
        if request.method == 'POST':
            Question = request.form['question']
            Choice1 = request.form['choice1']
            Choice2 = request.form['choice2']
            Choice3 = request.form['choice3']
            Choice4 = request.form['choice4']
            Answer = request.form['answer']

            quiz = Quiz(Question=Question,Choice1=Choice1,Choice2=Choice2,Choice3=Choice3,Choice4=Choice4,Answer=Answer)
            db.session.add(quiz)
            db.session.commit()

            flash('Quiz Added Successfully','success')
            return redirect(url_for('Admindashboard'))
    else:
        flash('Invalid Access','error')
        return redirect(url_for('index'))


    


if(__name__ == "__main__"):
    app.run(debug=True)