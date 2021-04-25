from db_connect import cursor, conn
from flask import render_template, send_from_directory
import datetime, os
from flask import Blueprint
from account import is_user, error_info
resourse = Blueprint('resourse', __name__)


@resourse.route('/<usertype>/account=<account>&user_no=<user_no>/downloads/', methods=['GET'])
def account_downloads(usertype, account, user_no):
    if not is_user(account):
        return error_info()
    sql = 'select download.res_number, res_name, download_date ' \
          'from download, resource ' \
          'where download.res_number = resource.res_number ' \
          'and download.account = "%s" ' \
          'order by download_date desc' % account
    print(sql)
    cursor.execute(sql)
    downloads = cursor.fetchall()
    return render_template('/account/downloads.html', downloads=downloads, account=account)


@resourse.route('/<usertype>/account=<account>&user_no=<user_no>/resource&cour_no=<cour_number>/', methods=['GET', 'POST'])
def course_resource(usertype, account, user_no, cour_number):
    if not is_user(account):
        return error_info()
    cursor.execute('select resource.res_number, resource.res_name, resource.res_downloadCount, '
                   'userinfo.username, resource.res_uploaddate '
                   'from resource natural join course_resource natural join course natural join userinfo '
                   'where course.cour_number = "%s"' % cour_number)
    resources = cursor.fetchall()
    print(resources)
    cursor.execute('select cour_name '
                   'from course '
                   'where cour_number = "%s"' % cour_number)
    course = cursor.fetchone()[0]
    print(course)
    return render_template('/course/course_resource.html',
                           course=course,
                           cour_number=cour_number,
                           resources=resources,
                           account=account)


@resourse.route('/<usertype>/account=<account>&user_no=<user_no>/resource&cour_no=<cour_number>/'
                'download&res_no=<res_number>/', methods=['GET'])
def download(usertype, account, user_no, cour_number, res_number):
    if not is_user(account):
        return error_info()
    res_number = int(res_number)
    # 下载量计数
    sql = 'update resource ' \
          'set res_downloadCount = res_downloadCount + 1 ' \
          'where res_number = %d' % res_number
    print(sql)
    cursor.execute(sql)

    # 需要插入到下载表中（注意避免重复插入）
    today = datetime.date.today().strftime("%Y-%m-%d")
    sql3 = 'select account, res_number, download_date ' \
           'from download ' \
           'where account = "%s" and res_number = %d and download_date = "%s" ' % \
           (account, res_number, today)
    print(sql3)
    cursor.execute(sql3)
    if cursor.fetchone() is None:
        sql4 = 'insert into download(account, res_number, download_date) ' \
               'values("%s", %d, "%s") ' % (account, res_number, today)
        print(sql4)
        cursor.execute(sql4)
    conn.commit()

    # 下载资源
    sql2 = 'select res_name ' \
           'from resource ' \
           'where res_number = %d ' % res_number
    print(sql2)
    cursor.execute(sql2)
    res = cursor.fetchone()
    res_name = res[0]
    base_path = os.path.join(os.path.dirname(__file__), 'static\\uploads')
    res_path = os.path.join(base_path, '%s' % cour_number)
    return send_from_directory(res_path, res_name, as_attachment=True)
