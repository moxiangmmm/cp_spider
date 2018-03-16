# coding=utf-8
import redis
import hashlib

class Item_dump():

    def __init__(self, company, key_name):
        self.r = redis.Redis(host='127.0.0.1', port=6379, db=5) # 连接数据库
        self.item_key = key_name
        self.company = company

    def item_dump(self):
        f = hashlib.sha1()
        f.update(self.company.encode())
        fingerprint = f.hexdigest()
        added = self.r.sadd(self.item_key, fingerprint)
        # 保存成功返回false， 保存失败返回True
        return added == 0


if __name__ == '__main__':
    with open("/home/python/Desktop/company/ah_company_23316.csv",'r') as f:
        company_list = f.readlines()
    for company in company_list:
        i = Item_dump(company.strip())
        ret = i.item_dump()
        print(ret)
        if not ret:
            with open('./log/new_company.csv','a') as f:
                f.write(company)





