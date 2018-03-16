import requests
headers = """
User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36
"""
url = "http://wenshu.court.gov.cn/CreateContentJS/CreateListDocZip.aspx?action=1"
headers = headers.split("\n")
d_headers = dict()
for h in headers:
    if h:
        k,v = h.split(":",1)
        d_headers[k] = v.strip()
# print(d_headers)
data = {
"docIds":'7fd35bf8-685b-45c8-93a2-a753009679dd|广州市白云合银泰富小额贷款股份有限公司与广州湘军商贸发展有限公司、孙军、广州印象家园公寓管理有限公司、广东京联经济发展有限公司借款合同纠纷2016民终11502二审民事裁定书|2017-04-01',
"keyCode":""
}
# session = requests.session()
ret = requests.post(url,headers=d_headers,data=data)
print(ret.content.decode())

