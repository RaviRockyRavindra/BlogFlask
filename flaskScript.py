import re
from flask import *
from flask_mysqldb import MySQL
import MySQLdb.cursors
import random
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
mysql = MySQL(app)

app.secret_key = '123456'  
app.config['MYSQL_HOST'] = '192.168.0.107'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'blogdb'
app.config['MAX_CONTENT-PATH']= '2048'
app.config['UPLOAD_IMAGE_FOLDER']= 'static\\uploads\\images'
app.config['UPLOAD_VIDEO_FOLDER']= 'static\\uploads\\videos'
app.config['UPLOAD_AUDIO_FOLDER']= 'static\\uploads\\audios'

class UserAccount():
    def set_password(self, passwordSecret):
        self.password = generate_password_hash(passwordSecret)
        return self.password

    def check_password(self, secret, password):
        return check_password_hash(secret, password)

class DataObject:
    def __init__(self,title,description,audio,video,image,username_list=[],blogid=[]):
        self.title = title
        self.description = description
        self.audio = audio
        self.video = video
        self.image = image
        self.username_list = username_list
        self.blogid = blogid

    def __repr__(self): 
        return "dataObject title:% s description:% s audio:% s video:% s image:% s username_list:% s" % (self.title, self.description, self.audio, self.video, self.image, self.username_list) 



@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(request.form['username'])
        if username and password:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE name = % s', (username, ))
            account = cursor.fetchone()
            ua = UserAccount()
            status = ua.check_password(account['password'],password)
            if account and status:
                session["id"] = account['id']
                session["username"] = request.form['username']
                sessionValue = True
                return redirect(url_for('indexPage', sessionValue=sessionValue, session = session))
            else:
                error = True
        return render_template('index.html', error = error)


@app.route('/logout',methods = ['POST'])
def logout():
    if 'username' in session:
        print(session)
        session.pop('username', None)
        return redirect(url_for('indexPage'))
    else:
        return redirect(url_for('indexPage'))

        

@app.route('/getMyBlogs', methods =['GET'])
@app.route('/getMyBlogs/<sessionValue>/<sessions>', methods =['GET'])
def getMyBlogs(sessionValue=None,sessions=None):
    if 'username' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        data = []
        cursor.execute('SELECT * FROM user_files WHERE user_id = % s',(session['id'],))
        dataResponse = cursor.fetchall()
        dataResponse = list(dataResponse)
        
        for count , each in enumerate(dataResponse):
            dataObject = DataObject(each['title'],each['description'],each['audioFilePath'],each['videoFilePath'],each['imageFilePath'],each['user_name'],each['sid'])
            data.append(dataObject)

        sessionValue = True
        selfAccount = True
        return render_template('index.html',dataObjects=data,sessionValue = sessionValue,session=session,selfAccount = selfAccount)

    else:
        return render_template('index.html')
             

@app.route('/', methods =['GET'])
@app.route('/<sessionValuee>/<sessions>', methods =['GET'])
def indexPage(sessionValuee=None,sessions=None):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    privacy = "public"
    cursor.execute('SELECT * FROM user_files WHERE privacy = % s',(privacy,))
    dataResponse = cursor.fetchall()
    dataResponse = list(dataResponse)
    user_id_list=[] 
    data=[]
    user_name_list=[]
    user_name_list2=[]
    # for ids in dataResponse:
    #     user_id_list.append(ids['user_id'])
    # print(user_id_list)    
    # format_strings = ','.join(['%s'] * len(user_id_list))  
    # cursor.execute("SELECT name from users WHERE id in (% s) " % format_strings,tuple(user_id_list))
    # user_name_response_tuple = cursor.fetchall()
    # user_name_response = list(user_name_response_tuple)

    # for each in user_name_response:
    #     user_name_list.append(each['name'])

    for count , each in enumerate(dataResponse):
        dataObject = DataObject(each['title'],each['description'],each['audioFilePath'],each['videoFilePath'],each['imageFilePath'],each['user_name'])
        data.append(dataObject)

    if 'username' in session:
        sessionValuee = True

    print(data)    

    return render_template('index.html', dataObjects=data, sessionValue = sessionValuee, session=sessions)


@app.route('/signup', methods =['GET', 'POST'])
def signup():
    return render_template('register.html')

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    user_id_list=[] 
    data=[]
    user_name_list=[]
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email'] 

        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
      # compiling regex
        pat = re.compile(reg)
        
        mat = re.search(pat, password)

        if mat:
            return render_template('register.html',msg = "passed")
        else:
            return render_template('register.html',msg = "Please ensure password must have [A-Z][a-z][0-9][extrasigns]")

        ua = UserAccount()
        password = ua.set_password(password)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE name = % s', (username, ))
        account = cursor.fetchone()
        
        if account:
            msg = 'Account already exists !' 

        else:
            cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (email, password, username, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            privacy = "public"
            cursor.execute('SELECT * FROM user_files WHERE privacy = % s',(privacy,))
            dataResponse = cursor.fetchall()
            dataResponse = list(dataResponse)
            
            # for ids in dataResponse:
            #     user_id_list.append(ids['user_id'])
            # format_strings = ','.join(['%s'] * len(user_id_list))  
            # cursor.execute("SELECT name from users WHERE id in (% s) " % format_strings,tuple(user_id_list))
            # user_name_response_tuple = cursor.fetchall()

            # for each in user_name_response_tuple:
            #     user_name_list.append(each['name'])

            for count , each in enumerate(dataResponse):
                dataObject = DataObject(each['title'],each['description'],each['audioFilePath'],each['videoFilePath'],each['imageFilePath'],each['name'])
                data.append(dataObject)

    return render_template('index.html', dataObjects=data, msg = msg)


@app.route('/upload', methods = ['POST', 'GET'])
def upload():
    if request.method == 'POST':
        if 'username' in session:

            title = request.form['title']
            description = request.form['subject']

            privacy = request.form['privacy']

            image = request.files['img']
            video = request.files['video']
            audio = request.files['audio']

            imageName = str(random.randint(100,1000)) + '.jpg' 
            videoName = str(random.randint(100,1000)) + '.mp4' 
            audioName = str(random.randint(100,1000)) + '.mp3'  

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO user_files VALUES (NULL,% s,% s,% s,% s,% s,% s,% s,% s)',(session['id'],session['username'],os.path.join(app.config['UPLOAD_AUDIO_FOLDER'],audioName),os.path.join(app.config['UPLOAD_VIDEO_FOLDER'],videoName),os.path.join(app.config['UPLOAD_IMAGE_FOLDER'],imageName),privacy,title,description))

            image.save(os.path.join(app.config['UPLOAD_IMAGE_FOLDER'],imageName))
            video.save(os.path.join(app.config['UPLOAD_VIDEO_FOLDER'],videoName))
            audio.save(os.path.join(app.config['UPLOAD_AUDIO_FOLDER'],audioName)) 

            mysql.connection.commit()


            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            privacy = "public"
            cursor.execute('SELECT * FROM user_files WHERE privacy = % s',(privacy,))
            dataResponse = cursor.fetchall()
            dataResponse = list(dataResponse)
            
            user_id_list=[] 
            data=[]
            user_name_list=[]
            # for ids in dataResponse:
            #     user_id_list.append(ids['user_id'])
            # format_strings = ','.join(['%s'] * len(user_id_list))  
            # cursor.execute("SELECT name from users WHERE id in (% s) " % format_strings,tuple(user_id_list))
            # user_name_response_tuple = cursor.fetchall()

            for each in dataResponse:
                dataObject = DataObject(each['title'],each['description'],each['audioFilePath'],each['videoFilePath'],each['imageFilePath'],each['user_name'])
                data.append(dataObject)

            sessionValue = True
            return render_template('index.html', dataObjects=data, sessionValue = sessionValue, session=session)

        else:
            return "session not exist please sign in !!"
        

@app.route('/deleteBlog/<blogid>', methods = ['POST', 'GET'])
def deleteBlog(blogid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    print(blogid)
    count = cursor.execute('Delete FROM user_files where sid = % s',(blogid,))
    print(count)
    return redirect(url_for('getMyBlogs'))


@app.route('/updateBlog', methods = ['POST', 'GET'])
def updateBlog():
    if request.method == 'POST':
        if 'username' in session:
            title = request.form['title']
            description = request.form['subject']
            blogidupdate = request.form['blogidupdate']
            print(blogidupdate)

            privacy = request.form['privacy']
            image = request.files['img']
            video = request.files['video']
            audio = request.files['audio']

            imageName = str(random.randint(100,1000)) + '.jpg' 
            videoName = str(random.randint(100,1000)) + '.mp4' 
            audioName = str(random.randint(100,1000)) + '.mp3'  

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE user_files set title = % s, description = % s,audioFilePath = % s, videoFilePath = % s,imageFilePath = % s,privacy = % s where sid = % s',(title,description,os.path.join(app.config['UPLOAD_AUDIO_FOLDER'],audioName),os.path.join(app.config['UPLOAD_VIDEO_FOLDER'],videoName),os.path.join(app.config['UPLOAD_IMAGE_FOLDER'],imageName),privacy,blogidupdate))


            image.save(os.path.join(app.config['UPLOAD_IMAGE_FOLDER'],imageName))
            video.save(os.path.join(app.config['UPLOAD_VIDEO_FOLDER'],videoName))
            audio.save(os.path.join(app.config['UPLOAD_AUDIO_FOLDER'],audioName)) 

            mysql.connection.commit()


            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            privacy = "public"
            cursor.execute('SELECT * FROM user_files WHERE privacy = % s',(privacy,))
            dataResponse = cursor.fetchall()
            dataResponse = list(dataResponse)
            
            user_id_list=[] 
            data=[]
            user_name_list=[]
            # for ids in dataResponse:
            #     user_id_list.append(ids['user_id'])
            # format_strings = ','.join(['%s'] * len(user_id_list))  
            # cursor.execute("SELECT name from users WHERE id in (% s) " % format_strings,tuple(user_id_list))
            # user_name_response_tuple = cursor.fetchall()

            for each in dataResponse:
                dataObject = DataObject(each['title'],each['description'],each['audioFilePath'],each['videoFilePath'],each['imageFilePath'],each['user_name'],each['sid'])
                data.append(dataObject)

            sessionValue = True
            return render_template('index.html', dataObjects=data, sessionValue = sessionValue, session=session)

        else:
            return "session not exist please sign in !!"        

if __name__ == '__main__':
    app.run(port=5000,threaded=True)