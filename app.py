from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename
import math
# from flask_mail import Mail
app = Flask(__name__)
app.secret_key = 'the random string'

# app.config.update(
#     MAIL_SERVER= "smtp.gmail.com",
#     MAIL_PORT="465",
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME="#",
#     MAIL_PASSWORD="#"
# )
# mail=Mail(app)'''This is for auto mail send'''


with open("templates/config.json", 'r') as c:
    params = json.load(c)["params"]
app.config['UPLOAD_FOLDER'] = params["upload_location"]

local_server=True
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phno = db.Column(db.String(12), unique=True, nullable=False)
    msg = db.Column(db.String(120), unique=True, nullable=False)
    date = db.Column(db.String(12), unique=True, nullable=True)
# db.create_all()
class Home_post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    subtitle = db.Column(db.String(80), unique=False, nullable=False)
    slug = db.Column(db.String(21), unique=True, nullable=False)
    content = db.Column(db.String(12), unique=True, nullable=False)
    date = db.Column(db.String(12), unique=True, nullable=True)
    img_file = db.Column(db.String(12), unique=True, nullable=True)

@app.route('/')
def home():
    posts = Home_post.query.filter_by().all()[0:5]
    last = math.ceil(len(posts)/int(params['no_ofpost']))
    page=request.args.get('page')
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    posts=posts[(page-1)*int(params['no_ofpost']):(page-1)*int(params['no_ofpost'])+int(params['no_ofpost'])]
    if page==1:
        prev="#"
        next="/?page="+str(page+1)
    elif page==last:
        prev = "/?page="+str(page-1)
        next = "#"
    else:
        prev = "/?page="+str(page-1)
        next = "/?page="+str(page+1)
    return render_template('index.html',params=params,posts=posts,prev=prev,next=next)

@app.route('/login' ,methods=["GET","POST"])
def login():
    if ('user' in session and session ['user'] == params['admin_user']):
        posts=Home_post.query.all()
        return render_template('dashbord.html',params=params,posts=posts)
    if request.method == "POST":
        username=request.form.get('username')
        password=request.form.get('pass')
        if (username==params['admin_user'] and password==params['admin_pwd']):
            session['user']= username
            posts=Home_post.query.all()
            return render_template('dashbord.html',params=params,posts=posts)

    return render_template('login.html',params=params)

@app.route('/edit/<string:sno>' ,methods=["GET" ,"POST"])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == "POST":
            e_title = request.form.get('title')
            e_stitle = request.form.get('stitle')
            e_slug = request.form.get('slug')
            e_content = request.form.get('content')
            e_image = request.form.get('img')
            date = datetime.now()
            if sno == '0':
                post = Home_post(title=e_title,subtitle=e_stitle,slug=e_slug,content=e_content,date=date,img_file= e_image)
                db.session.add(post)
                db.session.commit()
            else:
                post = Home_post.query.filter_by(sno=sno).first()
                post.title=e_title
                post.subtitle=e_stitle
                post.slug=e_slug
                post.content=e_content
                post.image_file=e_image
                post.date=date
                db.session.commit()
                return redirect('/edit/+sno')
        post = Home_post.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,sno=sno,post=post)
@app.route('/upload' ,methods=["GET","POST"])
def upload ():
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method=="POST":
            f = request.files["fileToUpload"]
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "Uploaded Sucessfully"
@app.route('/delete/<string:sno>',methods=["GET","POST"])
def delete (sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Home_post.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/login')

@app.route('/homepost/<string:post_slug>',methods=['GET'])
def homepost(post_slug):
    post = Home_post.query.filter_by(slug=post_slug).first()
    return render_template('homepost.html',params=params,post=post)
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/login')



@app.route('/about')
def about():
    return render_template('about.html',params=params)

@app.route('/samplepost')
def samplepost():
    return render_template('post.html',params=params)

@app.route('/contact', methods=["GET","POST"])
def contact():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('msg')
        date = datetime.now()
        entry = Contact(name=name, email=email, phno=phone, msg=msg, date=date)
        db.session.add(entry)
        db.session.commit()
        # mail.send_message('new message send from'+name,sender=email,recipients="reciver mail",
        #                   body=msg+phone)

    return render_template('contact.html',params=params)

if __name__ == '__main__':
    app.run(debug=True)
