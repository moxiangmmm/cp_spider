# coding=utf-8
from selenium import webdriver
import time
from hand_html import Handel_html
from rand_ua import Rand_ua
from read_company import read_company2, read_company1
from logs import Log
from item_dumpkey import Item_dump
import pymongo
import concurrent.futures
from retrying import retry
# 打开浏览器
# 搜索框输入公司名称
# 点击搜索按钮

# 读取列表信息
# 翻页

# 清空搜索条件
# 输入公司名称
# 点击搜索

class cp_spider():

    def __init__(self,company_name):
        u = Rand_ua()
        ua = u.rand_chose()
        self.cp_url = "http://wenshu.court.gov.cn/"
        self.company_name = company_name
        options = webdriver.ChromeOptions()
        path = "E:\python开发环境\chromedriver.exe"
        options.add_argument('--user-agent={}'.format(ua))
        self.driver = webdriver.Chrome(chrome_options=options, executable_path=path)

    @retry(stop_max_attempt_number=5)
    def start_request(self):
        try:
            self.driver.get(self.cp_url)
            time.sleep(5)
            self.driver.find_element_by_xpath('//input[@id="gover_search_key"]').click()
            self.driver.find_element_by_xpath('//input[@id="gover_search_key"]').send_keys(self.company_name)
            self.driver.find_element_by_xpath("//button[@class='head_search_btn']").click()
            time.sleep(5)
            html = self.driver.page_source
        except Exception as e:
            print(str(e))
            return
        time.sleep(10)
        return html

    def get_info(self, html):
        html_list = []
        page = 1
        h = Handel_html(html=html)
        result = h.pd_html()
        if not result:
            return ["无符合条件的数据"]
        total = h.get_total()  # 文书总条数
        t1 = int(total) % 5
        t2 = int(total) / 5
        if t1 != 0:
            total_page = int(t2) + 1
        else:
            total_page = int(t2)
        print(total_page)
        html_list.append(html)
        time.sleep(10)
        # while page < total_page:
        #     print("***********page", page)
        #     try:
        #         # self.driver.implicitly_wait(15) 使用未生效
        #         driver.find_element_by_xpath('//a[@class="next"]').click()
        #     except Exception as e:
        #         # 将错误写入日志
        #         # print('发生异常')
        #         print("*" * 10, str(e))
        #         html_list.append("数据未完整，只有前{}页,共{}页".format(page, total_page))
        #         break
        #     time.sleep(15)
        #     page += 1
        #     try:
        #         html = driver.page_source
        #     except Exception as e:
        #         print("*" * 10, str(e))
        #         Log('log/cp_log.log', e=e)
        #         html = "获取网页内容时出现异常"
        #         html_list.append(html)
        #     html_list.append(html)

    def search_company(self,company_name):
        self.driver.find_element_by_xpath("//a[@title='清空检索条件']").click() # 清空检索条件
        self.driver.find_element_by_xpath('//input[@id="gover_search_key"]').click()
        self.driver.find_element_by_xpath('//input[@id="gover_search_key"]').send_keys(company_name)
        self.driver.find_element_by_xpath("//button[@class='head_search_btn']").click()
        time.sleep(5)
        return self.driver.page_source

    def run(self):
        html= self.start_request()
        self.get_info(html)
        self.search_company("腾讯")

def main_spider():
    company_list = []
    num = 1
    for com in company_list:
        # if num == 1:
        pass



if __name__ == '__main__':
    c = cp_spider("中合银")
    c.run()



