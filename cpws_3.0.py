# coding=utf-8

from selenium import webdriver
import time
from hand_html import Handel_html
from rand_ua import Rand_ua
from read_company import read_company2, read_company1
from logs import Log
from item_dumpkey import Item_dump
import pymongo
from pyvirtualdisplay import Display
# 优化内容：
# 将访问异常企业写入csv
# 标记查询未完整的公司，数据未完整，只有前{}页,共{}页



class Cp_spider():

    def __init__(self, company):
        u = Rand_ua()
        ua = u.rand_chose()

        try:

            options = webdriver.ChromeOptions()
            options.add_argument('--user-agent={}'.format(ua))
            # options.add_argument("headless")
            # prefs = {'profile.default_content_setting_values': {'images': 2}}
            # options.add_experimental_option('prefs', prefs)  # 采用无图模式效果不理想

            self.driver = webdriver.Chrome(chrome_options=options)
        except Exception as e:
            Log('log/cp_log.log', e=e)
            # self.display.stop()
            return

        self.cp_url = "http://wenshu.court.gov.cn/"
        self.company = company

    def get_info(self):
        # self.driver.implicitly_wait(15) # 显性等待
        try:
            self.driver.get(self.cp_url)
            self.driver.find_element_by_xpath('//input[@id="gover_search_key"]').click()
            self.driver.find_element_by_xpath('//input[@id="gover_search_key"]').send_keys(self.company)
            self.driver.find_element_by_xpath("//button[@class='head_search_btn']").click()
        except Exception as e:
            print("*"*10,str(e))
            Log('log/cp_log.log',e=e)
            # self.driver.quit()
            return ["获取网页内容时出现异常"]

        time.sleep(10)
        html_list = []
        page = 1

        # [['（2016）京01民终7217号', '2016-12-19', '北京市第一中级人民法院', '魏巍等劳动争议二审民事判决书', ['民事', '二审'], 'http://wenshu.court.gov.cn/content/content?DocID=d4117425-9198-40a2-8a98-3711404e253b&KeyWord=深圳市中合银融资担保有限公司'], ['（2017）粤03民终2926号', '2017-05-12', '广东省深圳市中级人民法院', '江西中联建设集团有限公司与', ['民事', '二审'], 'http://wenshu.court.gov.cn/content/content?DocID=5d5cf5a2-2531-416b-9516-a85101011a03&KeyWord=深圳市中合银融资担保有限公司'], ['（2016）粤03民辖终3827、3828号', '2016-11-17', '广东省深圳市中级人民法院', '旭东电力集团有限公司与', ['民事', '二审'], 'http://wenshu.court.gov.cn/content/content?DocID=fe883891-d1a8-44a3-a23c-1f67a0349cb7&KeyWord=深圳市中合银融资担保有限公司'], ['（2016）粤0304民初18775-18776号', '2016-09-21', '深圳市福田区人民法院', '与旭东电力集团有限公司罗云富保证合同纠纷一审民事裁定书', ['民事', '一审'], 'http://wenshu.court.gov.cn/content/content?DocID=1c55cb08-667d-48eb-9dae-a7f4010e73cc&KeyWord=深圳市中合银融资担保有限公司'], ['（2016）粤0304民初18775-18776号之一', '2017-07-10', '深圳市福田区人民法院', '与旭东电力集团有限公司、罗云富保证合同纠纷一审民事裁定书', ['民事', '一审'], 'http://wenshu.court.gov.cn/content/content?DocID=197c2dfb-7520-4b7d-9598-a7f4010e73f2&KeyWord=深圳市中合银融资担保有限公司']]
        try:
            html = self.driver.page_source
            h = Handel_html(html=html)
            result = h.pd_html()
            if not result:
                self.driver.quit()
                return ["无符合条件的数据"]
            total = h.get_total() # 文书总条数
            t1 = int(total)%5
            t2 = int(total)/5
            if t1 != 0:
                total_page=int(t2)+1
            else:
                total_page = int(t2)
            print(total_page)

        except Exception as e:
            Log('log/cp_log.log', e=e)
            print("*" * 10, str(e))
            html = "获取网页内容时出现异常"
            html_list.append(html)
            total_page = 0
            self.driver.quit()


        html_list.append(html)

        while page < total_page:
            print("***********page", page)
            try:
                # self.driver.implicitly_wait(15) 使用未生效
                time.sleep(3)
                self.driver.find_element_by_xpath('//a[@class="next"]').click()
            except Exception as e:
                # 将错误写入日志
                # print('发生异常')
                print("*"*10, str(e))
                self.driver.quit()
                html_list.append("数据未完整，只有前{}页,共{}页".format(page,total_page))
                break
            time.sleep(10)
            page += 1
            try:
                html = self.driver.page_source
            except Exception as e:
                print("*" * 10, str(e))
                Log('log/cp_log.log', e=e)
                html = "获取网页内容时出现异常"
                html_list.append(html)
                self.driver.quit()
                # self.display.start()
            html_list.append(html)

        self.driver.quit()
        # self.display.start()

        return html_list


class main_spider():

    def __init__(self, csv, type=None):
        self.company_list = read_company2(csv)
        self.type = type
        self.client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        self.conn = self.client["qg_ss"]['cp_info']

    def save_mongodb(self, item):
        self.conn.insert_one(dict(item))
        print("保存成功！")


    def run(self):
        for company in self.company_list:
            i = Item_dump(company)
            ret = i.item_dump()
            if not ret:
                item = {}
                cp = Cp_spider(company)
                html_list = cp.get_info()
                if html_list == ["无符合条件的数据"]:
                    cp_list = ["无符合条件的数据"]
                else:
                    h = Handel_html(html_list=html_list)
                    cp_list = h.run()

                # 如果获取内容出现异常时计入异常名单
                if cp_list == ["获取网页内容时出现异常"]:
                    with open('log/except_company.csv','a') as f:
                        f.write(company+'\n')
                else:
                    item["company"] = company
                    item["type"] = self.type
                    item["文书信息"] = cp_list
                    print(item)
                    self.save_mongodb(item)


    def run_text(self):
        for company in self.company_list:
            item = {}
            cp = Cp_spider(company)
            html_list = cp.get_info()
            if html_list == ["无符合条件的数据"]:
                cp_list = ["无符合条件的数据"]
            else:
                h = Handel_html(html_list=html_list)
                cp_list = h.run()
            item["company"] = company
            item["type"] = self.type
            item["文书信息"] = cp_list
            print(item)



if __name__ == '__main__':
    path = "/home/python/Desktop/company/sz_total.csv"
    # path = "./log/text_company.csv"
    m = main_spider(path)
    m.run_text()
    # print(cp_list)




