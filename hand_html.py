# coding=utf-8
from lxml import etree
import re
import requests
from rand_ua import Rand_ua
from logs import Log
import time
import re
class Handel_html(object):

    def __init__(self, html_list=None, html=None):
        self.html = html
        self.html_list = html_list
        self.cp_list = []

    def handel(self, html):
        xml = etree.HTML(html)
        div_list = xml.xpath("//div[@id='resultList']//div[@class='dataItem']")
        for div in div_list:
            cp_one = []
            jieduan = div.xpath(".//div[@class='label']//text()")
            jd = jieduan[0] + jieduan[1] if len(jieduan)>1 else '未获取到' # 阶段
            href = div.xpath(".//tbody//tr[1]//a/@href")
            doc_href = href[1] if len(href)>1 else "未获取到文书id"
            ws_detail = self.get_detail(doc_href)
            t = div.xpath(".//div[@class='wstitle']//a/text()")
            title = t[0] if len(t)>1 else "未获取到" # 标题
            info = div.xpath(".//tbody//tr[2]//text()") # 信息
            if len(info) > 0:
                try:
                    info_list = info[0].split("\xa0\xa0\xa0\xa0")
                    # ['深圳市福田区人民法院', '（2016）粤0304民初18775-18776号之一', '2017-07-10']
                    fa_yuan = info_list[0]
                    id = info_list[1]
                    date = info_list[2]
                except:
                    fa_yuan = '未获取到'
                    id = '未获取到'
                    date = '未获取到'
                cp_one.append(id)
                cp_one.append(date)
                cp_one.append(fa_yuan)
                cp_one.append(title)
                cp_one.append(jd)
                cp_one.append(ws_detail)
                self.cp_list.append(cp_one)

    # 检测是否有数据
    def pd_html(self):
        xml = etree.HTML(self.html)
        result = xml.xpath("//div[@id='resultList']//text()")[0]
        print(result)
        if result == "无符合条件的数据...":
            return False
        else:
            return True

    # 获取结果总数
    def get_total(self):
        if self.html != "获取网页内容时出现异常":
            xml = etree.HTML(self.html)
            total = xml.xpath("//span[@id='span_datacount']//text()")
            t = total[0] if total else "0"
            return t
        else:
            return 0

    def get_detail(self,href):
        # /content/content?DocID=b18f2733-6f07-4d42-ab8b-d1859ce3222f&KeyWord=江苏和信工程咨询有限公司'
        # http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=d47506cc-644b-4c51-bffe-a71c0102f2b9
        if href != "未获取到文书id":
            d_id = re.findall(r"DocID=(.*?)&",href)
            doc_id = d_id[0] if d_id else 0
            if doc_id:
                u = Rand_ua()
                ua = u.rand_chose()
                headers = {"User-Agent":ua}
                d_url = "http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={}".format(doc_id)
                print(d_url)
                try:
                    ret = requests.get(d_url, headers=headers, timeout=60)
                except Exception as e:
                    print("*" * 10, str(e))
                    Log('log/cp_log.log', e=e)
                    return "获取文书内容失败"
                try:
                    html = ret.content.decode()
                    # print(html)
                    xml = etree.HTML(html)
                except Exception as e:
                    print("*" * 10, str(e))
                    Log('log/cp_log.log', e=e)
                    return "获取文书内容失败"
                try:
                    ws_detail = xml.xpath("//body//text()")
                except Exception as e:
                    print("*" * 10, str(e))
                    Log('log/cp_log.log', e=e)
                    return "获取文书内容失败"
                time.sleep(2)
                return ws_detail
        else:
            return "未获取到文书id"




    def run(self):
        for html in self.html_list:
            if html == "获取网页内容时出现异常":
                return ["获取网页内容时出现异常"]
            elif re.findall(r'数据未完整，只有前\w+页,共\w+页',html):
                self.cp_list.append(html)
            else:
                self.handel(html)
        return self.cp_list


if __name__ == '__main__':
    # html_list = []
    # with open('html/深圳市中合银融资担保有限公司_1.html','r') as f:
    #     html1 = f.read()
    # with open('html/深圳市中合银融资担保有限公司_2.html','r') as f:
    #     html2 = f.read()
    # html_list.append(html1)
    # html_list.append(html2)
    # h = Handel_html(html_list)
    # cp_list = h.run()
    # print(cp_list)
    h = Handel_html()
    h.get_detail("/content/content?DocID=b18f2733-6f07-4d42-ab8b-d1859ce3222f&KeyWord=江苏和信工程咨询有限公司")



# [['（2016）京01民终7217号', '2016-12-19', '北京市第一中级人民法院', '魏巍等劳动争议二审民事判决书', '民事二审', 'http://wenshu.court.gov.cn/content/content?DocID=d4117425-9198-40a2-8a98-3711404e253b&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2017）粤03民终2926号', '2017-05-12', '广东省深圳市中级人民法院', '江西中联建设集团有限公司与', '民事二审', 'http://wenshu.court.gov.cn/content/content?DocID=5d5cf5a2-2531-416b-9516-a85101011a03&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2016）粤03民辖终3827、3828号', '2016-11-17', '广东省深圳市中级人民法院', '旭东电力集团有限公司与', '民事二审', 'http://wenshu.court.gov.cn/content/content?DocID=fe883891-d1a8-44a3-a23c-1f67a0349cb7&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2016）粤0304民初18775-18776号', '2016-09-21', '深圳市福田区人民法院', '与旭东电力集团有限公司罗云富保证合同纠纷一审民事裁定书', '民事一审', 'http://wenshu.court.gov.cn/content/content?DocID=1c55cb08-667d-48eb-9dae-a7f4010e73cc&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2016）粤0304民初18775-18776号之一', '2017-07-10', '深圳市福田区人民法院', '与旭东电力集团有限公司、罗云富保证合同纠纷一审民事裁定书', '民事一审', 'http://wenshu.court.gov.cn/content/content?DocID=197c2dfb-7520-4b7d-9598-a7f4010e73f2&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2016）京01民终7217号', '2016-12-19', '北京市第一中级人民法院', '魏巍等劳动争议二审民事判决书', '民事二审', 'http://wenshu.court.gov.cn/content/content?DocID=d4117425-9198-40a2-8a98-3711404e253b&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2017）粤03民终2926号', '2017-05-12', '广东省深圳市中级人民法院', '江西中联建设集团有限公司与', '民事二审', 'http://wenshu.court.gov.cn/content/content?DocID=5d5cf5a2-2531-416b-9516-a85101011a03&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2016）粤03民辖终3827、3828号', '2016-11-17', '广东省深圳市中级人民法院', '旭东电力集团有限公司与', '民事二审', 'http://wenshu.court.gov.cn/content/content?DocID=fe883891-d1a8-44a3-a23c-1f67a0349cb7&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2016）粤0304民初18775-18776号', '2016-09-21', '深圳市福田区人民法院', '与旭东电力集团有限公司罗云富保证合同纠纷一审民事裁定书', '民事一审', 'http://wenshu.court.gov.cn/content/content?DocID=1c55cb08-667d-48eb-9dae-a7f4010e73cc&KeyWord=深圳市中合银融资担保有限公司'],
#  ['（2016）粤0304民初18775-18776号之一', '2017-07-10', '深圳市福田区人民法院', '与旭东电力集团有限公司、罗云富保证合同纠纷一审民事裁定书', '民事一审', 'http://wenshu.court.gov.cn/content/content?DocID=197c2dfb-7520-4b7d-9598-a7f4010e73f2&KeyWord=深圳市中合银融资担保有限公司']]
'''
['$(function(){$("#con_llcs").html("浏览：0次")});$(function() {\r\n    var jsonHtmlData = "{\\"Title\\":\\"南京南拓科技发展有限公司与大丰市兴城投资开发有限公司建设工程合同纠纷一审民事判决书\\",\\"PubDate\\":\\"2015-05-06\\",\\"Html\\":\\"', '江苏省大丰市人民法院', '民 事 判 决 书', '（2014）大民初字第2177号', '原告南京南拓科技发展有限公司，住所地南京市白下区太平南路333号1幢8A室。', '法定代表人张红军，该公司执行董事。', '委托代理人刘应华、曾晨，大丰市经济开发区法律服务所法律工作者。', '被告大丰市兴城投资开发有限公司，住所地大丰市区健康东路48号（财政局四楼）。', '法定代表人卞松岭，该公司董事长。', '委托代理人韦磊，该公司员工。', '原告南京南拓科技发展有限公司（以下简称南拓公司）与被告大丰市兴城投资开发有限公司（以下简称兴城公司）建设工程合同纠纷一案，本院于2014年11月24日立案受理后，依法由审判员朱剑媚适用简易程序公开开庭进行了审理。原告南拓公司的法定代表人张红军及委托代理人刘应华、曾晨，被告兴城公司的委托代理人韦磊到庭参加诉讼。本案现已审理终结。', '原告南拓公司诉称，原、被告分别于2009年12月7日、2010年11月6日签订了《大丰湿地公园联网监控系统工程合同》、《大丰湿地公园南园景观亮化工程施工合同》，被告兴城公司将其“大丰湿地公园联网监控系统”、“大丰湿地公园南园景观亮化工程”交由原告施工，约定了工程概况、工程质量及施工安装标准、合同价款、工程进度款支付、违约责任等内容。协议签订后，原告依约积极组织人力、物力、财力进行施工，现联网监控系统工程已于2011年8月10日通过竣工验收，南园景观亮化工程于2011年12月28日完成施工并通过竣工验收，少量扫尾工作也于2012年5月底前完成。原告根据两项工程完成的工程量，于2014年6月20日通过结算审计，联网监控系统工程和南园景观亮化工程的审定价分别为1085603.19元和2032438.32元，被告至今累计已支付两项工程的工程款为2400000元，余款718041.51元未予支付。现请求判决被告给付原告联网监控系统工程款235603.19元、南园景观亮化系统工程款482438.32元，合计718041.51元，并承付该款自2014年6月21日起至实际履行之日止按中国人民银行同期流动资金贷款利率计算的利息；本案的诉讼费用由被告承担。', '被告兴城公司辩称，原告诉称的签订工程合同和施工合同，并由原告实际进行了施工且已竣工验收没有异议，后双方已就工程款结算选定了审定机构，并由该审核机构出具了相应的审核书，对审核书确定的工程价款没有异议，我公司已付工程款240万元，因为单位目前资金比较紧张，所以没有就剩余款项及时支付，愿意服从法院裁决。', '经审理查明，2009年12月7日，兴城公司（甲方）与南拓公司（乙方）签订《大丰湿地公园联网监控系统安装工程合同》一份，约定：“1、工程名称：大丰湿地公园联网监控系统。2、工程地点：大丰市。3、工程范围：大丰湿地公园联网监控系统。4、工期：按甲方要求。5、质保期：一年……合同价款玖拾玖万柒仟零玖拾陆元壹角肆分，即￥997096.14元（含税）……九、工程进度款支付：1、合同签订后一周内甲方支付合同价款的30%预付款，计￥299128.84元。2、进度款支付当月完成量的50%。3、竣工后一周内甲方支付至合同价款的85%。4、决算后一周内甲方支付至决算价款的95%。5、质保期满后一次性结清尾款……验收合格后一年保修，所有设备和系统故障均由乙方免费保修（不可抗力和人为因素除外），保修期后乙方仍提供终身维护和技术服务等”。2010年11月6日，兴城公司（甲方）与南拓公司（乙方）又签订《大丰湿地公园南园景观亮化工程施工合同》一份，约定：“1、工程名称：大丰湿地公园南园景观亮化工程。2、工程地点：大丰市城东新区东方湿地公园。3、工程范围：大丰湿地公园南园景观亮化。4、工期：按甲方要求。5、质保期：一年……合同价款暂定壹佰玖拾叁万壹仟叁佰贰拾伍元叁角玖分，即￥1931325.39元，工程结算单价、总价以大丰审计局审计结论为准……九、工程进度款支付：1、合同签订后一周内甲方支付合同价款的30%预付款，计￥579397.60元。2、进度款支付当月完成量的50%。3、竣工后一周内甲方支付至合同价款的75%。4、审计结束后一周内甲方支付至审计价的95%。5、质保期满后一周内一次性结清尾款……验收合格后一年保修，所有设备和系统故障均由乙方免费保修（不可抗力和人为因素除外），保修期后乙方仍提供终身维护和技术服务等”。合同签订后，原告依约组织人员进行了施工。', '2011年8月10日、2011年12月28日，原告分别申请对大丰湿地公园联网监控系统工程和大丰湿地公园南园景观亮化工程进行竣工验收，经上海宏波工程咨询管理有限公司同意，并在南园景观亮化工程竣工验收报告处注“符合设计及规范要求”。2014年6月20日，原告施工工程经江苏和信工程咨询有限公司审核，出具了苏和审字（2014）204号《关于大丰湿地公园景观亮化工程、联网监控系统工程结算的审核报告》，其审核结果载明：“本工程送审价为3485017.67元，审定价为3118031.51元，核减价为366986.16元。其中：景观亮化工程送审价为2212833.19元，审定价为2032438.32元，核减价为180404.87元；联网监控系统工程送审价为1272184.48元，审定价为1085603.19元，核减价为186581.29元。详见《工程结算审定单》及相应的工程结算审核书。有关该工程结算审核增减内容和金额均已与建设单位及施工单位具体核对，并由建设单位代表和施工单位代表签字认可。详见相应的工程结算审定单。”被告兴城公司合计已向原告支付了工程款240万元，但余款718031.51元未予支付，原告遂于2014年11月24日向本院提起诉讼。', '上述事实，有当事人的陈述，《大丰湿地公园联网监控系统安装工程合同》、《大丰湿地公园南园景观亮化工程施工合同》、竣工验收报告、结算审核报告、《工程结算审定单》等证据在卷证实。', '本院认为，原、被告在协商一致的基础上签订了联网监控系统安装工程和景观亮化工程施工合同，约定了各自的权利义务，该合同不违反法律、法规的禁止性规定，应为合法有效。合同签订后，原告实际进行了施工，并经验收合格、交付使用，后经双方一致认可的审计机构审核，确定了工程款的数额，被告即应按照合同的约定及双方认可的工程款数额履行工程款的支付义务，但被告仅支付了工程款240万元，余款718031.51元未予支付，原告主张被告支付工程款718041.51元，对超过718031.51元部分，本院不予支持。原告主张被告支付所欠工程款自2014年6月21日起按中国人民银行同期流动资金贷款利率计算的利息，被告没有异议，本院依法应予支持。综上，依照《中华人民共和国合同法》第四十四条、第六十条的规定，判决如下：', '被告兴城公司给付原告南拓公司工程款718031.51元，并承付该款自2014年6月21日起至实际履行之日止按中国人民银行同期同类流动资金贷款利率计算的利息。于本判决生效后十日内履行。', '案件受理费11307元，减半收取5653元，由被告兴城公司负担。', '如不服本判决，可在判决书送达之日起15日内，向本院递交上诉状，并按对方当事人的人数提出副本7份，上诉于江苏省盐城市中级人民法院。', '审判员\u3000朱\u3000 剑\u3000 媚', '二〇一五年一月二十日', '书记员\u3000朱爱云（代）', '附件', '附录法律条文', '1、《中华人民共和国合同法》', '第四十四条依法成立的合同，自成立时生效。', '法律、行政法规规定应当办理批准、登记等手续生效的，依照其规定。', '第六十条当事人应当按照约定全面履行自己的义务。', '当事人应当遵循诚实信用原则，根据合同的性质、目的和交易习惯履行通知、协助、保密等义务。', '\\"}";\r\n    var jsonData = eval("(" + jsonHtmlData + ")");\r\n    $("#contentTitle").html(jsonData.Title);\r\n    $("#tdFBRQ").html("\xa0\xa0\xa0\xa0\xa0\xa0发布日期：" + jsonData.PubDate);\r\n    var jsonHtml = jsonData.Html.replace(/01lydyh01/g, "\\\'");\r\n    $("#DivContent").html(jsonHtml);\r\n\r\n    //初始化全文插件\r\n    Content.Content.InitPlugins();\r\n    //全文关键字标红\r\n    Content.Content.KeyWordMarkRed();\r\n});']

'''
