#-*- coding: utf-8 -*-

from flask import Flask, request, session, render_template, redirect, url_for,jsonify
from datetime import datetime
import jinja2
import sqlite3
import os


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
          return ' Incorrect information about login  !'

      conn = sqlite3.connect("check_cmd.db")
      cur = conn.cursor()
      sql = "select uid,userid, name,pw from users where userid=?"
      #app.logger.debug("%s" % sql)
      #app.logger.debug("#%s#" % userId)
      #app.logger.debug("%s" % type(userId) )
      cur.execute(sql, (userId,) )
      rows = cur.fetchall()
      #app.logger.debug("#%s#" % len(rows))
      print(rows)
      print(rows[0])
      #db_uid, db_userid, db_username, db_pw, db_dept, db_manager = rows[0]
      db_uid, db_userid, db_name, db_pw = list(rows[0])
      print(db_uid,db_userid,db_name,db_pw)
      print("#{}#{}#{}#".format(type(db_pw),type(pw), db_pw is pw) )
      if(db_pw == pw):
          print(db_pw)
          session['logFlag'] = True
          session['userid'] = db_userid
          session['username'] = db_name
          session['uid'] = db_uid
          return session['username'] + '<br>' + 'login success !!'
      else:
          return "Login Failed !! "
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


@app.errorhandler(404)
def not_found(error):
  return "요청하신 페이지를 찾을 수 없습니다. "

@app.route('/check_cmd/<username>/<cmd>')
def check_cmd(username,cmd):
  if(session['logFlag']==True):
      requests = read_request(username)
  for req in requests:
      print(req)
  return requests[-1]

@app.route('/request_cmd/<username>/<cmd>')
def request_cmd(username,cmd):
  if(session['logFlag']==True):
      requests = save_request_cmd(username,cmd)
  for req in requests:
      print(req)
  return requests[-1]

@app.route('/save_cmd/<userid>/<cmd>/')
def save_cmd(userid,cmd):
  now = datetime.now()
  nowDate = now.strftime('%Y-%m-%d')
  nowTime = now.strftime('%H:%M:%S')
  reqTime = nowDate + ' ' + nowTime
  #with open("save_request.log","a") as f:
  #    f.write("{0}#{1}#{2}#{3}".format(nowDate, nowTime, username, cmd))

  conn = sqlite3.connect("check_cmd.db")
  cur = conn.cursor()
  sql = "insert into requests(time, uid, userid, cmd, bPermit) values(?, ? ,?,?,?)"
  cur.execute(sql, (reqTime , 1, userid, cmd, 0) )
  conn.commit()
  conn.close()

  re_str = "{0}: asking for execution of {1}".format(userid, cmd)
  return re_str


@app.route('/read_cmd/<userid>/')
def read_cmd(userid):
  conn = sqlite3.connect("check_cmd.db")
  cur = conn.cursor()
  sql = "select * from requests where userid=?"
  cur.execute(sql, (userid,))
  rows = cur.fetchall()

  result =[]
  re_str ="""<link rel="stylesheet" type="text/css" href="{}">
  <script src="http://code.jquery.com/jquery-latest.js"></script>
 <script type="text/javascript">
 $(document).ready(function(){
     $(".wrapper2").css("background","yellow");
 })
 </script>
 """
  for row in rows:
      print(row)
      result.append( list(row) )
      temp_str = ''.join([ "<p style='width:100px; border:1px'>"+str(x)+"</p>" for x in list(row)])
      re_str += "<div class='wrapper' >%s</div>" % ( temp_str )
  conn.close()

  re_str = "<html>" + re_str + "</html>"
  return re_str

@app.route("/test_template/")
def test_template():
   return render_template("~/test_bash/template/index.html")

def check_login(username):
  return 1

def sign_in_user(username,pw, department, manager_name):
  conn = sqlite3.connect("check_cmd.db")
  cur = conn.cursor()
  sql = "select * from users where username=?"
  cur.execute(sql,(username))
  rows = cur.fetchall()
  if(len(rows)>0):
      conn.close()
      return False
  else:
      sql = "insert into users(username, pw, department, manager_name) values (?,?,?,?)"
      cur.execute(sql, (username, pw, department, manager_name))
      conn.commit()
      conn.close()
  return True

def _create_init_tables(bDelete=True):
  sql = " CREATE TABLE users(uid INTEGER PRIMARY KEY AUTOINCREMENT, userid text, name text, pw text, department text, manager_name text) "
  sql2 = "INSERT INTO USERS(userid, name, pw, department, manager_name) VAlUES ('admin', 'Lee Sangjae', '123456', 'Security' , 'park') "
  sql3 = "select * from users"
  sql4 = " CREATE TABLE requests(req_id INTEGER PRIMARY KEY AUTOINCREMENT, time text, uid int, userid text, cmd text, bPermit int) "
  sql5 = "INSERT INTO requests(time, uid, userid, cmd, bPermit) values ('2018-04-15 09:30:00',1,'Lee Sangjae','TEST Command',0) "
  sql6 = "select * from requests"

  with open("test.txt","w+") as f:
      s = f.readline().strip()
      nCount =0
      if(len(s)!=0):
          nCount +=1
      f.write("%d" % (nCount+1) )

  if(os.path.isfile("check_cmd.db")):
      try:
          os.remove("check_cmd.db")
      except OSError as e:
          print(e)

  conn = sqlite3.connect("check_cmd.db")
  type(conn)

  with conn:
      cur = conn.cursor()
      cur.execute(sql)
      cur.execute(sql2)
      conn.commit()
      cur.execute(sql3)
      rows = cur.fetchall()
      print("USER TABLE:", rows)

      cur.execute(sql4)
      cur.execute(sql5)
      conn.commit()
      cur.execute(sql6)
      rows = cur.fetchall()
      print("Req Table:", rows)

  conn.close()
  return True


if __name__=='__main__':
  app.debug = True
  #_create_init_tables()
  app.run()


