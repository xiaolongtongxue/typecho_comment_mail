# -*- coding: UTF-8 -*-
import subprocess

from mysql import connector
from mysql.connector import Error
import shlex
import os

MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_DATABASE = "{在这里输入使用的typecho的数据库名}"
MYSQL_USER = "{相应数据库使用的用户名}"
MYSQL_PASSWD = "{相应的用户密码}"
MYSQL_TABLE_FIRST = "typecho_"
SEND_FILE = os.path.dirname(os.path.abspath(__file__)) + "/for_mail.py"

MAIL_TITLE = "您在小龙同学的站点上的评论有新回复啦"

if __name__ == '__main__':
    table_comment = MYSQL_TABLE_FIRST + "comments"
    table_content = MYSQL_TABLE_FIRST + "contents"
    connection = connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWD,
        database=MYSQL_DATABASE
    )
    cursor = connection.cursor(prepared=True)
    try:
        send_dicts = []
        sql_get_send = "SELECT coid,mail," + MYSQL_TABLE_FIRST + "comments.cid,title," + MYSQL_TABLE_FIRST + \
                       "comments.parent,author," + MYSQL_TABLE_FIRST + "comments.text FROM " \
                       + MYSQL_TABLE_FIRST + "comments " "INNER JOIN " + MYSQL_TABLE_FIRST + \
                       "contents ON " + MYSQL_TABLE_FIRST + "comments.cid=" + MYSQL_TABLE_FIRST \
                       + "contents.cid WHERE ismailsend=0"
        cursor.execute(sql_get_send, ())
        unsend_mails = cursor.fetchall()
        for unsend_mail in unsend_mails:

            dict_ = {
                "child_coid": unsend_mail[0],
                "child_mail": unsend_mail[1],
                "cid": unsend_mail[2],
                "cname": unsend_mail[3],
                "parent_id": unsend_mail[4],
                "child_name": unsend_mail[5],
                "child_text": unsend_mail[6]
            }
            sql_type = "SELECT type,slug FROM " + MYSQL_TABLE_FIRST + "contents WHERE cid=?;"
            cid = unsend_mail[2]
            cursor.execute(sql_type, (cid,))
            type_ = cursor.fetchall()
            if type_[0][0] == "page":
                dict_['cid'] = type_[0][1]
            dict_['type'] = type_[0][0]
            if int(unsend_mail[4]) != 0:
                # 评论回复
                sql_parent = "SELECT mail,author,text FROM " + MYSQL_TABLE_FIRST + "comments WHERE coid=?;"
                cursor.execute(sql_parent, (unsend_mail[4],))
                receiver_mail = cursor.fetchall()
                if len(receiver_mail) > 0 and len(receiver_mail[0]) > 1:
                    dict_['receiver'] = receiver_mail[0][0]
                    dict_['parent_name'] = receiver_mail[0][1]
                    dict_['parent_text'] = receiver_mail[0][2]
                else:
                    dict_['receiver'] = False
            else:
                # 文章直接评论，回复给作者
                sql_author = "SELECT mail,name FROM " + MYSQL_TABLE_FIRST + \
                             "users WHERE uid=(SELECT authorId FROM " + \
                             MYSQL_TABLE_FIRST + "contents WHERE cid=?);"
                cursor.execute(sql_author, (cid,))
                author_mail = cursor.fetchall()
                if len(author_mail) > 0 and len(author_mail[0]) > 1:
                    dict_['receiver'] = author_mail[0][0]
                    dict_['parent_name'] = author_mail[0][1]
                    dict_['parent_text'] = "【系统提示：您是这篇文章的作者】"
                else:
                    dict_['receiver'] = False
            if dict_['receiver']:
                if dict_['child_mail'] == dict_['receiver']:
                    # 如果是自己回复自己的，就不发送邮件了
                    sql_update = "UPDATE `" + MYSQL_TABLE_FIRST + "comments` SET `ismailsend`=1 WHERE coid=?;"
                    cursor.execute(sql_update, (unsend_mail[0],))
                    connection.commit()
                    continue
                else:
                    send_dicts.append(dict_)
        # 接下来直接调用写好的脚本即可
        for send_dict in send_dicts:
            cmd = ['python3', shlex.quote(SEND_FILE),
                   '--receiver', shlex.quote(send_dict['receiver']),
                   '--cid', shlex.quote(str(send_dict['cid'])),
                   '--c_name', shlex.quote(send_dict['cname']),
                   '--parent_id', shlex.quote(str(send_dict['parent_id'])),
                   '--parent_name', shlex.quote(send_dict['parent_name']),
                   '--parent_text', shlex.quote(send_dict['parent_text']),
                   '--child_name', shlex.quote(send_dict['child_name']),
                   '--comment_id', shlex.quote(str(send_dict['child_coid'])),
                   '--text', shlex.quote(send_dict['child_text']),
                   '--title', shlex.quote(MAIL_TITLE),
                   '--type', shlex.quote(send_dict['type'])
                   ]
            for i in cmd:
                print(i, end=" ")
            res = subprocess.run(cmd, stdout=subprocess.PIPE)  # , stderr=subprocess.PIPE, text=True)
            if str(res.stdout) == "b'T'":
                sql_update = "UPDATE `" + MYSQL_TABLE_FIRST + "comments` SET `ismailsend`=1 WHERE coid=?;"
                # cursor.execute(sql_update, (send_dict['child_coid'],))
                # connection.commit()

            # print()
            # print()
            # print(res.stdout)
            # print("***********")
            # print(str(res.stdout) == "b'T'")
            # print(str(res.stdout) == "b'F'")
        """
        child_coid
        child_mail
        cid
        cname
        parent_id
        type
        receiver
        parent_name
        parent_text
        child_name
        child_text
        """
    except Error as error:
        print("error")
        print(error)
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

"""
当使用subprocess模块执行命令时，为了避免命令执行的远程代码执行（RCE）攻击，需要对参数进行适当的处理和过滤。以下是一个示例代码，演示了如何对参数进行处理以过滤特殊字符：
pythonCopy code
import subprocess
import shlex

def execute_command(command):
    # 对命令进行安全处理和过滤
    command = shlex.quote(command)
    
    # 执行命令
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    
    # 输出命令执行结果
    if output:
        print("命令输出：")
        print(output.decode())
    
    # 输出错误信息
    if error:
        print("错误信息：")
        print(error.decode())

# 示例调用
command = "ls -l /path/to/directory"
execute_command(command)
在上述代码中，我们使用了shlex.quote()函数来对命令参数进行安全处理和过滤。该函数会将参数转义，并确保参数中的特殊字符不被Shell解析。通过这种方式，可以防止特殊字符被误解为Shell命令的一部分，从而降低了命令执行的风险。
请注意，在使用该代码时，仍然需要谨慎处理用户输入的命令，以防止其他类型的攻击，如路径遍历等。建议对用户输入进行严格的验证和过滤，仅允许执行预定义的安全命令。
"""
