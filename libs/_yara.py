__author__ = 'marvin_ma'

import os, simple_json, time
from _http_requests import _Http_Requests
from _baselib import KeywordBase
import conf

YARA_URL = '/php/yara.php'

class YaraKeywords(KeywordBase):
    """
    This library contain all related keywords about update function: Yara Rules
    """
    def get_yara_csrf_token(self):
        try:
            ui = _Http_Requests()
            code, resp = ui.http_post(YARA_URL, {'action': 'get', 'rows': '20', 'page': '1', 'sidx': 'add_time', 'sord': 'desc'})
            response = simple_json.loads(resp)
            return response.get('token')
        except:
            raise Exception("get new_token failed.")
                    

    def get_yara(self, rows=20, page=1, sidx='add_time', sort='desc'):
        print "start getting yara..."
        ui = _Http_Requests()
        
        form_data = {}
        form_data['action'] = 'get'
        form_data['rows'] = rows
        form_data['page'] = page
        form_data['sidx'] = sidx
        form_data['sord'] = sort
        form_data['_search'] = 'false'
        code, resp = ui.http_post(YARA_URL, form_data)
        with open(os.path.join(conf.TEST_LOG_DIR, 'get_yara_result.log'), 'wb') as f:
            f.write(str(resp))
        if code != 200:
            raise StandardError("import yara failed, http response code: {0}".format(code))
        else:
            response = simple_json.loads(resp)
            return response.get('rows')
            


    def import_yara(self, risk_level, analyze_type, file_name):
        print "start importing yara..."
        ui = _Http_Requests()
        
        form_data = {}
        form_data['action'] = 'import'
        form_data['risk_level'] = risk_level
        form_data['file_type'] = analyze_type
        form_data['token'] = self.get_yara_csrf_token()
        form_data['rule_content_change'] = 'True'
        
        file = []
        file_path = os.path.join(conf.TEST_DATE_DIR, 'yara', file_name)
        with open(file_path, 'rb') as f:
            file.append(('yara_file', file_name, f.read()))
        code, resp = ui.http_post(YARA_URL, form_data, file)
        with open(os.path.join(conf.TEST_LOG_DIR, 'import_yara_result.log'), 'wb') as f:
            f.write(str(resp))
        if code != 200:
            raise StandardError("import yara failed, http response code: {0}".format(code))
        else:
            response = simple_json.loads(resp)
            return response.get('success')
            
    def delete_all_rules(self):
        print "start deleting all yaras..."
        ui = _Http_Requests()
        
        yaras = self.get_yara()
        ids = []
        for yara in yaras:
            ids.append(yara['id'])

        form_data = {}
        form_data['action'] = 'delete'
        form_data['token'] = self.get_yara_csrf_token()
        form_data['ids'] = ','.join(str(id) for id in ids)
        code, resp = ui.http_post(YARA_URL, form_data)
        if code != 200:
            raise StandardError("import yara failed, http response code: {0}".format(code))
        else:
            response = simple_json.loads(resp)
            return response.get('success')
        
if __name__ == '__main__':
    y = YaraKeywords()
    y.import_yara(risk_level='3', analyze_type='*', file_name='yara_normal.txt')
    print y.get_yara()
    y.delete_all_rules()
    

	