from db_connect import cursor, conn
from flask import render_template, request, redirect
from flask import Blueprint
account = Blueprint('account', __name__)


def error_info():
    return redirect('/login&no_login')


def error_login():
    return redirect('/login&fail_login')


# 用户身份认证
def is_user(account):
    sql = 'select isOnline, ip ' \
          'from userinfo ' \
          'where account = "%s" ' % account
    cursor.execute(sql)
    user = cursor.fetchone()
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    # 如果没有账号或者账号不在线的话都要返回错误
    if not user or user[0] != 1 or user[1] != ip:
        return False
    else:
        return True


@account.route('/', methods=['GET'])  # 跳转至login.html，请求方式GET
@account.route('/login', methods=['GET'])
def show():
    return redirect('/login&normal')


@account.route('/login&<state>', methods=['POST', 'GET'])
def login(state):
    if request.method == 'GET':
        print(state)
        return render_template('/account/login.html', state=state)
    else:
        account = request.form['account']  # 界面传值
        password = request.form['password']  # 界面传值
        if len(account) == 0 | len(password) == 0:
            return redirect('/login&fail_login')

        cursor.execute('select account from userinfo')  # 查询test表查询用户名
        accounts = cursor.fetchall()

        for account in accounts:
            if request.form['account'] == account[0]:
                cursor.execute('select password, usertype from userinfo where account=%s', (account[0],))

                user = cursor.fetchone()  # 从useinfo表中获取密码

                if request.form['password'] == user[0]:  # 如果页面输入的password匹配test表返回的密码
                    # 标记当前登录状态
                    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
                    sql = 'update userinfo ' \
                          'set isOnline = true, ip = "%s" ' \
                          'where account = "%s"' % (ip, request.form['account'])
                    print(sql)
                    cursor.execute(sql)
                    conn.commit()
                    account_type = request.form['type']
                    if account_type == 'admin' and user[1] == 'admin':
                        return redirect('/index_admin/account=%s/index/' %
                                        (request.form['account']))
                    elif account_type == "student" and user[1] == 'student':
                        cursor.execute('select stu_number from student where account = "%s"' % account)
                        stu_number = cursor.fetchone()[0]
                        return redirect('/index_student/account=%s&user_no=%s/index/' %
                                        (request.form['account'], stu_number))
                    elif account_type == "teacher" and user[1] == 'teacher':
                        cursor.execute('select teac_number from teacher where account = "%s"' % account)
                        teac_number = cursor.fetchone()[0]
                        return redirect('/index_teacher/account=%s&user_no=%s/index/' %
                                        (request.form['account'], teac_number))
                    else:
                        return error_login()
                    # return '<h>欢迎回来,%s！</h>' % account[0]

                return error_login()

        cursor.close()  # 关闭游标
        conn.close()  # 关闭连接


@account.route('/logout/account=<account>', methods=['GET'])
def logout(account):
    sql = 'update userinfo ' \
          'set isOnline = false ' \
          'where account = "%s"' % account
    print(sql)
    cursor.execute(sql)
    conn.commit()
    return redirect('/login')


@account.route('/regist', methods=['POST', 'GET'])  # 表单提交
def regist():
    if request.method == 'GET':
        return render_template('/account/regist.html')
    else:
        account = request.form.get('account')
        pw = request.form.get('password')
        username = request.form.get('username')
        usertype = request.form.get('usertype')
        sql = 'insert into userinfo(account, password, username, usertype) ' \
              'values ("%s", "%s", "%s", "%s")' % \
              (account, pw, username, usertype)
        print(sql)
        cursor.execute(sql)

        # 如果是老师类型，插入teacher表中
        # 如果是学生类型，插入student表中
        if usertype == 'teacher':
            teac_name = request.form.get('teac_name')
            teac_number = request.form.get('teac_number')
            col_number = request.form.get('col_number')
            teac_mail = request.form.get('teac_mail')
            teac_office = request.form.get('teac_office')
            sql = 'insert into teacher(account, teac_name, teac_number, col_number, teac_mail, teac_office) ' \
                  'values ("%s", "%s", "%s", "%s", "%s", "%s")' % \
                  (account, teac_name, teac_number, col_number, teac_mail, teac_office)
            print(sql)
            cursor.execute(sql)
        else:
            stu_name = request.form.get('stu_name')
            stu_number = request.form.get('stu_number')
            major_number = request.form.get('major_number')
            stu_phone = request.form.get('stu_phone')
            stu_birth = request.form.get('stu_birth')
            sql = 'insert into student(account, stu_name, stu_number, major_number, stu_phone, stu_birth) ' \
                  'values ("%s", "%s", "%s", "%s", "%s", "%s")' % \
                  (account, stu_name, stu_number, major_number, stu_phone, stu_birth)
            cursor.execute(sql)
            # cursor.execute('insert into student(account, stu_name, stu_number, major_number, stu_phone, stu_birth) '
            #                'values ("%s", "%s", "%s", "%s", "%s", "%s")',
            #                (account, stu_name, stu_number, major_number, stu_phone, stu_birth))

        conn.commit()
        return redirect('/login&reg_ok')
