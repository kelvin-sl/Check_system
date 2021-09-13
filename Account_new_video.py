# 2021/7/24 record還不會判斷抓到重複值

from email.mime.text import MIMEText
from email.utils import formataddr
from loguru import logger
import db_connection
import smtplib
import ixigua_checker
import bilibili_info
import datetime
import time

def main_checker():
    pass
    creators = db_connection.get_total_info()
    for creator in creators:

        # 先進西瓜再進b站
        logger.info(f"Checking the ixigua channel of {creator.get('Name')}")
        try:
            validation = ixigua_checker.ixigua_checker(creator)
        except Exception as e:
            # 建立錯誤表格 將沒有檢查到的頻道存在錯誤表格中
            logger.warning('Happened Exception')
            error_creator = (creator.get('Name'), creator.get('ixigua'), creator.get('oper_name')
                        , datetime.datetime.today(), e)
            db_connection.insert_error_channel_ixigua(error_creator)


        if creator.get('bilibili') != '':
            
            logger.info(f"Checking the bilibili channel of {creator.get('Name')}")
            try:
                validation = bilibili_info.bilibili_checker(creator)
            except Exception as e:
                # 建立錯誤表格 將沒有檢查到的頻道存在錯誤表格中
                logger.warning('Happened Exception')
                error_creator = (creator.get('Name'), creator.get('bilibili'), creator.get('oper_name')
                            , datetime.datetime.today(), e)
                db_connection.insert_error_channel_bilibili(error_creator)


def break_info():
    logger.info(f"Start the Broken Update Info")

    creators = db_connection.get_total_info()
    today = datetime.datetime.today()
    seven_day = datetime.timedelta(6,0,0)
    for creator in creators:
        # time.sleep(5)

        # 先看西瓜頻道是否更新
        logger.info(f"Checking the ixigua channel of {creator.get('Name')}")

        table_name = f"{creator.get('Id')}_ixigua"
        record = db_connection.get_creator_info(table_name)

        if isinstance(record.get('Last_update'), datetime.datetime):
            if (today - record.get('Last_update')) > seven_day :
                sendEmailtobrokenoper(creator, '西瓜视频', record.get('Last_update'))
            else:
                logger.info(f"Ixigua account of {creator.get('Name')} is continuously updating ")
        else:
            logger.warning(f'Datetime format wrong! In table {table_name}')

        if creator.get('bilibili') != '':
            logger.info(f"Checking the bilibili channel of {creator.get('Name')}")
            table_name = f"{creator.get('Id')}_bilibili"
            record = db_connection.get_creator_info(table_name)

            if isinstance(record.get('Last_update'), datetime.datetime):
                if (today - record.get('Last_update')) > seven_day :
                    sendEmailtobrokenoper(creator, 'B站', record.get('Last_update'))
                else:
                    logger.info(f"Bilibili account of {creator.get('Name')} is continuously updating ")
            else:
                logger.warning(f'Datetime format wrong! In table {table_name}')


def sendEmailtobrokenoper(creator_info, platform, upload_time):
    name_op = creator_info.get('oper_name')
    creator = creator_info.get('Name')

    logger.debug(f'Email Broken Update Info to {name_op}')
    nl = '\n'
    ret=True
    try:
        my_sender = "kelvinwang@cyberbroad.cn"
        my_pass = "ShdewmiSbyr4u7M7"
        my_user = f'{name_op}@cyberbroad.cn'
        my_checker = "sherrylin@cyberbroad.cn"
        my_boss = "haotienlan@cyberbroad.cn"

        content = (f"嗨，{name_op}"+
            f"{nl}我们注意到{creator} 在{platform}的帐号超过一周没有上传新视频" +
            f"{nl}上次的发布时间為：{upload_time} " +
            f"{nl}{nl}请至创作者的youtube帐号查看他的最新视频" +
            f"{nl}{nl}增加创作者与观众的连结！" +
            f"{nl}{nl}星擘机器人" +
            f"{nl}祝好")
        # 邮件内容
        msg=MIMEText(content,'plain','utf-8')
        # 邮件的主题      
        msg['Subject']="【帐号断更通知】"       
        # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['From']=formataddr(["星擘机器人", my_sender]) 
        # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['To']=formataddr([name_op, my_user])
        # 副本
        msg['cc']=f'{formataddr(["Kelvin", my_sender])}, {formataddr(["Sherry", my_checker])}, {formataddr(["Jason", my_boss])}'

        # SMTP服务器，腾讯企业邮箱端口是465，腾讯邮箱支持SSL(不强制)， 不支持TLS
        # qq邮箱smtp服务器地址:smtp.qq.com,端口号：456
        server=smtplib.SMTP_SSL("smtp.exmail.qq.com", 465) 
        # 登录服务器，括号中对应的是发件人邮箱账号、邮箱密码
        server.login(my_sender, my_pass) 
        # 发送邮件，括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.sendmail(my_sender, [my_user, my_sender, my_checker, my_boss], msg.as_string()) 
        # 关闭连接
        server.quit() 
        # 如果 try 中的语句没有执行，则会执行下面的 ret=False 
    except Exception: 
        ret=False

# break_info()
now = datetime.datetime.today()
check_once = True

while True:
    time.sleep(2)
    now = datetime.datetime.today()

    if now.hour % 3 == 0:
        main_checker()

    if now.weekday() == 6 and now.hour == 19 and check_once:
        break_info()
        check_once = False

    if now.weekday() == 6 and now.hour == 20:
        check_once = True


