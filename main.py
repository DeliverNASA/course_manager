from flask import Flask
from account import account
from administrator import admin
from message import message
from resourse import resourse
from student import student
from teacher import teacher
from datetime import timedelta


app = Flask(__name__)  # 引入Flask
app.secret_key = 'zhuzhuxia'
app.send_file_max_age_default = timedelta(seconds=1)    # 设置文件下载的缓存时间
app.register_blueprint(account, url_prefix='/')
app.register_blueprint(admin, url_prefix='/')
app.register_blueprint(message, url_prefix='/')
app.register_blueprint(resourse, url_prefix='/')
app.register_blueprint(student, url_prefix='/')
app.register_blueprint(teacher, url_prefix='/')


if __name__ == '__main__':
    app.run()
