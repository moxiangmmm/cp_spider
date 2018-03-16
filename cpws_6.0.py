# coding=utf-8
import requests
import json
from cpws_pkg.make_header import make_header
from cpws_pkg.get_json import get_js
from lxml import etree
from cpws_pkg.logs import Log
from retrying import retry
from cpws_pkg.read_company import read_company2
from cpws_pkg.item_dumpkey import Item_dump
import pymongo
import time
# 第一步发起请求获取cookie 捕捉异常
# 第二步获取number 捕捉异常
# 第三步获取vl5x需执行一段js代码 捕捉异常
# 第四步携带参数请求内容 捕捉异常
# 处理取得数据 捕捉异常
# 传入变量 公司名称，

class Cp_Spider():

    def __init__(self,company_name):
        self.company_name = company_name
        self.first_url = "http://wenshu.court.gov.cn/list/list/?sorttype=1&conditions=searchWord+QWJS+++{}".format(self.company_name)
        self.list_url = "http://wenshu.court.gov.cn/List/ListContent"
        self.number_url = "http://wenshu.court.gov.cn/ValiCode/GetCode"
        self.d_url = "http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={}"

        self.session = requests.session()
        # case_info = "d4117425-9198-40a2-8a98-3711404e253b|魏巍等劳动争议二审民事判决书|2016-12-19"
        self.headers = """
Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Encoding:gzip, deflate
Accept-Language:zh-CN,zh;q=0.9
Cache-Control:max-age=0
Connection:keep-alive
Host:wenshu.court.gov.cn
Upgrade-Insecure-Requests:1
User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36
"""
        self.d_headers = make_header(self.headers)

    @retry(stop_max_attempt_number=3)
    def get_vl5x(self):
        try:
            self.session.get(self.first_url,headers=self.d_headers, timeout=180)
            cookie_jar = self.session.cookies
            cook_dic = requests.utils.dict_from_cookiejar(cookie_jar)
            print(cook_dic)
            vl5x = get_js(cook_dic)
            print(vl5x )
            return vl5x
        except Exception as e:
            print("*"*10,e)
            raise e

    @retry(stop_max_attempt_number=3)
    def get_number(self):
        try:
            data = {"guid":self.company_name}
            try:
                ret = self.session.post(self.number_url,headers=self.d_headers,data=data,timeout=180)
            except Exception as e:
                Log("./log/cp_log_6.0.log",e)
                with open("./log/except_company.csv",'a') as f:
                    f.write(self.company_name+'\n')
                return "error for get_number"
            cookie_jar = self.session.cookies
            cook_dic = requests.utils.dict_from_cookiejar(cookie_jar)
            print(cook_dic)
            number = ret.content.decode()
            print(number)
            return number
        except Exception as e:
            print("*" * 10, e)
            raise e

    @retry(stop_max_attempt_number=3)
    def get_content(self,index,vl5x):
        try:
            number = self.get_number()
            data={
            "Param":"全文检索:{}".format(self.company_name),
            "Index":str(index),
            "Page":'20',
            "Order":"法院层级",
            "Direction":"asc",
            "vl5x":vl5x,
            "number":number,
            "guid":self.company_name
            }
            ret = self.session.post(self.list_url,headers=self.d_headers,data=data,timeout=180)
            json_html = ret.content.decode()
            return json_html
        except Exception as e:
            print("*" * 10, e)
            raise e

    @retry(stop_max_attempt_number=3)
    def get_detail(self,ws_id):
        try:
            ret = self.session.get(self.d_url.format(ws_id), headers=self.d_headers, timeout=60)
            html = ret.content.decode()
            xml = etree.HTML(html)
            ws_detail = xml.xpath("//body//text()")
            return ws_detail
        except Exception as e:
            print("*" * 10, e)
            raise e

    def handel_json(self, json_html_list):
        cp_list = []
        for json_html in json_html_list:
                json_list = json.loads(json.loads(json_html))
                for info_dic in json_list[1:]:
                    try:
                        cp_one = []
                        id = info_dic["案号"]
                        date = info_dic["裁判日期"]
                        fa_yuan = info_dic["法院名称"]
                        title = info_dic["案件名称"]
                        jd = info_dic["审判程序"]
                        ws_id = info_dic["文书ID"]
                        print(ws_id)
                        ws_detail = self.get_detail(ws_id)
                        cp_one.append(id)
                        cp_one.append(date)
                        cp_one.append(fa_yuan)
                        cp_one.append(title)
                        cp_one.append(jd)
                        cp_one.append(ws_detail)
                        cp_list.append(cp_one)
                    except Exception as e:
                        print("*"*10,e)
                        cp_one = "提取信息异常"
                        cp_list.append(cp_one)
        return cp_list

    def run(self):
        try:
            json_html_list = []
            vl5x = self.get_vl5x()
            json_html = self.get_content(index=1,vl5x=vl5x)
            json_list = json.loads(json.loads(json_html))
            total_info = json_list[0]["Count"]
            item = {}
            item["company"] = self.company_name
            item["total"] = total_info
            if total_info == "0":
                print("无符合条件数据")
                item["文书信息"] = ["无符合条件数据"]
                return item
            json_html_list.append(json_html)
            t1 = int(total_info) % 20
            t2 = int(total_info) / 20
            if t1 != 0 and int(total_info) > 20:
                total_page = int(t2) + 1
            else:
                total_page = int(t2)
            print(total_page)
            # 将每一个待处理json添加到列表里，一次性传给handel_json
            if total_page >1:
                page=2
                while page <= total_page:
                    json_html = self.get_content(index=page, vl5x=vl5x)
                    json_html_list.append(json_html)
                    page += 1
            cp_list = self.handel_json(json_html_list)
            item["文书信息"] = cp_list
            print(item)
            self.session.close()
            return item
        except Exception as e:
            with open('./log/except_company.csv','a') as f:
                f.write(self.company_name+'\n')
            Log("./log/cp_log_6.log",e)
            print("*"*10,str(e))
            return "文书信息获取失败"

def main_spider(path,key_name):
    company_list = read_company2(path)
    client = pymongo.MongoClient(host='127.0.0.1', port=27017)
    conn = client["qg_ss"]['cp_info_3']
    for company in company_list:
        i = Item_dump(company, key_name)
        ret = i.item_dump()
        if not ret:
            cp = Cp_Spider(company)
            item = cp.run()
            if item != "文书信息获取失败":
                conn.insert_one(item)
                print(time.ctime(),"保存成功！")

if __name__ == '__main__':
    main_spider("E:\zhy-数据\company_list\hunan_company.csv","cp_dump_2")
