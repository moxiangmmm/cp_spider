
def make_header(headers):
    header = headers.split("\n")
    d_headers = dict()
    for h in header:
        if h:
            k,v = h.strip().split(":",1)
            d_headers[k] = v.strip()
    return d_headers

if __name__ == '__main__':
    headers = """
Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Encoding:gzip, deflate
Accept-Language:zh-CN,zh;q=0.9
Cache-Control:max-age=0
Connection:keep-alive
Host:wenshu.court.gov.cn
Upgrade-Insecure-Requests:1
User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36
"""
    print(make_header(headers))