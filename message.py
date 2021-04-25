from db_connect import cursor, conn
from flask import render_template, request, redirect
import datetime
import sys
from flask import Blueprint
from account import is_user, error_info
message = Blueprint('message', __name__)


@message.route('/<usertype>/account=<account>&user_no=<user_no>/contact/', methods=['GET', 'POST'])
def account_contact(usertype, account, user_no):
    if not is_user(account):
        return error_info()
    if request.method == 'GET':
        sql = 'select mes_time, send_account, mes_content, mes_number, mes_isRead ' \
              'from message ' \
              'where receive_account = "%s" ' \
              'order by mes_time desc' % account
        print(sql)
        cursor.execute(sql)
        messages = cursor.fetchall()
        return render_template('/account/contact.html', messages=messages, account=account, user_no=user_no)
    else:
        receive_account = request.form.get('receive_account')
        mes_content = request.form.get('content')
        mes_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        mes_number = -1
        for i in range(sys.maxsize + 1):
            cursor.execute('select * from message where mes_number = %d' % i)
            ret = cursor.fetchone()
            if ret is None:
                mes_number = i
                break
        if mes_number < 0:
            return '信息太多，请联系管理员清理空间'
        sql = 'insert into message(mes_number, send_account, receive_account, mes_time, mes_content, mes_isRead) ' \
              'values (%d, "%s", "%s", "%s", "%s", "%s")' % \
              (mes_number, account, receive_account, mes_time, mes_content, "未读")
        print(sql)
        cursor.execute(sql)
        conn.commit()
        return redirect('/%s/account=%s&user_no=%s/contact/' % (usertype, account, user_no))


@message.route('/<usertype>/account=<account>&user_no=<user_no>/details&mes_number=<mes_number>/')
def message_details(usertype, account, user_no, mes_number):
    sql = 'select receive_account ' \
          'from message ' \
          'where mes_number = %d' % int(mes_number)
    print(sql)
    cursor.execute(sql)
    account = cursor.fetchone()
    if not account or not is_user(account[0]):
        return error_info()
    account = account[0]
    # 点击详情默认已读
    sql = 'update message ' \
          'set mes_isRead = "已读" ' \
          'where mes_number = "%s" ' % mes_number
    cursor.execute(sql)
    conn.commit()
    sql = 'select send_account, mes_time, mes_content ' \
          'from message ' \
          'where mes_number = "%s" ' % mes_number
    print(sql)
    cursor.execute(sql)
    details = cursor.fetchone()
    return render_template('/account/contact_details.html', account=account, details=details)


@message.route('/<usertype>/account=<account>&user_no=<user_no>/contact/confirm&mes_number=<mes_number>/')
def message_confirm(usertype, account, user_no, mes_number):
    if not is_user(account):
        return error_info()
    sql = 'update message ' \
          'set mes_isRead = "已读" ' \
          'where mes_number = "%s" ' % mes_number
    print(sql)
    cursor.execute(sql)
    conn.commit()
    return redirect('/%s/account=%s&user_no=%s/contact/' % (usertype, account, user_no))
