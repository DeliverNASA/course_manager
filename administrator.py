from db_connect import cursor, conn
from flask import render_template, request, redirect
from flask import Blueprint
from account import is_user, error_info
from werkzeug.utils import secure_filename
import datetime
import sys
import os
admin = Blueprint('admin', __name__)


def error_info_admin():
    return redirect('/login&no_power')


# 管理员身份验证
def is_admin(account):
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    sql = 'select isOnline, ip ' \
          'from userinfo ' \
          'where account = "%s" and usertype = "admin"' % account
    print(sql)
    cursor.execute(sql)
    administrator = cursor.fetchone()
    print(administrator)
    if not administrator or administrator[0] != 1 or administrator[1] != ip:
        return False
    else:
        return True


@admin.route('/index_admin/account=<account>/index/', methods=['GET'])
def index_admin(account):
    if not is_admin(account):
        return error_info_admin()
    return render_template('/administrator/admin.html', account=account)


@admin.route('/index_admin/account=<account>/college/', methods=['POST', 'GET'])
def college(account):
    if not is_admin(account):
        return error_info_admin()
    if request.method == 'GET':
        cursor.execute("select * from college")
        colleges = cursor.fetchall()
        return render_template('/administrator/college.html', colleges=colleges, account=account)
    else:
        col_number = request.form.get('col_number')
        col_name = request.form.get('col_name')
        submit = request.form.get('confirm')
        if submit == '添加':
            print("添加")
            cursor.execute('insert into college(col_number, col_name) '
                           'values ("%s", "%s")' %
                           (col_number, col_name))
        elif submit == '更新':
            sql = 'update college ' \
                  'set col_name = "%s" ' \
                  'where col_number = "%s"' \
                  % (col_name, col_number)
            print(sql)
            cursor.execute(sql)
            # cursor.execute('update college '
            #                'set col_name = "%s" '
            #                'where col_number = "%s"' %
            #                (col_name, col_number))
        conn.commit()
        return redirect('/index_admin/account=%s/college/' % account)


@admin.route('/index_admin/account=<account>/college/delete_college/<id>/')
def delete_college(account, id):
    print(account)
    if not is_admin(account):
        return error_info_admin()
    cursor.execute('delete '
                   'from college '
                   'where college.col_number = %s' % id)
    conn.commit()
    return redirect('/index_admin/account=%s/college/' % account)


@admin.route('/index_admin/account=<account>/major&college=<col_name>/', methods=['POST', 'GET'])
def major(account, col_name):
    if not is_admin(account):
        return error_info_admin()
    cursor.execute('select col_number from college where col_name = "%s"' % col_name)
    col_number = cursor.fetchone()[0]
    if request.method == 'GET':
        cursor.execute('select * from major where col_number = "%s"' % col_number)
        majors = cursor.fetchall()
        return render_template('/administrator/major.html', col_name=col_name, majors=majors, account=account)
    else:
        major_number = request.form.get('major_number')
        major_name = request.form.get('major_name')
        submit = request.form.get('confirm')
        if submit == '添加':
            cursor.execute('insert into major(major_number, major_name, col_number) '
                           'values ("%s", "%s", "%s")' %
                           (major_number, major_name, col_number))
        elif submit == '更新':
            cursor.execute('update major '
                           'set major_name = "%s" '
                           'where major_number = "%s"' %
                           (major_name, major_number))
        conn.commit()
        return redirect('/index_admin/account=%s/major&college=%s/' % (account, col_name))


@admin.route('/index_admin/account=<account>/major&college=<col_name>/delete_major/<id>/')
def delete_major(account, col_name, id):
    if not is_admin(account):
        return error_info_admin()
    cursor.execute('delete '
                   'from major '
                   'where major.major_number = %s' % id)
    conn.commit()
    return redirect('/index_admin/account=%s/major&college=%s/' % (account, col_name))


@admin.route('/index_admin/account=<account>/course/', methods=['POST', 'GET'])
def course(account):
    if not is_admin(account):
        return error_info_admin()
    if request.method == 'GET':
        cursor.execute("select * from course")
        courses = cursor.fetchall()
        return render_template('/administrator/course.html', courses=courses, account=account)
    else:
        cour_number = request.form.get('cour_number')
        cour_name = request.form.get('cour_name')
        cour_score = int(request.form.get('cour_score'))
        submit = request.form.get('confirm')
        if submit == '添加':
            cursor.execute('insert into course(cour_number, cour_name, cour_score) '
                           'values ("%s", "%s", %d)' %
                           (cour_number, cour_name, cour_score))
        elif submit == '更新':
            cursor.execute('update course '
                           'set cour_name = "%s", cour_score = %d '
                           'where cour_number = "%s"' %
                           (cour_name, cour_score, cour_number))
        conn.commit()
        return redirect('/index_admin/account=%s/course/' % account)


@admin.route('/index_admin/account=<account>/course/delete_course/<id>/')
def delete_course(account, id):
    if not is_admin(account):
        return error_info_admin()
    cursor.execute('delete '
                   'from course '
                   'where course.cour_number = %s' % id)
    conn.commit()
    return redirect('/index_admin/account=%s/course/' % account)


@admin.route('/index_admin/account=<account>/resource/', methods=['GET'])
def resource(account):
    if not is_admin(account):
        return error_info_admin()
    sql = 'select res_number, res_name, res_downloadCount, Account, res_uploadDate ' \
          'from resource'
    print(sql)
    cursor.execute(sql)
    resources = cursor.fetchall()
    return render_template('/administrator/resource.html', resources=resources, account=account)


@admin.route('/index_admin/account=<account>/resource/delete_resource/<id>')
def delete_resource(account, id):
    if not is_admin(account):
        return error_info_admin()
    cursor.execute('delete '
                   'from resource '
                   'where resource.res_number = %d' % int(id))
    conn.commit()
    return redirect('/index_admin/account=%s/resource/' % account)


@admin.route('/index_admin/account=<account>/course/add_to_course/<cour_number>&<type>', methods=['POST'])
def add_to_course(account, cour_number, type):
    print(type)
    if not is_admin(account):
        return error_info_admin()
    print("课程添加")
    if type == 'teacher':
        teac_number = request.form.get('teac_number')
        sql = 'insert into teacher_course(cour_number, teac_number) ' \
              'values ("%s", "%s")' % \
              (cour_number, teac_number)
        cursor.execute(sql)
        conn.commit()
        return redirect('/index_admin/account=%s/course/' % account)
    elif type == 'student':
        stu_number = request.form.get('stu_number')
        sql = 'insert into student_course(cour_number, stu_number) ' \
              'values ("%s", "%s")' % \
              (cour_number, stu_number)
        print(sql)
        cursor.execute(sql)
        conn.commit()
        return redirect('/index_admin/account=%s/course/' % account)
    else:
        return '用户类型有误'


@admin.route('/<usertype>/account=<account>&user_no=<user_no>/resource&cour_no=<cour_number>/add_to_course/', methods=['POST'])
def add_resource_to_course(usertype, account, user_no, cour_number):
    if not is_user(account):
        return error_info
    print("进入resource管理")
    f = request.files['res_file']
    base_path = os.path.join(os.path.dirname(__file__), 'static\\uploads')
    # 判断存储目录是否存在，不存在则新建
    res_path = os.path.join(base_path, '%s' % cour_number)
    print(res_path)
    if not os.path.isdir(res_path):
        os.mkdir(base_path + "\\" + cour_number)
    res_name = secure_filename(f.filename)
    f.save(os.path.join(res_path, res_name))

    # 首先先在resource表中添加
    res_number = -1
    res_account = account
    res_uploaddate = datetime.datetime.today().strftime("%Y-%m-%d")
    for i in range(sys.maxsize + 1):
        cursor.execute('select * from resource where res_number = %d' % i)
        ret = cursor.fetchone()
        if ret is None:
            res_number = i
            break
    if res_number < 0:
        return '资源太多，请联系管理员清除部分不常用资源'
    sql = 'insert into resource(res_number, res_name, res_downloadCount, account, res_uploadDate) ' \
          'values (%d, "%s", 0, "%s", "%s")' % \
          (res_number, res_name, res_account, res_uploaddate)
    print(sql)
    cursor.execute(sql)
    # 其次在course_resource表中添加关联
    print("添加resource和course关联")
    sql2 = 'insert into course_resource(cour_number, res_number) ' \
           'values ("%s", %d)' % \
           (cour_number, res_number)
    print(sql2)
    cursor.execute(sql2)
    conn.commit()
    return redirect('/%s/account=%s&user_no=%s/resource&cour_no=%s/' % (usertype, account, user_no, cour_number))


