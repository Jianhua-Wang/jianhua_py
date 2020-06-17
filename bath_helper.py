# -*- coding:UTF-8 -*-
import requests
import datetime
import time
def print_logo():
    logo = '''
========================================================================
     \033[1;33m/\\\033[0m
    \033[1;33m/__\\\033[0m\033[1;31m\\\033[0m            Take a bath whenever you want.
   \033[1;33m/\033[0m  \033[1;31m---\\\033[0m
  \033[1;33m/\\\033[0m      \033[1;31m\\\033[0m          Author: Jianhua Wang
 \033[1;33m/\033[0m\033[1;32m/\\\033[0m\033[1;33m\\\033[0m     \033[1;31m/\\\033[0m         Date:   05-30-2020
 \033[1;32m/  \   /\033[0m\033[1;31m/__\\\033[0m
\033[1;32m`----`-----\033[0m
========================================================================
    '''
    print(logo)

print_logo()
username = input('手机号：')
password = input('密码：')
host = 'http://t1.beijingzhangtu.com'
appointmentStartTime = '18:00'
appointmentEndTime = '22:00'
dayTime = (datetime.datetime.now()+datetime.timedelta(days=1)).strftime("%Y-%m-%d")
# dayTime = (datetime.datetime.now().strftime("%Y-%m-%d")

print(f'将要预约时间为：{dayTime} {appointmentStartTime}-{appointmentEndTime}')

loginPayload = {
    'phone': username,
    'pass': password
    }
login_json = requests.post(host+'/api/user/loginByPhone.html', data=loginPayload).json()
print(login_json['msg'])
userId = login_json['data']['id']
libraryId = login_json['data']['libraries'][0]['id']
token = login_json['data']['token']

def appoint():
    RandomPayload = {
        'floorid': '149',
        'roomid': '287',
        'appointmentStartTime': appointmentStartTime,
        'appointmentEndTime': appointmentEndTime,
        'buildingid': '71',
        'appointmentDay': dayTime,
        'libraryid': libraryId,
        'userid': userId,
        'token': token
        }
    Random_json = requests.post(host+'/api/YySeatAppointment/autoAppointmentes.html', data=RandomPayload).json()
    print(Random_json['msg'])
    if int(Random_json['code']):
        print(f"随机预约的位置为{Random_json['data']['num']}")
        return 0
    else:
        return 1

out = 1
print('开始预约，按ctrl C停止。')
while out:
    print('继续尝试。。。')
    # time.sleep(1)
    out = appoint()