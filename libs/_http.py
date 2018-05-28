import pycurl
from StringIO import StringIO
from urllib import urlencode

from base64 import b64encode
from urllib import quote
import conf


class _HTTP_Clint(object):
    def __init__(self, IP, protocol='https', isVERBOSE=False):
        self._curl = pycurl.Curl()
        self._header_out = StringIO()
        self._body_out = StringIO()
        self._curl.setopt(pycurl.FOLLOWLOCATION, 1)
        self._curl.setopt(pycurl.COOKIEFILE, '')
        #self._curl.setopt(pycurl.COOKIEJAR, "cookie_file_name")
        if "https" == protocol:
            self._curl.setopt(pycurl.SSL_VERIFYHOST, 0)
            self._curl.setopt(pycurl.SSL_VERIFYPEER, 0)
            self._url_prefix = 'https://' + IP
        else:
            self._url_prefix = 'http://' + IP
        self._curl.setopt(pycurl.HEADERFUNCTION, self._header_out.write)
        self._curl.setopt(pycurl.WRITEFUNCTION, self._body_out.write)
        self._curl.setopt(pycurl.VERBOSE, isVERBOSE)

    def send_get_request(self, pageLocation, header=[]):
        '''
        implement HTTP GET method
        '''
        self._header_out.truncate(0)
        self._body_out.truncate(0)
        url = self._url_prefix + pageLocation
        self._curl.setopt(pycurl.HTTPHEADER, header)
        self._curl.setopt(self._curl.URL, url)
        self._curl.perform()

    def send_post_request(self, pageLocation, postData='', header=[]):
        '''
        implement HTTP POST method
        '''
        self._header_out.truncate(0)
        self._body_out.truncate(0)
        url = self._url_prefix + pageLocation
        self._curl.setopt(pycurl.HTTPHEADER, header)
        self._curl.setopt(pycurl.POSTFIELDS, postData)
        self._curl.setopt(self._curl.URL, url)
        self._curl.perform()

    def get_response_header(self):
        return self._header_out.getvalue()

    def get_response_body(self):
        return self._body_out.getvalue()

    def get_response_code(self):
        return self._curl.getinfo(self._curl.RESPONSE_CODE)

    def close_client(self):
        self._header_out.close()
        self._header_out.close()
        self._curl.close()


class HTTTPKeywords:
    #def __init__(self, DDEI_IP=conf.DDEI_IP):
    #  self.http = _HTTP_Clint(DDEI_IP)

    def login_DDEI_Via_HTTP(self, page=conf.DDD_LOGIN_PAGE, usr=conf.UI_USR, pwd=conf.UI_PWD):
        self.http = _HTTP_Clint(conf.DDEI_IP)
        postfields = 'userid=' + usr + '&password=' + pwd + '&pwdfake=' + quote(
            b64encode(pwd)) + '&sessionsetting=public'
        self.http.send_post_request(page, postfields)
        #print self.http.get_response_header()

    def register_to_uc(self, host=conf.DDD_HOST, use_proxy='0', api_key=conf.DDD_API_KEY):
        '''
        register to DDD server ,and the response is a dict
        {"register_status":3,"lastbeat_time":"2016-06-28 22:45:09","fingerprint":"1hnJSViTnRO1Bm+wVUlf\/J9ApL9ePhlNeKavIDwd18A="}
        '''
        csrf = self.get_set_cookies()
        page = conf.DDD_REGISTER_PAGE
        header = ['X-Requested-With: XMLHttpRequest']
        postfields = 'action=register&host=' + host + '&use_proxy=' + use_proxy + '&api_key=' + api_key + '&csrfp_token=' + csrf
        self.http.send_post_request(page, postfields, header)
        responseBody = self.http.get_response_body()
		# eval() not support upper case
        responseBody = responseBody.replace('false', 'False', 5)
        responseBody = responseBody.replace('true', 'True', 5)
        print 'register_to_uc response body %s' % responseBody
        return eval(responseBody)

    def unregister_from_uc(self):
        '''
        unregister to DDD server ,and the response is a dict
        {"register_status":0}
        '''
        csrf = self.get_set_cookies()
        page = conf.DDD_UNREGISTER_PAGE
        header = ['X-Requested-With:XMLHttpRequest']
        postfields = 'action=unregister&csrfp_token=' + csrf
        self.http.send_post_request(page, postfields, header)
        responseBody = self.http.get_response_body()
		# eval() not support upper case
        responseBody = responseBody.replace('false', 'False', 5)
        responseBody = responseBody.replace('true', 'True', 5)
        print 'unregister_from_uc response body  %s' % responseBody
        return eval(responseBody)

    def test_connection_with_uc(self):
        '''
        test connection to DDD server ,and the response is a dict
        {"status":1}
        '''
        csrf = self.get_set_cookies()
        page = conf.DDD_TEST_CONNECTION_PAGE
        header = ['X-Requested-With:XMLHttpRequest']
        postfields = 'action=test&csrfp_token=' + csrf
        self.http.send_post_request(page, postfields, header)
        responseBody = self.http.get_response_body()
        print 'test_connection_with_uc response body  %s' % responseBody
        return eval(responseBody)

    def update_proxy_setting_for_uc(self, isenableProxy = '0'):
        '''
        update proxy setting to DDD agent ,and the response is a dict
        {"status":1}
        '''
        csrf = self.get_set_cookies()
        page = conf.DDD_REGISTER_PAGE
        header = ['X-Requested-With:XMLHttpRequest']
        postfields = 'action=update&use_proxy='+isenableProxy+ '&csrfp_token=' + csrf
        self.http.send_post_request(page, postfields, header)
        responseBody = self.http.get_response_body()
        print 'update_proxy_setting_for_uc response body  %s' % responseBody
        return eval(responseBody)

    def get_uc_info(self):
        '''
        get uc information from DDD agent,and the response is a dict
        {"register_status":3,"err_code":0,"lastbeat_time":"2016-06-29 04:00:08","fingerprint":"kT6E77PcFfGDVjYyjqcKFkFWRmZqnW
\/\/I2Sx4QRvUy4=","hostname":"cli2.localhost.localdomain","server":"10.204.253.144","port":"443","uc_api_key"
:"eb90cff8-9254-40ee-b76b-734720965ea7","use_proxy":"0","uc_running":0,"module":""}
        '''
        csrf = self.get_set_cookies()
        page = conf.DDD_REGISTER_PAGE
        header = ['X-Requested-With:XMLHttpRequest']
        postfields = 'action=get_uc_info&csrfp_token=' + csrf
        self.http.send_post_request(page, postfields, header)
        responseBody = self.http.get_response_body()
        print 'get_uc_info response body  %s' % responseBody
        return eval(responseBody)

    #def enable_global_proxy_setting(self,enableProxy='on'):
    #    page = conf.Global_Proxy_Setting_Page
    #    header = [
    #              'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    #              'Accept-Encoding: gzip, deflate, br',
    #              'Accept-Language: en-US,en;q=0.5',
    #              'Connection: keep-alive',
    #              'Referer: https://10.204.253.141/initUpdProxyPage.ddei',
    #              'User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:44.0) Gecko/20100101 Firefox/44.0',
    #              'Content-Type: application/x-www-form-urlencoded'
    #              ]
    #    #postfields = 'useProxy=on&proxyType='+conf.AUTO_PROXY_TYPE+'&proxyAddr='+conf.AUTO_PROXY_SERVER+'&proxyPort='+conf.AUTO_PROXY_PORT+'&proxyUserName='+conf.AUTO_PROXY_USER+'&proxyPwd='+conf.AUTO_PROXY_PASS
    #    postfields = 'useProxy=on&proxyType=http&proxyAddr=10.204.253.162&proxyPort=8080&proxyUserName=&proxyPwd='
    #    self.http.send_post_request(page, postfields)
    #    print self.http.get_response_body()

    #def disable_global_proxy_setting(self):
    #    page = conf.Global_Proxy_Setting_Page
    #    self.http.send_post_request(page)
    #    print self.http.get_response_body()

    def get_set_cookies(self):
        header = self.http.get_response_header()
        first = header.find('csrfp_token=')
        header_csrf = header[first+12:]
        end = header_csrf.find(';')
        header_csrf = header_csrf[:end]
        return header_csrf

    def close_http_connection(self):
        self.http.close_client()


if __name__ == '__main__':
    http = HTTTPKeywords()
    http.login_DDEI_Via_HTTP()
    http.register_to_uc()
    pass
