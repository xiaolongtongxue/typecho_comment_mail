INSTALL_PATH=/www/typecho_comment_mail

cd $INSTALL_PATH

echo "----------------"
echo "下载相应的python包"
echo "----------------"

pip3 install PyEmail
pip3 install mysql-connector-python==8.0.23
python3 install.py

echo "-------------"
echo "用户权限相关操作"
echo "-------------"

useradd type_comment_mail -s /sbin/nologin
groupadd type_comment_mail_group
usermod -a -G type_comment_mail_group type_comment_mail
chgrp -R type_comment_mail_group $INSTALL_PATH
chmod -R 750 $INSTALL_PATH

sudo echo "type_comment_mail ALL=(ALL) NOPASSWD:`which crontab`" >> /etc/sudoers


echo "接下来需要您手动编辑一下crontab的文件，请复制下边的文字并将其粘贴进接下来的编辑框中

# '''
*/5 8-22 * * * python3 ${INSTALL_PATH}/mail.py
*/30 * * * * python3 ${INSTALL_PATH}/mail.py
# '''

准备好之后请按任意键继续。
Press any key to continue when ready.
"
read

sudo crontab -u type_comment_mail -e

cd -

echo "安装完毕"
echo "install Ready"
