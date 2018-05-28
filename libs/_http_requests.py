import urllib, urllib2, os, cookielib, types, ssl, httplib, mimetypes, mimetools
from StringIO import StringIO
from base64 import b64encode
import conf

ssl._create_default_https_context = ssl._create_unverified_context 

if not os.access(conf.TEST_LOG_DIR, os.F_OK):
    os.mkdir(conf.TEST_LOG_DIR)

class _Http_Requests():
    def __init__(self):
        self._cookie = os.path.join(conf.TEST_LOG_DIR,'cookie.txt')
        
    def _login(self):
        login_data = {'userid': conf.UI_USR, 'password': conf.UI_PWD, 'pwdfake': b64encode(conf.UI_PWD), 'sessionsetting': 'public'}
        login_url = 'https://' + conf.DDEI_IP + conf.DDD_LOGIN_PAGE
        try:
            os.remove(self._cookie)
        except:
            pass
        print "login to DDEI..."
        code, content = self._post(login_url, login_data)
        if code != 200 or 'invalid' in content:
            raise Exception("LoginError")
        return 0


    def _post(self, url, data, file=None):
        """
        Used to post data to web application and get the response.
        :Parameters:
            uri: string
                The URI to launch.
            data: string/tuple/dictionary
                The data that need to send to server.
            file:
                The file that need to send to server
            cookie: object
                The cookie that need to send to server.
        :Return:
                The response object if no error occur. Any error will cause exception.
        """    
        cookieJar = cookielib.MozillaCookieJar(self._cookie)
        if os.path.isfile(self._cookie):
            cookieJar.load(None, True)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar));
        urllib2.install_opener(opener)

        if file:
            content_type, body = encode_multipart_formdata(data, file)
            headers = {'Content-Type': content_type, 'Content_length': str(len(body))}
            '''
            with open(os.path.join(conf.TEST_LOG_DIR, 'post_content.txt'), 'wb') as f:
                f.write(str(body))
            '''
            r = urllib2.Request(url, body, headers)
            with open(os.path.join(conf.TEST_LOG_DIR, 'post_info.log'), 'wb') as f:
                f.write(url + '\n\n\n\n\n')
                f.write(str(headers) + '\n\n\n\n\n')
                f.write(body)
            resp = urllib2.urlopen(r)
        else:
            if type(data) is types.DictionaryType or type(data) is types.TupleType:
                data = encodeurl(data, doseq=0, safe='\\x')
            with open(os.path.join(conf.TEST_LOG_DIR, 'post_info.log'), 'wb') as f:
                f.write(url + '\n\n\n\n\n')
                f.write(data)
            resp = opener.open(url, data)
            
        code = resp.getcode()
        try:
            response = resp.read()
        except:
            response = ''
        cookieJar.save(None, True)
        return code, response

    def _get(self, url, data={}):
        """
        Used get method to access DDEI web application and get the response.

        :Parameters:
            uri: string
                 The URI to launch.
        :Return:
        The return code and content
        exception.
        """
        cookieJar = cookielib.MozillaCookieJar(self._cookie)
        if os.path.isfile(self._cookie):
            cookieJar.load(None, True)
        else:
            cookieJar = None

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar));
        if data != {}:
            data = encodeurl(data)
            url +='?'+data
        resp = opener.open(url)
        if cookieJar is not None:
            cookieJar.save(None, True)
        code = resp.getcode()
        try:
            response = resp.read()
        except:
            response = ''

        return code, response


    def _check_session(self):
        """
        " this function verify whehter the cookie is valid, if not valid, then call _login()
        """
        try:
            code, content = self._get('https://' + conf.DDEI_IP + '/html/license.html')
            if 'parent.parent.location.href="/loginPage.ddei"' in content or 'parent.parent.location.href="/timeout.ddei"' in content:
                return 1
            else:
                return 0
        except Exception, e:
            return 1


    def http_get(self, url, data={}):
        '''
        ' this function return the code and content of the URL
        ' parameters:
        '     ip: dda ip address: 10.204.253.205
        '     url: the url that we want to get data from , like /mediall/&&&&/llog.html?aa=22,bb=cc; not include the https://ip
        ' return:
        '     code: return code, 200 is success
        '     content: the respose content, str type
        '''
        url = 'https://' + conf.DDEI_IP.strip() + url
        if self._check_session() != 0:
            self._login()
        code, content = self._get(url, data)
        return code, content


    def http_post(self, url, data={}, file=None):
        '''
        ' this function post the data to the URL, return the code and content of the post action
        ' parameters:
        '     ip: ddei ip address: 10.204.253.205
        '     url: the url that we want to get data from , like /php/license.php, not include the https://ip
        '     data: dist type: {'username':'ddei','password':'admin!'}
        ' return:
        '     code: return code, 200 is success
        '     content: the respose content, str type
        
        unquote_special: 0 means don't unquote the special, when value have [] or ", need to enable this func
        if enable this, DBCS characters may have error
        '''
        url = 'https://' + conf.DDEI_IP.strip() + url
        if self._check_session() != 0:
            print "check session failed"
            self._login()
        return self._post(url, data, file)

def encode_multipart_formdata(fields, file):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = mimetools.choose_boundary()
    CRLF = '\r\n'
    L = []
    for (key, value) in fields.items():
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    if file:
        for (key, filename, value) in file:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % mimetypes.guess_type(filename)[0] or 'application/octet-stream')
            L.append('')
            L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')

    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def encodeurl(query, doseq=0, safe=''):
    """Encode a sequence of two-element tuples or dictionary into a URL query string.

    If any values in the query arg are sequences and doseq is true, each
    sequence element is converted to a separate parameter.

    If the query arg is a sequence of two-element tuples, the order of the
    parameters in the output will match the order of parameters in the
    input.
    """
    if hasattr(query,"items"):
        # mapping objects
        query = query.items()
    else:
        # it's a bother at times that strings and string-like objects are
        # sequences...
        try:
            # non-sequence items should not work with len()
            # non-empty strings will fail this
            if len(query) and not isinstance(query[0], tuple):
                raise TypeError
            # zero-length sequences of all types will get here and succeed,
            # but that's a minor nit - since the original implementation
            # allowed empty dicts that type of behavior probably should be
            # preserved for consistency
        except TypeError:
            ty,va,tb = sys.exc_info()
            raise TypeError, "not a valid non-string sequence or mapping object", tb
    l = []
    if not doseq:
        # preserve old behavior
        for k, v in query:
            k = urllib.quote(str(k),safe)
            v = urllib.quote(str(v).replace('\'','"'), safe)  # add the replace for php can't get the %27 and %22
            l.append(k + '=' + v)
    else:
        for k, v in query:
            k = urllib.quote_plus(str(k), safe)
            if isinstance(v, str):
                v = urllib.quote_plus(v, safe)
                l.append(k + '=' + v)
            elif _is_unicode(v):
                # is there a reasonable way to convert to ASCII?
                # encode generates a string, but "replace" or "ignore"
                # lose information and "strict" can raise UnicodeError
                v = urllib.quote_plus(v.encode("utf-8","replace"))
                l.append(k + '=' + v)
            else:
                try:
                    # is this a sufficient test for sequence-ness?
                    x = len(v)
                    ty = type(v)
                except TypeError:
                    # not a sequence
                    v = urllib.quote(str(v))
                    l.append(k + '=' + v)
                else:
                    # loop over the sequence
                    l.append(k +'=' +str(v).replace('\'','"'))
                    #for elt in v:
                    #    l.append(k + '=' + urllib.quote_plus(str(elt)))
    final_query = '&'.join(l).replace('\\x','%').replace(' ','') # ADDED for DBCS characters.
    return final_query
		
if __name__ == '__main__':
    ui = _Http_Requests()
    ui.http_post('/php/license.php', urllib.urlencode({'ac_id': 'default'}))
