#重要提醒：1.在使用本脚本前，首先首先首先！！！编辑好名为"12306.json"的文件，否则无法运行！！json文件中名称的具体含义可见本程序35-37行代码
#        2.下载浏览器驱动，将驱动放在python.exe所在的根目录下
#（必看）  3.提前找到想乘坐的车次预定按钮css信息，填到187和195行代码！！！！
#        4.第一次使用需要扫码登录，之后会生成一个名为"12306cookies.pkl"的文件，之后短时间内购票就不需要再进行登录操作（①若需要重新登录，删掉此文件即可；②长时间未登录，也需要删掉此文件重新登陆）
#        5.21行进行定时设置，设置时间最好提前10秒
#        6.无选座功能
import time
import requests
from prettytable import PrettyTable
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import pickle
import os
import datetime
import sys
def stop():
    sys.exit()
#下面8行代码是定时抢票功能，需要的可以取消注释

# dingshi='2024-12-11 09:59:50' #这里设置抢票时间（24小时制），最好提前十秒，比如14:30：00可以设置成14:29:50
# print(f'您设置的时间是：{dingshi}')
# while 1:
#     print('\r当前时间：{}'.format(str(datetime.datetime.now())[:19]),end="",flush=True)
#     time.sleep(1)
#     n=str(datetime.datetime.now())[:19]
#     if n==dingshi:
#         break

#加载乘客信息（请在json文件中设置好个人出行信息）
info_user=open('E:/cursor_pro/12306_ticket/12306抢票/12306抢票/Ticket_script/12306.json', encoding='utf-8').read()
user_data=json.loads(info_user)
FP=user_data['FP']#出发城市
TP=user_data['TP']#目的城市
DATE=user_data['DATE']#出发日期（XXXX-XX-XX）
while 1:
    # choice=2
    choice=int(input('查票请扣1，购票请扣2，退出请扣3：'))
    if choice==1 or choice==2:
        if choice==1:
            print('---------------------查票功能---------------------')
            #读取12306上对应的城市编号文件city.json
            f=open('E:/cursor_pro/12306_ticket/12306抢票/12306抢票/Ticket_script/city.json',encoding='utf-8').read()
            city_data=json.loads(f)
            # 修改请求URL和参数1
            base_url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ'
            params = {
                'leftTicketDTO.train_date': DATE,
                'leftTicketDTO.from_station': city_data[FP],
                'leftTicketDTO.to_station': city_data[TP],
                'purpose_codes': 'ADULT'
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://kyfw.12306.cn',
                'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
                'X-Requested-With': 'XMLHttpRequest',
                'Host': 'kyfw.12306.cn',
                'Connection': 'keep-alive'
            }

            # 创建session对象来维持会话
            session = requests.Session()
            session.headers.update(headers)

            try:
                # 首先访问初始页面获取必要的cookies
                session.get('https://kyfw.12306.cn/otn/leftTicket/init')
                # 使用POST方法发送请求
                time.sleep(1)  # 添加延迟
    
                # 构建完整的URL（使用GET方法而不是POST）
                query_url = f"{base_url}?leftTicketDTO.train_date={params['leftTicketDTO.train_date']}&leftTicketDTO.from_station={params['leftTicketDTO.from_station']}&leftTicketDTO.to_station={params['leftTicketDTO.to_station']}&purpose_codes={params['purpose_codes']}"

                # 发送GET请求
                response = session.get(query_url)
                if response.status_code != 200:
                    print(f"Error: Request failed with status code {response.status_code}")
                    print(f"Response text: {response.text}")
                    stop()
                json_data = response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error making request: {e}")
                print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
                stop()
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                print(f"Response text: {response.text}")
                stop()
            #print(json_data)
            tb=PrettyTable()
            tb.field_names=[
                '序号',
                '车次',
                '出发时间',
                '到达时间',
                '耗时',
                '特等座',
                '一等',
                '二等',
                '软卧',
                '硬卧',
                '硬座',
                '无座'
            ]
            page=0
            #扒取信息中的有用信息
            result=json_data['data']['result']
            for i in result:
                index=i.split('|')
                # page=0
                # for j in index:
                #     print(page,"***",j)
                #     page+=1
                # break
                num=index[3]#车次
                leave_time = index[8]  # 出发时间
                arrive_time = index[9]  # 到达时间
                cost_time = index[10]  # 耗时
                topGrade=index[32]#商务
                first_class = index[31]#一等座
                second_class = index[30]#二等座
                hard_sleeper = index[28]#硬卧
                hard_seat = index[29]#硬座
                no_seat = index[26]#无座
                soft_sleeper = index[23]#软卧
                # dict={
                #     '车次':num,
                #     '出发时间': leave_time,
                #     '到达时间': arrive_time,
                #     '耗时': cost_time,
                #     '特等座': topGrade,
                #     '一等': first_class,
                #     '二等': second_class,
                #     '软卧': soft_sleeper,
                #     '硬卧': hard_sleeper,
                #     '硬座': hard_seat,
                #     '无座': no_seat
                # }
                tb.add_row([
                page,
                num,
                leave_time,
                arrive_time,
                cost_time,
                topGrade,
                first_class,
                second_class,
                soft_sleeper,
                hard_sleeper,
                hard_seat,
                no_seat
                ])
                page+=1
            print(tb)

        if choice==2:
            print('---------------------购票功能---------------------')
            zhuye12306_url='https://www.12306.cn/index/index.html'
            target_url='https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc'

            class Log:
                def __init__(self):
                    self.status = 0
                    self.login_method = 1
                    self.options = webdriver.EdgeOptions()
                    self.options.add_experimental_option('detach', True)
                    self.options.add_experimental_option('excludeSwitches', ['enable automation'])
                    self.driver = webdriver.Edge(options=self.options)

                def button(self):
                    try:
                        self.driver.find_element(By.ID, 'link_for_ticket')
                        return True
                    except exceptions.NoSuchElementException:
                        return False

                def set_cookies(self):
                    self.driver.get(zhuye12306_url)
                    self.driver.find_element(By.ID,'J-btn-login').click()
                    print('###请扫码登录###')
                    while not self.button():
                        time.sleep(1)
                    print('###扫码成功###')
                    pickle.dump(self.driver.get_cookies(), open('12306cookies.pkl', 'wb'))
                    print('cookie保存成功')
                    self.driver.get(target_url)

                def get_cookie(self):
                    cookies = pickle.load(open('12306cookies.pkl', 'rb'))
                    for cookie in cookies:
                        cookie_dict = {
                            'domain': '.12306.cn',
                            'name': cookie.get('name'),
                            'value': cookie.get('value')
                        }
                        self.driver.add_cookie(cookie_dict)
                    print('载入cookie')


                def login(self):
                    if self.login_method == 0:
                        self.driver.get(zhuye12306_url)
                        print('开始登录')
                    elif self.login_method == 1:
                        if not os.path.exists('12306cookies.pkl'):
                            self.set_cookies()
                        else:
                            self.driver.get(target_url)
                            self.get_cookie()

                def goupiao(self):
                    self.driver.maximize_window()
                    # 输入出发地点
                    self.driver.find_element(By.ID, 'fromStationText').click()
                    self.driver.find_element(By.ID, 'fromStationText').clear()
                    self.driver.find_element(By.ID, 'fromStationText').send_keys(FP)
                    self.driver.find_element(By.ID, 'fromStationText').send_keys(Keys.ENTER)
                    # 输入到达地点
                    self.driver.find_element(By.ID, 'toStationText').click()
                    self.driver.find_element(By.ID, 'toStationText').clear()
                    self.driver.find_element(By.ID, 'toStationText').send_keys(TP)
                    self.driver.find_element(By.ID, 'toStationText').send_keys(Keys.ENTER)
                    # 输入出发日期
                    self.driver.find_element(By.ID, 'train_date').click()
                    self.driver.find_element(By.ID, 'train_date').clear()
                    self.driver.find_element(By.ID, 'train_date').send_keys(DATE)
                    self.driver.find_element(By.ID, 'train_date').send_keys(Keys.ENTER)
                    # 学生票取消197和221行的注释
                    # self.driver.find_element(By.ID, 'sf2').click()
                    # 查询车票
                    self.driver.find_element(By.ID, 'query_ticket').click()
                    time.sleep(1)

                    # 预定车票
                    def iselement(self):
                        try:
                            self.driver.find_element(By.CSS_SELECTOR,'#queryLeftTable #ticket_6i0000G33602_01_07 .no-br .btn72')  #找到你想乘坐车次的ccs预定按钮信息
                            return True
                        except exceptions.NoSuchElementException:
                            return False

                    while not iselement(self):
                        #设置刷新页面时间间隔
                        # time.sleep(0.0001)
                        self.driver.find_element(By.ID, 'query_ticket').click()
                        # time.sleep(1)  # 增加循环等待时间
                    self.driver.find_element(By.CSS_SELECTOR,'#queryLeftTable #ticket_6i0000G33602_01_07 .no-br .btn72').click()
                    time.sleep(1)
                                        # 等待乘客选择界面加载
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC

                                    # 切换到乘客选择iframe（如果存在）
                    try:
                        iframe = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.ID, "iframe_id"))  # 需要替换为实际的iframe id
                        )
                        self.driver.switch_to.frame(iframe)
                    except:
                        pass  # 如果没有iframe就跳过

                    # 等待乘客选择元素出现
                    passenger = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "normalPassenger_0"))
                    )
                    passenger.click()

                    # 切回主框架（如果之前切换过iframe）
                    try:
                        self.driver.switch_to.default_content()
                    except:
                        pass
                    # self.driver.implicitly_wait(5)
                    # 选择乘车人（"0"代表第一个人，一般都是本人，多人的话依此类推）
                    # self.driver.find_element(By.ID, 'normalPassenger_0').click()
                    # driver.find_element(By.ID,'normalPassenger_1').click()
                    # driver.find_element(By.ID,'normalPassenger_2').click()
                    # self.driver.find_element(By.CSS_SELECTOR, '#dialog_xsertcj_ok.btn92s').click()

                    # 确定订单
                    self.driver.find_element(By.CSS_SELECTOR, '#submitOrder_id.btn92s').click()
                    time.sleep(3)
                    # 选座界面自动选座，直接提交订单
                    self.driver.find_element(By.ID, 'qr_submit_id').click()

                def enter_ticket(self):
                    print('打开浏览器，进入12306官网')
                    self.login()
                    self.driver.refresh()
                    self.status = 2
                    print('登录成功，开始购票')
                    self.goupiao()

            train = Log()
            train.enter_ticket()
            break
    if choice == 3:
        print('出门左转，米其林豪华厕所装修风格餐厅，快去吧，真是个小馋猫呢')
        break
"""
            options = webdriver.EdgeOptions()
            options.add_experimental_option('detach', True)
            options.add_experimental_option('excludeSwitches', ['enable automation'])
            prefs={'credentials_enable_service':False,'profile.password_manager_enabled':False}
            options.add_experimental_option('prefs',prefs)
            options.add_argument('--disable-blink-features=AutomationControlled')
            driver = webdriver.Edge(options=options)
            #打开购票网址
            # driver.get('https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc')
            driver.maximize_window()
            #输入出发地点
            driver.find_element(By.ID,'fromStationText').click()
            driver.find_element(By.ID,'fromStationText').clear()
            driver.find_element(By.ID,'fromStationText').send_keys(FP)
            driver.find_element(By.ID,'fromStationText').send_keys(Keys.ENTER)
            #输入到达地点
            driver.find_element(By.ID,'toStationText').click()
            driver.find_element(By.ID,'toStationText').clear()
            driver.find_element(By.ID,'toStationText').send_keys(TP)
            driver.find_element(By.ID,'toStationText').send_keys(Keys.ENTER)
            #输入出发日期
            driver.find_element(By.ID,'train_date').click()
            driver.find_element(By.ID,'train_date').clear()
            driver.find_element(By.ID,'train_date').send_keys(DATE)
            driver.find_element(By.ID,'train_date').send_keys(Keys.ENTER)
            #学生票的话取消126和157行的注释
            driver.find_element(By.ID,'sf2').click()
            #查询车票
            driver.find_element(By.ID,'query_ticket').click()
            time.sleep(1)
            #预定车票
            def iselement():
                try:
                    driver.find_element(By.CSS_SELECTOR,'#queryLeftTable #ticket_24000G10850D_03_10 .no-br .btn72')
                    return True
                except exceptions.NoSuchElementException:
                    return False
            while not iselement():
                time.sleep(0.5)
                driver.find_element(By.ID,'query_ticket').click()
            driver.find_element(By.CSS_SELECTOR,'#queryLeftTable #ticket_24000G10850D_03_10 .no-br .btn72').click()
            time.sleep(1)
            #输入身份证后四位
            driver.find_element(By.ID,'J-userName').click()
            driver.find_element(By.ID,'J-userName').send_keys(ACCOUNT)
            driver.find_element(By.ID,'J-password').click()
            driver.find_element(By.ID,'J-password').send_keys(PW)
            driver.find_element(By.ID,'J-login').click()
            time.sleep(1)
            driver.find_element(By.ID,'id_card').click()
            driver.find_element(By.ID,'id_card').send_keys(ID)
            driver.find_element(By.ID,'verification_code').click()
            #输入验证码
            VC=input('请输入验证码：')
            driver.find_element(By.ID,'code').click()
            driver.find_element(By.ID,'code').send_keys(VC)
            driver.find_element(By.ID,'sureClick').click()

            driver.implicitly_wait(10)
            #选择乘车人（"0"代表第一个人，一般都是本人，多人的话依此类推）
            driver.find_element(By.ID,'normalPassenger_0').click()
            # driver.find_element(By.ID,'normalPassenger_1').click()
            # driver.find_element(By.ID,'normalPassenger_2').click()
            driver.find_element(By.CSS_SELECTOR,'#dialog_xsertcj_ok.btn92s').click()

            #确定订单
            driver.find_element(By.CSS_SELECTOR,'#submitOrder_id.btn92s').click()
            time.sleep(3)
            #选座面自动选座，直接提交订单
            driver.find_element(By.ID,'qr_submit_id').click()
    if choice==3:
        print('出门左转，米其林豪华厕所装修风格餐厅，快去吧，真是个小馋猫呢')
        break
"""

