from loguru import logger
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.utils import formataddr
import datetime
import time
import requests
import smtplib
import db_connection




def last_video(creator_id):

        url = f'https://api.bilibili.com/x/space/arc/search?mid={creator_id}&pn=1&ps=1&index=1&jsonp=jsonp'    
        response_1 = requests.get(url)
        video_info = response_1.json()
        lastest_video = video_info["data"]["list"]["vlist"][0]["bvid"]
        up_name = video_info["data"]["list"]["vlist"][0]["author"]

      

        # 得到影片的發布時間
        url_video = f'https://www.bilibili.com/video/{lastest_video}'
        response_2 = requests.get(url_video)
        soup = BeautifulSoup(response_2.text, "html5lib")

        update_time = soup.find('div', {'class':'video-data'}).find_all('span')[2].text

        try:
            video_name = soup.find('span', {'class':'tit tr-fix'}).text
        except Exception as e:
            video_name = soup.find('span', {'class':'tit'}).text

    
        temp_list = [x for x in update_time.split(' ')]
        d_list = [int(x) for x in temp_list[0].split('-')]
        t_list = [int(x) for x in temp_list[1].split(':')]
        date_format = datetime.datetime(d_list[0], d_list[1], d_list[2], t_list[0], t_list[1], t_list[2])
        return video_name, url_video, date_format

def sendEmailtooper(name_op, creator, update_time, url_video):

    logger.debug(f'Sending email to {name_op}')
    nl = '\n'
    ret=True
    try:
        my_sender = "kelvinwang@cyberbroad.cn"
        my_pass = "ShdewmiSbyr4u7M7"
        my_user = f'{name_op}@cyberbroad.cn'
        my_checker = "sherrylin@cyberbroad.cn"

        content = f"嗨，{name_op}"+f"{nl}我们注意到{creator}有一部新视频 " +f"{nl}发布时间：{update_time} " +f"{nl}{url_video}" +f"{nl}{nl}提醒你在一小时内处理以下运营工作" +f"{nl}1. 设置一键三连按钮 (设置于10秒处，左下角)" +f"{nl}2. 置顶留言" +f"{nl}3. 与观众互动" +f"{nl}4. 设置关联视频 (设置于片尾，置中)" +f"{nl}{nl}增加创作者与观众的连结！" +f"{nl}{nl}星擘机器人" +f"{nl}祝好"
        # 邮件内容
        msg=MIMEText(content,'plain','utf-8')
        # 邮件的主题      
        msg['Subject']="【星擘文化运营通知】"       
        # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['From']=formataddr(["星擘机器人", my_sender]) 
        # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['To']=formataddr([name_op, my_user])
        # 副本
        msg['cc']=f'{formataddr(["Kelvin", my_sender])},{formataddr(["Sherry", my_checker])}'

        # SMTP服务器，腾讯企业邮箱端口是465，腾讯邮箱支持SSL(不强制)， 不支持TLS
        # qq邮箱smtp服务器地址:smtp.qq.com,端口号：456
        server=smtplib.SMTP_SSL("smtp.exmail.qq.com", 465) 
        # 登录服务器，括号中对应的是发件人邮箱账号、邮箱密码
        server.login(my_sender, my_pass) 
        # 发送邮件，括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.sendmail(my_sender, [my_user, my_sender, my_checker], msg.as_string()) 
        # 关闭连接
        server.quit() 
        # 如果 try 中的语句没有执行，则会执行下面的 ret=False 
    except Exception: 
        ret=False

def bilibili_checker(creator):
    validation = last_video(creator.get('bilibili'))
    if len(validation) != 3:
        a = 1/0
    last_video_name, link, upload_time = validation
    format = [last_video_name, link, upload_time]
    format = tuple(format)

    # 取得DB中的創作者紀錄

    table_name = f"{creator.get('Id')}_bilibili"
    record = db_connection.get_creator_info(table_name)
    # and record.get('Link') != link
    if record.get('Link') != link :
        # send info email
        logger.info(f'New video has been found.')
        sendEmailtooper(creator.get('oper_name'), creator.get('Name'), upload_time, link)
        logger.success('Mailing completed')

        # tragger the update time in Account_creator
        logger.info(f'Update notification time')
        db_connection.update_time(creator.get('Name'), upload_time)
        logger.success(f'Updating completed')
        
        # insert new video into db
        logger.info(f'Insert new video info into table')
        db_connection.insert_new_video(format, table_name)
        logger.success(f'Inserting completed')


    else:
        logger.info(f'Not Find New Video')
    return 0

