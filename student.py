from db_connect import cursor, conn
from flask import render_template, request, redirect
from flask import Blueprint
from account import is_user, error_info
student = Blueprint('student', __name__)


# 学生主页
@student.route('/index_student/account=<account>&user_no=<stu_number>/index/')
def index_student(account, stu_number):
    if not is_user(account):
        return error_info()
    return render_template('/student/index_student.html', account=account, stu_number=stu_number)


@student.route('/index_student/account=<account>&user_no=<stu_number>/info/', methods=['POST', 'GET'])
def info_student(account, stu_number):
    if not is_user(account):
        return error_info()
    if request.method == 'GET':
        sql = 'select stu_number, stu_name, col_name, major_name, stu_birth, stu_phone ' \
              'from student natural join major natural join college ' \
              'where stu_number = "%s"' % stu_number
        cursor.execute(sql)
        student = cursor.fetchone()
        print(student)
        return render_template('/student/info_student.html', student=student, account=account)

    else:
        submit = request.form.get('change')
        if submit == '电话':
            stu_phone = request.form.get('stu_phone')
            cursor.execute('update student '
                           'set stu_phone = "%s"'
                           'where account = "%s"' %
                           (stu_phone, account))
        elif submit == '密码':
            # 先比较旧密码是否正确
            old_pw = request.form.get('old_password')
            cursor.execute('select account, password '
                           'from userinfo '
                           'where account = "%s"' % account)
            real_pw = cursor.fetchone()[1]
            print("real_pw=" + str(real_pw))
            if old_pw != real_pw:
                return '<h>密码错误！</h>'

            new_pw = request.form.get('new_password')
            confirm = request.form.get('confirm')
            if new_pw != confirm:
                return '<h>请再确认新密码！</h>'
            print("验证通过")
            cursor.execute('update userinfo '
                           'set password = "%s"'
                           'where account = "%s"' %
                           (new_pw, account))
        conn.commit()
        return redirect('/index_student/account=%s&user_no=%s/info/' % (account, stu_number))


@student.route('/index_student/account=<account>&user_no=<stu_number>/course/', methods=['GET'])
def course_student(account, stu_number):
    if not is_user(account):
        return error_info()
    cursor.execute('select course.cour_number, course.cour_name, course.cour_score, student_course.grade '
                   'from student_course natural join course '
                   'where student_course.stu_number = "%s"' % stu_number)
    courses = cursor.fetchall()
    return render_template('/student/course_student.html', courses=courses, account=account)

