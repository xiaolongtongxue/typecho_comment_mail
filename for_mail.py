# -*- coding:utf-8 -*-
import argparse
import sys

POST_LINK_TYPE = "/archives/{cid}/"
PAGE_LINK_TYPE = "/{slug}.html"

SMTP_SERVER = "smtp.qq.com"  # SMTP Server
SMTP_PORT = 465
SMTP_KEY = "{请输入你的SMTP KEY}"
LOGIN_EMAIL = "{登录SMTP服务器使用的邮箱}"

HOST_ADDRESS = "https://blog.txk123.top"

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PASSWD = "{Redis的密码}"
REDIS_DBNUM = 15
CYCLE = 60
MAX_SEND = 5

parser = argparse.ArgumentParser(description='通过该脚本配置相应内容可发送邮件')
parser.add_argument("--smtp_server", type=str, help="使用的SMTP SERVER，如smtp.qq.com", default=SMTP_SERVER)
parser.add_argument('--smtp_port', type=str, help='SMTP服务器的服务端口', default=SMTP_PORT)
parser.add_argument('--smtp_key', type=str, help='SMTP服务器的SMTP KEY', default=SMTP_KEY)
parser.add_argument('--login_email', type=str, help='登录smtp key使用的邮箱', default=LOGIN_EMAIL)
parser.add_argument("--receiver", type=str, help="接收者的邮箱地址，必填！！", required=True)
parser.add_argument("--cid", type=str, help="相应文章的ID，必填！！", required=True)
parser.add_argument("--c_name", type=str, help="相应文章的文章名，必填！！", required=True)
parser.add_argument("--parent_id", type=str, help="上一级评论的评论的评论ID", required=True)
parser.add_argument("--parent_name", type=str, help="上一级评论的评论人用户名", required=True)
parser.add_argument("--parent_text", type=str, help="上一级评论的评论内容", required=True)
parser.add_argument("--child_name", type=str, help="回复的这一级评论的评论人用户名", required=True)
parser.add_argument("--comment_id", type=str, help="回复的这一级评论的ID", required=True)
parser.add_argument("--text", type=str, help="评论回复正文，必填！！", required=True)
parser.add_argument("--title", type=str, help="评论回复标题，必填！！", required=True)
parser.add_argument("--type", type=str, help="可查看_content数据表来查看相关属性，为post或page", default="page")


def send_email(smtp_server: str, smtp_port: int, smtp_key: str, login_email: str, receivers: list, text: str,
               title: str, child_name: str, sender_name='您在小龙同学的博客上的评论有回复啦'):
    """
    :param smtp_server: 使用的SMTP服务器
    :param smtp_port: SMTP服务器的相应端口
    :param smtp_key: SMTP Key相关内容
    :param login_email: 登录SMTP KEY使用的邮箱
    :param receivers: 接收者邮箱地址（列表形式，可以多个）
    :param text: 发送的正文内容
    :param title: 邮件的标题
    :param child_name: 回复你的邮件的人的ID
    :param sender_name: 表示你的邮件有人回复了，有一个醒目的作用
    :return:
    """
    import smtplib
    import email.utils
    from email.mime.text import MIMEText

    message = MIMEText(text.encode('utf-8', 'replace').decode('utf-8'), 'html')
    message['To'] = email.utils.formataddr((sender_name, receivers[0]))
    message['From'] = email.utils.formataddr((child_name, 'tian_onmyway@foxmail.com'))
    message['Subject'] = title
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(login_email, smtp_key)
    server.set_debuglevel(False)
    try:
        server.sendmail(login_email, receivers, msg=message.as_string())
        isSend = True
    except smtplib.SMTPException as e:
        print("Check_Send Sending Failure.The Error message is :: " + str(e))
        isSend = False
    finally:
        server.quit()
    return isSend


def get_text(data_: dict):
    import jinja2
    import os
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__)) + '/html'))
    template = env.get_template('index.html')
    document = template.render(data_)
    return document


def get_link(c_type_: str, cid_: str):
    if c_type_ == "post":
        if POST_LINK_TYPE == "/":
            return HOST_ADDRESS + "/index.php?id=" + cid_
        else:
            return HOST_ADDRESS + POST_LINK_TYPE.replace("{cid}", cid_)
    elif c_type_ == "page":
        if PAGE_LINK_TYPE == "/{slug}.html":
            return HOST_ADDRESS + PAGE_LINK_TYPE.replace("{slug}", cid_)
    else:
        return "e"


def un_bomb(receiver_: str):
    try:
        import redis
        connection = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        connection.auth(REDIS_PASSWD)
        connection.select(REDIS_DBNUM)
        if connection.get(receiver_) is None:
            connection.set(receiver_, 1)
            connection.expire(receiver_, CYCLE)
        else:
            connection.incr(receiver_)
            if int(connection.get(receiver_)) > MAX_SEND:
                return False
        return True
    except Exception as e:
        print(e)
        return False


def for_str(a: str):
    import html
    return html.escape(a[1: -1] if (a.startswith("'") and a.endswith("'")) else a)


if __name__ == '__main__':
    args = parser.parse_args()

    smtp_server, smtp_port, smtp_key, login_email = args.smtp_server, args.smtp_port, args.smtp_key, args.login_email
    receiver = args.receiver
    cid = args.cid
    c_name = args.c_name
    parent_id = args.parent_id
    parent_name = args.parent_name
    parent_text = args.parent_text
    child_name = args.child_name
    comment_id = args.comment_id
    comment_text = args.text
    title = args.title
    c_type = args.type

    if not un_bomb(receiver_=receiver):
        print("F", end="")
        sys.exit()

    data = {
        "title": for_str(title),
        "parent": for_str(parent_name),
        "link": for_str(get_link(c_type, cid)),
        "cname": for_str(c_name),
        "parent_text": for_str(parent_text),
        "child_name": for_str(child_name),
        "comment_text": for_str(comment_text),
        "comment_link": get_link(c_type, cid) + "/comment-page-1#comment-" + comment_id
    }
    text = get_text(data)
    res = send_email(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        smtp_key=smtp_key,
        login_email=login_email,
        receivers=[receiver],
        text=text,
        title=title,
        child_name=child_name,
    )
    if res:
        print("T", end="")
    else:
        print("F", end="")
