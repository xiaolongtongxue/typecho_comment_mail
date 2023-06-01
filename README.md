# Typecho Commit mail

对于个人博客来说，评论回复很难被人关注到永远是个人博客需要注意的一个点。在之前博客采用的 cms 还是 typecho 的时候（当然现在不是了，直接跳罐子的请自我反思一下），尝试过采用 CommentToMail 插件 来进行评论邮件的操作，但是几经调试觉得是真的难用。于是就：

![0.0](/xiaolongtongxue/typecho_comment_mail/images/image-20230601205949008.png)

最近为了解决这个问题，这边更换了一种思路。头一阵子在对 XL-Sec（[详情链接](/archives/122/)）的用户模块进行研发的时候，发现 python 的 PyEmail 相关类库是真的好用！！

# PyEmail库的使用

## 安装方法

```bash
pip3 install PyEmail
```

## 程序案例

可以修改下边的程序来使用

```python
# -*- coding: utf-8 -*-
import smtplib
import email.utils
from email.mime.text import MIMEText

message = MIMEText("我是邮件的内容")
message['To'] = email.utils.formataddr(('接收者显示的姓名', 'receiver@qq.com'))
message['From'] = email.utils.formataddr(('发送者显示的姓名', 'sender@foxmail.com'))
message['Subject'] = '我是邮件的标题'
server = smtplib.SMTP_SSL('smtp.qq.com', 465)
server.login('Loginer_email@qq.com', '{请输入你的SMTP KEY}')
server.set_debuglevel(False)
try:
    server.sendmail('sender@qq.com', ['receiver@qq.com'], msg=message.as_string())
    isSend = True
except smtplib.SMTPException as e:
    print("Check_Send Sending Failure.The Error message is :: " + str(e))
    isSend = False
finally:
    server.quit()
```

关于其中的 SMTP KEY 的获取，如果您是QQ邮箱的话，可以参考 **[参考链接](/archives/121/)** 来进行获取，SMTP KEY 本质上就是一个登录的凭证而已，并不是多高级的东西

# 实现思路

通过设计 for_mail.py 来获取参数，通过获取的参数来进行 Jinja2 合成 HTML，并通过邮箱进行发送。同时为了避免RCE攻击，也需要使用 shlex 进行相关参数的过滤。直接命令行操控的程序为 mail.py。基本流程如下图所示：

![基本流程](/xiaolongtongxue/typecho_comment_mail/images/image-20230601212816615.png)

这边针对 Typecho 开发了一套评论邮件自动回复的方案，考虑到对实际生产业务性能的而影响，最终实现的效果为评论的内容会在五分钟之内恢复到上一级评论者的邮箱中（自己给自己回复的不予发送），同时考虑到邮箱轰炸行为的可能，这边使用Redis对回复邮箱的行为进行了限制，如果配合好 XL-Sec 的CC防御功能，则可有效避免邮箱轰炸的行为出现。

![实际上的发送邮件操作](/xiaolongtongxue/typecho_comment_mail/images/image-20230601212342682.png)

# 实际效果

本博客已经集成了该邮件回复系统，可以在本文下方直接评论尝试捏！来试试不就知道啦！

[hide]谢谢您的支持！[/hide]

邮件长这样

![image-20230601214122435](/xiaolongtongxue/typecho_comment_mail/images/image-20230601214122435.png)

# 特点

## 思路特点

- 避免了 PHP 中一些较难配置的点，避免了一些固定插件中的固化内容；
- 高度 diy 化，十分灵活，方便用户配置。

## 安全性

通过 shelx 进行了安全配置，避免了 RCE 攻击的情况。案例：

```python
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
```

# 安装部署方法

本项目已开源，适用于各种版本的基于 Linux 平台运行的 Typecho 站点 ，需要有 crontab 和 Redis 的支持，欢迎各位站长朋友、师傅们点个 STAR 呀：

| **git**  | **链接**                                                     |
| -------- | ------------------------------------------------------------ |
| Github   | **[https://github.com/xiaolongtongxue/typecho_comment_mail](https://github.com/xiaolongtongxue/typecho_comment_mail)** |
| Gitee    | **[https://gitee.com/xiaolongtongxue/typecho_comment_mail](https://gitee.com/xiaolongtongxue/typecho_comment_mail)** |
| 个人Gogs | **[https://git.txk123.top/xiaolongtongxue/typecho_comment_mail](https://git.txk123.top/xiaolongtongxue/typecho_comment_mail)** |

安装脚本如下：

```bash
git clone https://gitee.com/xiaolongtongxue/typecho_comment_mail
mv typecho_comment_mail /www/typecho_comment_mail
cd /www/typecho_comment_mail
```

接下来需要在修改相应的程序中的内容，每隔文件都有，稍稍看下就好，都在前十几行，其中示例中的 typecho_ 实际上就是您的数据库表的表头

![配置示例](/xiaolongtongxue/typecho_comment_mail/images/image-20230601215421370.png)

```bash
bash install.sh
```

[note type="info flat"]在运行 install.sh进行安装的时候，会要求进行针对新创建的低权限用户的 crontab 的编辑，默认是使用 vi 或者vim 进行编辑，如果不知道如何使用 vim 编辑的话，直接按下按键“i”，然后粘贴后，依此按下 ":wq" 和 Esc 就可以退出了，vim很好用，建议一定要会呢！[/note]

# Ending

在临毕业前给大家整了个小活儿，如果大家觉得有用的话，不妨点击下方的 **打赏** 按钮，请我喝杯冰阔乐捏！嘿嘿🤭



