from db_connect import cursor, conn
from flask import render_template, request, redirect
from flask import Blueprint
from account import is_user, error_info
teacher = Blueprint('teacher', __name__)


# 教师主页
@teacher.route('/index_teacher/account=<account>&user_no=<teac_number>/index/')
def index_teacher(account, teac_number):
    if not is_user(account):
        return error_info()
    return render_template('/teacher/index_teacher.html', account=account, teac_number=teac_number)


@teacher.route('/index_teacher/account=<account>&user_no=<teac_number>/info/', methods=['POST', 'GET'])
def info_teacher(account, teac_number):
    if not is_user(account):
        return error_info()
    if request.method == 'GET':
        sql = 'select teac_number, teac_name, col_name, teac_mail, teac_office ' \
              'from teacher natural join college ' \
              'where teac_number = "%s"' % teac_number
        print(sql)
        cursor.execute(sql)
        teacher = cursor.fetchone()
        print(teacher)
        return render_template('/teacher/info_teacher.html', teacher=teacher, account=account)
    else:
        submit = request.form.get('change')
        if submit == '邮箱':
            teac_mail = request.form.get('teac_mail')
            cursor.execute('update teacher '
                           'set teac_mail = "%s"'
                           'where teac_number = "%s"' %
                           (teac_mail, teac_number))
        elif submit == '工作地点':
            teac_office = request.form.get('teac_office')
            cursor.execute('update teacher '
                           'set teac_office = "%s"'
                           'where teac_number = "%s"' %
                           (teac_office, teac_number))
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
        return redirect('/index_teacher/account=%s&user_no=%s/info/' % (account, teac_number))


@teacher.route('/index_teacher/account=<account>&user_no=<teac_number>/course/', methods=['GET'])
def course_teacher(account, teac_number):
    if not account or not is_user(account):
        return error_info()
    cursor.execute('select cour_number, cour_name '
                   'from teacher_course natural join course '
                   'where teac_number = "%s"' % teac_number)
    courses = cursor.fetchall()
    return render_template('/teacher/course_teacher.html', courses=courses, account=account, teac_number=teac_number)


@teacher.route('/index_teacher/account=<account>&user_no=<teac_number>/grade&cour_no=<cour_number>/', methods=['GET', 'POST'])
def course_grade(account, teac_number, cour_number):
    if not is_user(account):
        return error_info()
    sql = 'select stu_number, stu_name, grade ' \
          'from student natural join student_course natural join course ' \
          'where cour_number = "%s"' % cour_number
    print(sql)
    cursor.execute(sql)
    students = cursor.fetchall()
    if request.method == 'GET':
        sql2 = 'select cour_number, cour_name ' \
               'from course ' \
               'where cour_number = "%s"' % cour_number
        print(sql2)
        cursor.execute(sql2)
        course_info = cursor.fetchone()
        return render_template('/course/course_grade.html',
                               account=account,
                               students=students,
                               course=course_info,
                               teac_number=teac_number)
    else:
        for student in students:
            print(student[0])
            stu_grade = request.form.get(student[0])
            print("stu_grade = " + stu_grade)
            sql2 = 'update student_course ' \
                   'set grade = %d ' \
                   'where stu_number = "%s"' % (int(stu_grade), student[0])
            cursor.execute(sql2)
        conn.commit()
        return redirect('/index_teacher/account=%s&user_no=%s/grade&cour_no=%s/' %
                        (account, teac_number, cour_number))


