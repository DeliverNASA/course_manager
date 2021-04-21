import mysql.connector


conn = mysql.connector.connect(user="root",
                               password="mysql",
                               database="course_manager",
                               auth_plugin='mysql_native_password')  # 数据库连接
cursor = conn.cursor()
