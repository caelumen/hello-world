#-*- coding: utf-8 -*-

from flask import Flask, request, session, render_template, redirect, url_for,jsonify
import sqlite3
app = Flask(__name__)

@app.route('/')
def hello_world():
   return 'hello world!'

@app.route('/main')
def main():
   return 'Main Page'

@app.route('/user/<username>')
def showUserProfile(username):
   app.logger.debug('RETRIEVE DATA - USER ID: %s' % username)
   return 'USER : %s ' % username

@app.route('/user/id/<int:userId>')
def showUserProfileById(userId):
   return 'User ID: %d' % userId

@app.route('/account/login', methods=['POST'])
def login():
   if request.method == 'POST':
       userId = request.form['id']
       pw = request.form['pw']

       if len(userId) ==0 or len(pw) ==0 :
           return userId + ',' + pw + 'login failed !'

       session['logFlag'] = True
       session['userId'] = userId
       return session['userId'] + 'login !!'
   else:
       return 'illeagal Access !!'
app.secret_key = 'test_secret_key'

@app.route('/user', methods=['GET'])
def getUser():
   if session.get('logFlag') != True:
       return 'Access Denied !'
   userId = session['userId']
   return '[GET][USER] USER ID : {0}'.format(userId)

@app.route('/account/logout', methods=['POST','GET'])
def logout():
   session['logFlag'] = False
   session.pop('userId', None)
   return redirect(url_for('main'))


@app.route('/checkperm/<userid>/<cmd>')
def checkperm(userid, cmd):
    block_cmds = ['halt', 'shutdown', 'poweroff', 'init', 'reboot', 'fastboot', 'fasthalt', 'systemctl' ]


    if(cmd in block_cmds):
        return jsonify(userid=userid, cmd=cmd, permit=0)
    else:
        return jsonify(userid=userid, cmd=cmd, permit=1)




@app.route('/html')
def html():
   str = '''
   <html>
   <head>
   <title> TEST HTML Page </title>
   <script src="http://code.jquery.com/jquery-latest.js"></script>
   <script type="text/javascript">
   $(document).ready(function(){
       $("#content").css("background","yellow");
   })
   $("#btn_submit").onclick( function(){
       alert('');
   })
   </script>
   </head>
   <body>
   <form id=form_login method=POST action="/account/login">
   <div id='content'> 이부분은 로그인 정보를 입력합니다. </div>
   <div> ID : <input type=text name=id value=""> </div>
   <div> PW : <input type=text name=pw value=""> </div>
   <div> <input type=button value="login" id="btn_submit" > </div>
   </form>
   </body>
   <script type="text/javascript">
   //document.getElementById("btn_submit").onclick = function(){
   //     document.getElementById("form_login").submit();
   //}
   $("#btn_submit").click( function(){
       $("#form_login").submit();
   })
   </script>
   </html>
   '''
   return str

@app.errorhandler(400)
def uncaughtError(error):
   return '잘못된 사용입니다. '




if __name__=='__main__':
   app.debug = True
   app.run(host='127.0.0.1')

