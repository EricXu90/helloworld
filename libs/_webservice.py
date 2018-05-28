# -*- coding: utf-8 -*-

'''
Created on 2016/02/17

@author: Marvin Ma
'''

import hashlib, os, sys, shutil, zipfile, time, StringIO, pycurl, uuid, re, ConfigParser, datetime
from lxml import etree
import conf
from _baselib import KeywordBase


#DDEI_APIKEY = 'D1EC5252-EE89-11E6-A5DF-005056014677'


######## Value for testing ########
test_ip                 = conf.DDEI_IP
#test_apikey             = DDEI_APIKEY
test_protocol_version   = '1.0'
test_product_name       = 'testIMSVA'
test_client_hostname    = 'testIMSVAhost'
test_source_id          = '103'
test_source_name        = 'testIMSVA'
test_client_uuid        = 'dec48bca-1807-415d-9ffa-f587749dac96'
###################################

WEB_HOME = r'/web_service/sample_upload'
WEB_SERVICE = {
               'Register':r'{0}/register'.format(WEB_HOME),
               'TestConnection':r'{0}/test_connection'.format(WEB_HOME),
               'CheckDuplicateSample':r'{0}/check_duplicate_sample'.format(WEB_HOME),
               'UploadSample':r'{0}/upload_sample'.format(WEB_HOME),
               'GetSampleList':r'{0}/get_sample_list'.format(WEB_HOME),
               'GetSample':r'{0}/get_sample'.format(WEB_HOME),
               'GetBriefReport':r'{0}/get_brief_report'.format(WEB_HOME),
               'GetReport':r'{0}/get_report'.format(WEB_HOME),
               'GetReportBySRID':r'{0}/query_sample_info'.format(WEB_HOME),
               'GetPcap':r'{0}/get_pcap'.format(WEB_HOME),
               'GetSandboxScreenshot':r'{0}/get_sandbox_screenshot'.format(WEB_HOME),
               'GetBlackLists':r'{0}/get_black_lists'.format(WEB_HOME),
               'GetBlackListBySHA1':r'{0}/get_black_list_by_sha1'.format(WEB_HOME),
               'GetEventLog':r'{0}/get_event_log'.format(WEB_HOME),
               'Unregister':r'{0}/unregister'.format(WEB_HOME),
               'GetOpenIOCReport':r'{0}/get_openioc_report'.format(WEB_HOME),
               'GetExceptionList':r'{0}/get_exception_list'.format(WEB_HOME),
               'UploadExceptionList':r'{0}/upload_exception_list'.format(WEB_HOME),
               }

class WebServiceKeywords(KeywordBase):

    def _init_args(self):

        ####################Test Segment######################        
        self.service            = None
        self.apikey             = None
        self.host               = conf.DDEI_IP

        ####################Head Segment######################        
        self.content_type       = None
        self.content_length     = None
        self.protocol_version   = None
        self.challenge          = None
        self.time               = None
        self.checksum           = None
        self.product_name       = None
        self.client_hostname    = None
        self.client_uuid        = None
        self.source_id          = None
        self.source_name        = None
        self.last_query_id      = None
        self.body_path          = None
        self.body_content       = None
        self.checksum_calculating_order = None


        ####################Error Segment########################
        self.missing_checksum       = None
        self.invalid_content_type   = None
        self.invalid_content_length = None
        self.invalid_apikey         = None

        ####################Request Message######################        
        self.request_message = {}

    def _set_up_from_ini(self, ini_path):
        obj_ini = INI_Agent(ini_path)

        ##################Product Test Info################
        self.protocol_version   = obj_ini.get_value('Product', 'ProtocolVersion') if obj_ini.get_value('Product', 'ProtocolVersion') else None
        self.time               = obj_ini.get_value('Product', 'Time') if obj_ini.get_value('Product', 'Time') else int(time.time())
        self.challenge          = obj_ini.get_value('Product', 'Challenge') if obj_ini.get_value('Product', 'Challenge') else uuid.uuid4()
        self.product_name       = obj_ini.get_value('Product', 'ProductName') if self.service in ['Register'] else None
        self.client_hostname    = obj_ini.get_value('Product', 'ProductHost') if self.service in ['Register'] else None
        self.source_id          = obj_ini.get_value('Product', 'SourceID') if self.service in ['Register', 'UploadSample'] else None
        self.source_name        = obj_ini.get_value('Product', 'SourceName') if self.service in ['Register', 'UploadSample'] else None
        self.client_uuid        = obj_ini.get_value('Product', 'ClientUUID')
        self.last_query_id      = obj_ini.get_value('Product', 'LastQueryID') if obj_ini.get_value('Product', 'LastQueryID') else None
        self.checksum_calculating_order = obj_ini.get_value('Product', 'ChecksumCalculatingOrder') if obj_ini.get_value('Product', 'ChecksumCalculatingOrder') else None

        ##################For Generate Error##########
        self.missing_checksum       = obj_ini.get_value('Error', 'MissingChecksum')
        self.invalid_content_type   = obj_ini.get_value('Error', 'InvalidContentType')
        self.invalid_content_length = obj_ini.get_value('Error', 'InvalidContentLength')
        self.invalid_apikey         = obj_ini.get_value('Error', 'InvalidAPIKey')

        
        if self.service in ['CheckDuplicateSample', 'GetBriefReport']:
            self.content_type = 'text/plain'
        elif self.service in ['UploadSample']:
            self.content_type = 'application/x-compressed'
        elif self.service in ['UploadExceptionList']:
            self.content_type = 'text/xml'
            self.body_path = obj_ini.get_value('ForUploadException', 'ExceptionListPath')
        else:
            self.content_type = None

        if self.invalid_content_type:
            self.content_type = self.invalid_content_type
        
        if self.invalid_content_length:
            self.content_length = self.invalid_content_length
         
        if self.invalid_apikey:
            self.apikey = self.invalid_apikey
        else:
            self.apikey = self._get_apikey()

    def _set_up_default(self):
        self.client_hostname    = test_client_hostname  if self.service in ['Register'] else None
        self.product_name       = test_product_name     if self.service in ['Register'] else None
        self.source_id          = test_source_id        if self.service in ['Register', 'UploadSample'] else None
        self.source_name        = test_source_name      if self.service in ['Register', 'UploadSample'] else None
        self.time               = int(time.time())
        self.challenge          = uuid.uuid4()
        self.client_uuid        = test_client_uuid
        self.apikey             = self._get_apikey()
        self.protocol_version   = test_protocol_version

    def _get_header_array(self):
    ################ Purpose ################
    # 1. Create header array by Header class
    # 2. Append checksum
    #########################################

        checksum_dict = {}
        checksum_list = []
        head_array = []

        # APIKey must be the first value of checksum
        self.request_message['apikey'] = self.apikey
        checksum_list.append(self.apikey)
        self.request_message['service'] = self.service

        if self.time:
            self.request_message['time'] = self.time
            head_array.append("X-DTAS-Time: " + str(self.time))
            checksum_dict['X-DTAS-Time'] = str(self.time)
        if self.challenge:
            self.request_message['challenge'] = self.challenge
            head_array.append("X-DTAS-Challenge: " + str(self.challenge))
            checksum_dict['X-DTAS-Challenge'] = str(self.challenge)
        if self.protocol_version:
            self.request_message['protocol_version'] = self.protocol_version
            head_array.append("X-DTAS-ProtocolVersion: " + str(self.protocol_version))
            checksum_dict['X-DTAS-ProtocolVersion'] = self.protocol_version
        if self.host:
            self.request_message['host'] = self.host
            head_array.append("Host: " + self.host)
        if self.body_path:
            self.request_message['body_path'] = self.body_path
            self.body_content = open(self.body_path, 'r').read()
            self.content_length = str(self.content_length) if self.content_length else str(len(self.body_content))
        else:
            self.body_content = None
        if self.content_type:
            self.request_message['content_type'] = self.content_type
            head_array.append("Content-Type: " + self.content_type)
        if self.content_length:
            self.request_message['content_length'] = self.content_length
            head_array.append("Content-Length: " + self.content_length)
        if self.product_name:
            self.request_message['product_name'] = self.product_name
            head_array.append("X-DTAS-ProductName: " + str(self.product_name))
            checksum_dict['X-DTAS-ProductName'] = str(self.product_name)
        if self.client_hostname:
            self.request_message['client_hostname'] = self.client_hostname
            head_array.append("X-DTAS-ClientHostname: " + str(self.client_hostname))
            checksum_dict['X-DTAS-ClientHostname'] = str(self.client_hostname)
        if self.source_id:
            self.request_message['source_id'] = self.source_id
            head_array.append("X-DTAS-SourceID: " + str(self.source_id))
            checksum_dict['X-DTAS-SourceID'] = str(self.source_id)
        if self.source_name:
            self.request_message['source_name'] = self.source_name
            head_array.append("X-DTAS-SourceName: " + str(self.source_name))
            checksum_dict['X-DTAS-SourceName'] = str(self.source_name)
        if self.client_uuid:
            self.request_message['client_uuid'] = self.client_uuid
            head_array.append("X-DTAS-ClientUUID: " + str(self.client_uuid))
            checksum_dict['X-DTAS-ClientUUID'] = str(self.client_uuid)
        if self.last_query_id:
            self.request_message['last_query_id'] = self.last_query_id
            head_array.append("X-DTAS-LastQueryID: " + str(self.last_query_id))
            checksum_dict['X-DTAS-LastQueryID'] = str(self.last_query_id)

        if self.checksum_calculating_order:
            self._write_test_log("Checksum Order: %s" % self.checksum_calculating_order)
            order_list = self.checksum_calculating_order.split(',')
            for order in order_list:
                self._write_test_log(order)
                if checksum_dict.has_key(order):
                    checksum_list.append(checksum_dict[order])
            self.request_message['checksum_calculating_order'] = self.checksum_calculating_order
            head_array.append("X-DTAS-ChecksumCalculatingOrder: " + str(self.checksum_calculating_order))
        else:
            self._write_test_log("Checksum Order: Default")
            for head in head_array:
                tmp = head.split(':')[0]
                if checksum_dict.has_key(tmp):
                    self._write_test_log(tmp + '----------' + checksum_dict[tmp])
                    checksum_list.append(checksum_dict[tmp])

        # Get request checksum
        self.checksum = self._get_checksum_sha1(checksum_list, self.body_content)

        if self.missing_checksum:
            pass
        else:
            self.request_message['checksum'] = self.checksum
            head_array.append("X-DTAS-Checksum: " + self.checksum)

   
        # Avoid keep alive too long
        head_array.append("Connection: close")
        self._write_test_log("Header: " + str(head_array))

        return head_array

    def _get_checksum_sha1(self, checksum_list, body_content):
    ################ Purpose ################
    # Calculate checksum of 
    # header, file and body_content
    #########################################
        string = ""

        for value in checksum_list:
            string = string + str(value)
        if body_content:
            string = string + str(body_content)
        self._write_test_log("Checksum to calculate: %s" % string)
        checksum = hashlib.sha1(string).hexdigest()
        return checksum

    def _get_apikey(self):
    ################ Purpose ################
    # Calculate checksum of 
    # header, file and body_content
    #########################################        
        self.connect_to_DDEI()
        self.login_DDEI()
        apikey = self.exec_sql_command_on_DDEI("select value from tb_global_setting where section = 'WebServiceAPI' and name = 'apikey';")
        print "APIKey:", apikey
        return apikey.upper()
        
    
    def send_request(self, service, ini_path = None, removed_header_seg=None):

        '''
        [SERVICE]
        
        TestConnection
        Register
        Unregister
        GetExceptionList
        UploadExceptionList
        GetBlackLists
        
        '''
        self.update_testdata_exceptionlist_path()
        self._init_args()
        self.service = service        
        url  = "https://" + conf.DDEI_IP + WEB_SERVICE[self.service]
        ini_path           = os.path.join(conf.TEST_DATE_DIR, 'webservice', ini_path)

        if ini_path:
            self._write_test_log("set up ProductTestInfo from %s" % ini_path)
            self._set_up_from_ini(ini_path)
        else:
            self._write_test_log("set up ProductTestInfo from default")
            self._set_up_default()

        #remove some request header segment to create fatal
        if removed_header_seg:
            if self.__dict__.has_key(removed_header_seg):
                self.__dict__[removed_header_seg] = None
            else:
                raise Exception("specified segment is not in request header")

        request_head = self._get_header_array()

        print url
        print request_head
        
        return_body = StringIO.StringIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.VERBOSE, False)
        curl.setopt(pycurl.HTTPHEADER, request_head)
        curl.setopt(pycurl.WRITEFUNCTION, return_body.write)
        curl.setopt(pycurl.USERAGENT, 'curl')
        curl.setopt(pycurl.CONNECTTIMEOUT, 10)
        curl.setopt(pycurl.TIMEOUT, 600)
        curl.setopt(pycurl.SSL_VERIFYHOST, 0)
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)

        if self.body_path:
            curl.setopt(pycurl.UPLOAD, 1)
            curl.setopt(pycurl.READDATA, open(self.body_path, 'r'))
            if removed_header_seg == 'content_length':
                pass
            else:
                curl.setopt(pycurl.INFILESIZE, int(self.content_length))
        
        try:
            self._write_test_log("=====>Start performing request %s" % self.service)
            curl.perform()
            self._write_test_log("=====>Finish performing request %s" % self.service)
        except pycurl.error, (code, msg):
            if code == pycurl.E_GOT_NOTHING:
                pass
            else:
                self._write_test_log("[CULR ERROR] (%s,%s)" % (code , msg))
        except Exception, e:
            self._write_test_log("Exception: %s" % e)

        return_code = curl.getinfo(pycurl.HTTP_CODE)
        return_body = return_body.getvalue()
        curl.close()
        self._write_test_log("return code: {0}".format(return_code))
        self._write_test_log("return body:\n{0}".format(return_body))
        return return_code, return_body


    def check_response_schema(self, return_body, xsd, report_num=0):
        xmlschema_doc = etree.parse(os.path.join(conf.TEST_DATE_DIR, 'webservice', xsd))
        xmlschema = etree.XMLSchema(xmlschema_doc)
        doc = etree.fromstring(return_body)
        result_num = len(doc.findall('.//REPORT'))
        if xmlschema.validate(doc):
            self._write_test_log("return body schema validate successfully.")
            if report_num != 0:
                if result_num != int(report_num):
                    self._write_test_log("report number validate failed, expected: %s, return: %s " % (report_num, str(result_num)))
                    return False
                else:
                    self._write_test_log("report number validate successfully")
                    return True
        else:
            log = xmlschema.error_log
            error = log.last_error
            self._write_test_log(str(error))
            self._write_test_log("return body schema  validate failed.")
            return False
        return True
        
    def update_testdata_exceptionlist_path(self):
        data_folder = os.path.join(conf.TEST_DATE_DIR, 'webservice')
        key = 'ExceptionListPath'

        to_update_files = [i for i in os.listdir(data_folder) if i.endswith('ini') and os.path.isfile(os.path.join(data_folder, i))]

        for i in to_update_files:
            fr = open(os.path.join(data_folder, i), 'r')
            r_content = fr.readlines()
            w_content = []
            
            for a in r_content:
                if key in a:
                    fname = os.path.basename(a.split()[-1].split('=')[-1])
                    a = "%s = %s\n" % (key, os.path.join(data_folder, fname))
                w_content.append(a)
                
            fw=open(os.path.join(data_folder, i), 'w')
            fw.writelines(w_content)
            fr.close()
            fw.close()

    def check_response_element(self, return_body, element):
        doc = etree.fromstring(return_body)
        e_list = []
        '''
        self._write_test_log("root: {0}".format(doc.tag))
        self._write_test_log("root: {0}".format(doc.attrib))
        for child in doc:
            self._write_test_log("child tag: {0},    child attrib: {1}".format(child.tag, child.attrib))
        '''
        for report in doc.findall('.//REPORT'):
            e = report.find(element).text
            e_list.append(e)
        return e_list
        
        
        
        

class INI_Agent:
    def __init__(self, ini_path):
        try:
            self.path = os.path.join(conf.TEST_DATE_DIR, 'webservice', ini_path);
            if os.path.exists(self.path):
                self.config = ConfigParser.ConfigParser();
                self.config.optionxform = str;
                self.config.read(self.path);
            else:
                raise Exception, "File not exist!"
        except Exception, e:
            print "__init__() got exception: ", sys.exc_info()[:2];

    def get_value(self, section, key, default_value = ''):
        
        try:
            ini_value = self.config.get(section, key);
            if len(ini_value) == 0:
                ini_value = default_value;
            return ini_value;
        
        except ConfigParser.NoSectionError:
            pass
        except ConfigParser.NoOptionError:
            pass
        except Exception, e:
            print "get_value() got exception: ", sys.exc_info()[:2];

    def set_value(self, section, key, value):
        try:
            print "set_value(): section is %s, key is %s, value is %s" % (section, key, value);
            self.config.set(section, key, value);
            self.config.write(open(self.path, "w"));
        except Exception, e:
            print "set_value() got exception: ", sys.exc_info()[:2];


if __name__ == '__main__':
    ########clear up testlog########
    test_log_path = os.path.join(conf.TEST_LOG_DIR, conf.CASE_ID, 'testlog.log')
    if os.path.exists(test_log_path):
        os.remove(test_log_path)
    ################################
    base = WebServiceKeywords()
    #code, body = base.send_request('Register', 'test_valid_checksum_order.ini')
    code, body = base.send_request('GetExceptionList', 'test_info.ini')
    print code
    print body
    #print base.check_response_schema(body, 'get_black_lists.xsd', 12)
    base.check_response_element(body, 'ID')

    
    
    
    
