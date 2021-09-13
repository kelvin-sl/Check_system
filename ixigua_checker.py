"""
 4/14 可以讀到西瓜上創作者的name video tag
 4/17 chrome不能用無頭模式上西瓜視頻
 5/29 solve upvideo problem
"""
from loguru import logger
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from email.mime.text import MIMEText
from email.utils import formataddr
import db_connection
import pandas as pd
import os
import datetime
import time
import requests
import smtplib
import csv

# 只要傳入id 就可以得到最新影片
def last_video(creator_id):
    # 用firefox查西瓜資料
    options = Options()
    options.add_argument('--headless')
    path = '/home/kelvin/geckodriver/geckodriver'
    browser = webdriver.Firefox(executable_path=path, options=options)

    url = f"https://www.ixigua.com/home/{creator_id}"

    browser.get(url)
    # 等待網站回應
    time.sleep(20)

    soup = BeautifulSoup(browser.page_source, "html5lib")

    try:
        video = soup.find('div', {'class':'HorizontalFeedCard'})
    except Exception as e:
        return e

    try:
        video.find('span', {'class':'stickingTag'}).text
        video = soup.find_all('div', {'class':'HorizontalFeedCard'})
        upload_time = video[1].find('div', {'class':'HorizontalFeedCard__bottomInfo'})
        upload_time = upload_time.text.split('·')[1][1:]

        last_video = video[1].find('div', {'class':'HorizontalFeedCard__contentWrapper'}).find('a')

    except :
        video = soup.find('div', {'class':'HorizontalFeedCard'})
        upload_time = video.find('div', {'class':'HorizontalFeedCard__bottomInfo'})
        upload_time = upload_time.text.split('·')[1][1:]
    
        last_video = video.find('div', {'class':'HorizontalFeedCard__contentWrapper'}).find('a')

    link = f"https://www.ixigua.com{last_video.get('href')}"
    browser.quit()
    return last_video.text, link ,upload_time


def sendEmailtooper(name_op, creator, update_time, url_video):
    '''
     To 運營者
     Cc kelvin sherry
    '''

    logger.debug(f'Sending email to {name_op}')
    nl = '\n'
    ret=True
    try:
        my_sender = "kelvinwang@cyberbroad.cn"
        my_pass = "ShdewmiSbyr4u7M7"
        my_user = f'{name_op}@cyberbroad.cn'
        my_checker = "sherrylin@cyberbroad.cn"

        content = f"嗨，{name_op}" + f"{nl}我们注意到{creator}有一部新视频 " + f"{nl}发布时间：{update_time} " +f"{nl}{url_video}" + f"{nl}{nl}提醒你在一小时内处理以下运营工作" +f"{nl}1. 设置引导关注按钮 " + f"{nl}2. 置顶留言" +f"{nl}3. 与观众互动" +f"{nl}{nl}增加创作者与观众的连结！" + f"{nl}{nl}星擘机器人" +f"{nl}祝好"
        # 邮件内容
        msg=MIMEText(content,'plain','utf-8')
        # 邮件的主题      
        msg['Subject']="【星擘文化西瓜运营通知】"       
        # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['From']=formataddr(["星擘机器人", my_sender]) 
        # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['To']=formataddr([name_op, my_user])
        # 副本
        msg['cc']=f'{formataddr(["Kelvin", my_sender])}'

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

def ixigua_checker(creator):
    validation = last_video(creator.get('ixigua'))
    if len(validation) != 3:
        a = 1/0
    last_video_name, link, upload_time = validation

    format = [last_video_name, link, time_format(upload_time)]
    format = tuple(format)

    # 取得DB中的創作者紀錄

    table_name = f"{creator.get('Id')}_ixigua"
    record = db_connection.get_creator_info(table_name)

    if record.get('Link') != link:
        # send info email
        logger.info(f'New video has been found.')
        sendEmailtooper(creator.get('oper_name'), creator.get('Name'), time_format(upload_time), link)
        logger.success('Mailing completed')

        # tragger the update time in Account_creator
        logger.info(f'Update notification time')
        db_connection.update_time(creator.get('Name'), time_format(upload_time))
        logger.success(f'Updating completed')

        # insert new video into db
        logger.info(f'Insert new video info into table')
        db_connection.insert_new_video(format, table_name)
        logger.success(f'Inserting completed')


    else:
        logger.info(f'Not Find New Video')
    return 0


def time_format(upload_time):
    today = datetime.datetime.today()
    if '分钟' in upload_time:

        min = int(upload_time.split('分')[0])
        format_min = datetime.timedelta(minutes = min)
        output_time = today - format_min
        return output_time
    elif '小时' in upload_time:
        
        hour = int(upload_time.split('小')[0])
        format_hour = datetime.timedelta(hours = hour)
        output_time = today - format_hour
        return output_time
    elif '昨天' in upload_time:
        
        format_day = datetime.timedelta(days = 1)
        output_time = today - format_day
        output_time = output_time.replace(hour = 18)
        return output_time
    elif '前天' in upload_time:
        
        format_day = datetime.timedelta(days = 2)
        output_time = today - format_day
        output_time = output_time.replace(hour = 18)
        return output_time
    else:
        month, day = upload_time.split('-')
        output_time = today.replace(month = int(month), day = int(day), hour = 18)
        return output_time
