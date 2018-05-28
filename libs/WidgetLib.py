__author__ = 'Jason Li'

from _baselib import KeywordBase
try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    from robot.api import logger
except ImportError, e:
    raise ImportError('[%s] module is missing..' % str(e))
import json
import re
import cookielib
import base64


class WidgetLib():
    '''
    This library contain all related keywords about Dashboard Widget
    '''
    def __init__(self, url):
        self._client = HttpSession()
        self.url = 'https://' + url

        self._allWidgetsInfo = {}
        self._allTabsInfo = {}

    def ddei_http_get(self, u):
        return self._client.get(u)

    def ddei_http_post(self, u, **kwargs):
        return self._client.post(u, kwargs)

    def ddei_http_post_json_return_json(self, u, **kwargs):
        return self._client.post_json_return_json(u, kwargs)

    def ddei_http_post_params_return_json(self, u, **kwargs):
        return self._client.post_params_return_json(u, kwargs)



    def ddei_http_login(self, username, password):
        # get some cookie
        r = self.ddei_http_get(self.url + '/loginPage.ddei')
        #
        logger.info('Login url is ' + self.url)
        logger.info('username is ' + username)
        logger.info('password is ' + password)
        r = self.ddei_http_post(
            self.url + '/login.ddei',
            userid = username,
            password = password,
            pwdfake = base64.b64encode(password),
            sessionsetting = 'public'
            )
        logger.info('Begin to login')
        main_page = self.ddei_http_get(self.url + '/main.php')
        if main_page.find('Recipients') == -1:
            logger.info('Login failed')
            return False
        else:
            logger.info('Login successful')
            return True

    def ddei_http_logout(self):
        logout_page = self.ddei_http_get(self.url + '/timeout.ddei')
        logger.info('Begin to logout')
        if logout_page.find('Password') == -1:
            logger.info('logout failed')
            return False
        else:
            logger.info('logout successful')
            return True

    def ddei_get_value_by_key(self, dic, key):
        if key in dic:
            return dic[key]
        return None  # or raise exception


    ######################################################
    ### medium/high level
    ######################################################

    def ddei_enter_dashboard(self):
        # It is required to call this in test suite setup or case setup
        # Get userid cookies, IMPORTANT!!!
        logger.info('Entering Dashboard')
        self.ddei_http_get(self.url + '/dashboard/widget/index.php')
        # Get widgets information
        # logger.info('Getting all widgets of the dashboard')
        self.ddei_get_all_widgets_of_dashboard()

    def ddei_get_all_widgets_of_dashboard(self):
        logger.info('Getting all widgets of the dashboard')
        dic = self.ddei_http_post_json_return_json(
                self.url + '/dashboard/widget/db_controller.php?',
                act = 'getUdataAll',
                cid = '1'
                )

        self._allWidgetsInfo = dic['result']['udata']
        self._allTabsInfo = dic['result']['pdata']
        max_wid = 0
        for widget in self._allWidgetsInfo:
            num = widget['wid']
            max_wid = max(max_wid, int(num))
        self._max_wid = max_wid
        # DEBUG: print total/max wid number
        # print max_wid
        logger.info('Max wid is ' + str(max_wid))
        return


    def ddei_get_all_widgets_of_tab(self, tab):
        # getModule
        logger.info('Getting all the widgets of the tab ' + str(tab))
        return self.ddei_http_post_json_return_json(
                self.url + '/dashboard/widget/db_controller.php?',
                act = 'getModule',
                pid = tab
                )

    def ddei_update_widgets_of_tab(self, tab, udata):
        # act = udata
        logger.info('Updating widgets of the tab ' + str(tab))
        response = self.ddei_http_post_json_return_json(
                self.url + '/dashboard/widget/db_controller.php?' ,
                act = 'udata' ,
                pid = tab ,
                udata = udata
        )
        # network error or json decode fail
        if response == None:
            return None
        # maybe "OK"
        return response['response']

    def ddei_get_items_of_widget(self, module, grid_type=None):
        widget_id = -1
        # self.ddei_get_all_widgets_of_dashboard()
        for widget in self._allWidgetsInfo:
            # A little trick,
            # widget['modname'] = modHighRisk,
            # module = modWidgetHighRisk
            if widget['modname'] == (module[:3]+module[9:]):
                widget_id = int(widget['wid'])
                break
        if widget_id == -1:
            return None

        if grid_type==None:
            return self.ddei_http_post_params_return_json(
                self.url + '/dashboard/widget/proxy_controller.php?',
                module = module,
                widget_id = widget_id
                )
        else:
            return self.ddei_http_post_params_return_json(
                self.url + '/dashboard/widget/proxy_controller.php?',
                module = 'modWidgetGrid',
                widget_id = widget_id,
                grid_type = grid_type
                )

    def ddei_get_items_of_widget_by_id(self, widget_id, grid_type=None):
        module = ''
        logger.info('Finding the widget of the corresponding wid ...' + str(widget_id))
        #logger.info(self.url)
        widget_id = int(widget_id)
        for widget in self._allWidgetsInfo:
            # A little trick,
            # widget['modname'] = modHighRisk,
            # module = modWidgetHighRisk
            # logger.info(widget['wid'])
            if int(widget['wid']) == widget_id:
                modname = widget['modname']
                module = modname[:3] + 'Widget' + modname[3:]
                break
        # not found
        if module == '':
            logger.info('The widget does not exist')
            return None
        logger.info(module)
        logger.info('Find the wid')
        logger.info('Getting all items of the wid ....')

        if grid_type==None:
            return self.ddei_http_post_params_return_json(
                self.url + '/dashboard/widget/proxy_controller.php?',
                module = module,
                widget_id = widget_id
                )
        else:
            return self.ddei_http_post_params_return_json(
                self.url + '/dashboard/widget/proxy_controller.php?',
                module = 'modWidgetGrid',
                widget_id = widget_id,
                grid_type = grid_type
                )

    def ddei_test(self):
        self.ddei_get_all_widgets_of_dashboard()
        logger.info(self._allWidgetsInfo)

    def ddei_add_widget(self, tab, widget_modname):
        logger.info('Adding widget ' + widget_modname)
        # First get all widgets of the current tab
        tab_widgets = self.ddei_get_all_widgets_of_tab(tab)
        #yun_chai add...because old function did not let the old widget order+1,this will have problem
        #for single_widget in tab_widgets['result']:
        #    if single_widget['column'] == 0:
        #        single_widget['order'] += 1
        #yun_chai add...
        # Second contruct
        widgetname = widget_modname
        wid = self._max_wid + 1
        wdata = {
            'data': '',
            'modname': widgetname,
            'param': '',
            'pid': str(tab),
            'wid': wid,
            'widget_key': ''
        }
        udata = {
            'column' : 0,
            'modname' : widgetname,
            'order' : 1,
            'page' : str(tab),
            'wid' : wid,
            'widget_key' : ''
        }
        response =  self.ddei_http_post_json_return_json(
                self.url + '/dashboard/widget/db_controller.php?',
                act = 'addWidgets',
                pid = str(tab) ,
                udata = [udata] ,
                updatedOriginalUdata = tab_widgets['result'] ,
                wdata = [wdata]
        )
        # network error or json decode fail
        if response == None:
            return [None, None]
        # update widget information
        self.ddei_get_all_widgets_of_dashboard()
        return [response['response'], wid]

    def ddei_close_widget(self, tab, widget_modname):
        # get widgets of the tab,
        # it is used to update tab when closed
        response = self.ddei_get_all_widgets_of_tab(tab)
        # error
        if response == None:
            return None
        if response['response'] != 'OK':
            return None
        # get udata
        udata = response['result']

        max_id = -1
        # First check if the widget exist
        logger.info('Checking if the widget exists.....')
        # logger.info(self._allWidgetsInfo)
        for widget in self._allWidgetsInfo:
            if widget['modname'] == widget_modname:
                # Find the max wid of the same module
                # same module, different wid
                # delete the max one
                max_id = max(max_id, int(widget['wid']))
        if max_id == -1:
            return None
        wid = max_id
        # delete in db
        logger.info('Deleting the widget in DB ......')
        response = self.ddei_http_post_json_return_json(
                self.url + '/dashboard/widget/db_controller.php?' ,
                act = 'moduledelete' ,
                pid = str(tab) ,
                wid = str(wid)
        )
        # network error or json decode fail
        if response == None:
            return None
        # delete fail
        # print response['response']
        if response['response'] != 'OK':
            return None
        # delete again on UI, ask RD why this step is needed?
        logger.info('Deleting widget on the UI ....')
        response = self.ddei_http_post(
                self.url + '/dashboard/widget/proxy_controller.php?' ,
                module = 'modWidgetClose' ,
                widget_id = str(wid)

        )

        # update widget information, delete corresponding wid item in the list
        for widget in udata:
            if int(widget['wid']) == wid:
                udata.remove(widget)
        response = self.ddei_update_widgets_of_tab(tab, udata)
        self.ddei_get_all_widgets_of_dashboard()

        logger.info('Try delete finished... see result ')
        return response

    def ddei_change_widget_name(self, tab, wid, new_name):
        data = '{"wfUserData":{"widget_name":"' + new_name + '"},"wfMiscData":[{"id":"timer","data":{"timer_unit":"minutes","timer_on":true,"timer_unit_interval":600000}}]}'
        response = self.ddei_http_post_json_return_json(
                self.url + '/dashboard/widget/db_controller.php?' ,
                act = 'module' ,
                data = data ,
                pid = str(tab) ,
                wid = wid
        )
        if response == None:
            return None
        return response['response']


    def ddei_check_widget_name(self, tab, target_wid):
        response = self.ddei_http_post_json_return_json(
                self.url + '/dashboard/widget/db_controller.php?' ,
                act = 'getWdataAll' ,
                cid = '1'
        )
        # network error
        if response == None:
            return None
        if response['response'] != 'OK':
            return None

        for widget in response['result']:
            if widget['wid'] == str(target_wid):
                data = widget['data']
                dic = json.loads(data)
                if 'widget_name' in dic:
                    widgetname = dic['widget_name']
                    return widgetname
                else:
                    return None

        return None


    def ddei_change_period_time(self, target_wid, new_period, grid_type=None):
        logger.info('changing widget period time....')
        module = ''
        target_wid = int(target_wid)
        for widget in self._allWidgetsInfo:
            # A little trick,
            # widget['modname'] = modHighRisk,
            # module = modWidgetHighRisk
            if int(widget['wid']) == target_wid:
                modname = widget['modname']
                module = modname[:3] + 'Widget' + modname[3:]
                break
        if module == '':
            return None
        logger.info(module)
        if grid_type==None:
            response = self.ddei_http_post_params_return_json(
                self.url +  '/dashboard/widget/proxy_controller.php?' ,
                module = module ,
                period = new_period ,
                widget_id = target_wid
                )
        else:
            response = self.ddei_http_post_params_return_json(
                self.url +  '/dashboard/widget/proxy_controller.php?' ,
                module = 'modWidgetGrid' ,
                period = new_period ,
                widget_id = target_wid ,
                grid_type = grid_type
                )

        logger.info(response)
        logger.info('Period time has been changed.')
        if response == None:
            return None
        else:
            return response['widget_setting']['period']


    def ddei_get_period_time(self, target_wid, grid_type=None):
        logger.info('Getting widget period time....')

        response = self.ddei_get_items_of_widget_by_id(target_wid, grid_type)
        logger.info(response)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_setting' in response:
            if 'period' in response['widget_setting']:
                pass
            else:
                return None
        else:
            return None
        logger.info('Getting widget period information ...')
        return response['widget_setting']['period']


    #==============================================================================================Edit by yun_chai
    
    #
    #add tab function
    #
    def ddei_add_tab(self,tab_name):
        logger.info('add new tab....')
        #make params
        #get the already exist tab max id
        max_pid = len(self._allTabsInfo)
        #get the new tab pid and pageName
        add_pid = max_pid + 1
        pageNumber = add_pid + 1
        #make the params of the new tab        
        new_tab_param = {"sqeuenceNumber":add_pid,"pageName":tab_name,"layout":"1","icon":"","allowConfig":True,"allowClose":True,"fixedColumn":None,"eventCode":"null","pageNumber":pageNumber,"boxWidth":"","autoFit":1,"isSlideShow":1,"intIntervalSlideShow":10,"isReadOnly":False,"isDisabled":False,"container_id":1}
        TabsInfo = self._allTabsInfo
        #add the new tab info into the old disc
        TabsInfo.append(new_tab_param)
        response_add =  self.ddei_http_post_json_return_json(
                self.url + '/dashboard/widget/db_controller.php?',
                act = 'pdata',
                pdata = TabsInfo,
                cid = 1
        )
        if response_add == None:
            return None
        return [response_add['response'],pageNumber]
        # check tab infomation
        #response_save = self.ddei_get_all_widgets_of_dashboard()
        #print self._allTabsInfo
        #for tab in self._allTabsInfo:
        #    if tab['pageName'] == 'chai':
        #        print tab['sqeuenceNumber']

    #
    #delete tab function
    #
    #here tab_pid = sqeuenceNumber + 1
    def ddei_delete_tab(self,tab_pid):
        logger.info('delete the tab...' + str(tab_pid))
        pid = int(tab_pid)
        index = pid - 2
        #param
        del self._allTabsInfo[index]
        TabsInfo = self._allTabsInfo
        #this is ths delete action
        response_delete =  self.ddei_http_post_json_return_json(
                self.url + '/dashboard/widget/db_controller.php?',
                act = 'pdata',
                pdata = TabsInfo,
                cid = 1
        )
        #this is some sync action
        response_del =  self.ddei_http_post_json_return_json(
                self.url + '/dashboard/widget/db_controller.php?',
                act = 'delTab',
                pid = tab_pid
        )
        if response_delete == None:
            return None
        return response_delete['response']

    #
    #change widget position with the wid,which you want this widget to be the order_exp position
    #
    def ddei_change_widget_position(self,tab_pid,target_wid,column_exp, order_exp):
        logger.info('change widget position...' + str(target_wid))
        #get the widget Infomation of the tab,the result we can use to make the params
        response_widgetInfo = self.ddei_get_all_widgets_of_tab(tab_pid)
        #debug
        #print response_widgetInfo['result']
        #this represent if we find the target widget,then flag=1,else flag=0
        flag = 0
        for single_widget in response_widgetInfo['result']:
            #print single_widget['wid']
            if single_widget['wid'] == target_wid:
                order_index = single_widget['order']
                column_index = single_widget['column']
                single_widget['order'] = int(order_exp)
                single_widget['column'] = str(column_exp)
                flag = 1
                #print 'hehehehe'
                for single_w in response_widgetInfo['result']:
                    if column_index == str(column_exp):
                        if single_w['column'] == single_widget['column'] and single_w['wid'] != target_wid:
                            if int(order_exp) <= int(single_w['order']) < int(order_index):
                                #print 'hahaha'
                                #print single_widget['order']
                                single_w['order'] += 1
                    elif column_index != str(column_exp):
                        if single_w['column'] == single_widget['column'] and single_w['wid'] != target_wid:
                            if  int(single_w['order']) >= int(order_exp):
                                single_w['order'] += 1
                break   
        if flag == 0:
            return 'Not Found The Widget'
        #debug
        print response_widgetInfo['result']
        udata = response_widgetInfo['result']
        response_change = self.ddei_update_widgets_of_tab(tab_pid, udata)
        #print response_change
        return response_change


    #
    #check the position of the widget of the tab
    #
    def ddei_check_position_fo_widgets_of_tab(self, tab, target_wid):
        # getModule
        logger.info('Getting all the widgets of the tab ' + str(tab))
        response = self.ddei_http_post_json_return_json(
                self.url + '/dashboard/widget/db_controller.php?',
                act = 'getModule',
                pid = tab
        )
        print response['result']
        print target_wid
        for single_wid_info in response['result']:
            if single_wid_info['wid'] == target_wid:
                return single_wid_info['order']
        return 'Fail'

    #
    #widget refresh or not refresh settings,when refresh_time=1,it means Automatically refresh the widget,else not refresh,here also can change widget name
    #
    def ddei_change_widget_refresh_time(self, tab, wid, new_name, refresh_flag):
        if refresh_flag == 1:
            refresh = 'true'
        else:
            refresh = 'false'
        data = '{"wfUserData":{"widget_name":"' + new_name + '"},"wfMiscData":[{"id":"timer","data":{"timer_unit":"minutes","timer_on":"' + refresh + '","timer_unit_interval":600000}}]}'
        response = self.ddei_http_post_json_return_json(
                self.url + '/dashboard/widget/db_controller.php?' ,
                act = 'module' ,
                data = data ,
                pid = str(tab) ,
                wid = wid
        )
        if response == None:
            return None
        return response['response']

    #
    #widget(detection message) drilldown
    #
    def ddei_drilldown_of_detection(self,start_time,end_time):
        print start_time
        print end_time
        response = self.ddei_http_post(
                self.url + '/detections/log_msg.php?' ,
                start_time = start_time,
                end_time = end_time,
                ple_log_id = '1'
        )
        if response == None:
            return None
        return response

    #
    #widget(High Risk Message) drilldown
    #
    def ddei_drilldown_of_high_risk(self,start_time,end_time):
        print start_time
        print end_time
        response = self.ddei_http_post(
                self.url + '/detections/log_msg.php?' ,
                start_time = start_time,
                end_time = end_time,
                risk_level = '3',
                new_threat = '1',
                ple_log_id = '1'
        )
        if response == None:
            return None
        return response

    #
    #widget(Top Recipients) drilldown
    #
    def ddei_drilldown_of_top_recipients(self,start_time,end_time):
        print start_time
        print end_time
        response = self.ddei_http_post(
                self.url + '/detections/log_recipients.php?' ,
                start_time = start_time,
                end_time = end_time,
                ple_log_id = '1'
        )
        if response == None:
            return None
        return response

    #
    #widget(Quarantined Messages) drilldown
    #
    def ddei_drilldown_of_quarantined(self,start_time,end_time):
        print start_time
        print end_time
        response = self.ddei_http_post(
                self.url + '/detections/quarantine.php?' ,
                start_time = start_time,
                end_time = end_time,
        )
        if response == None:
            return None
        return response

    #
    #widget(Top attacker ip adddress) drilldown
    #
    def ddei_drilldown_of_attackers(self,start_time,end_time):
        print start_time
        print end_time
        response = self.ddei_http_post(
                self.url + '/detections/log_attackers.php?' ,
                start_time = start_time,
                end_time = end_time,
                ple_log_id = '1'
        )
        if response == None:
            return None
        return response

    #
    #widget(attackers map) drilldown
    #
    def ddei_drilldown_of_attackers_map(self,start_time,end_time):
        print start_time
        print end_time
        response = self.ddei_http_post(
                self.url + '/detections/log_attackers.php?' ,
                start_time = start_time,
                end_time = end_time
        )
        if response == None:
            return None
        return response

    #
    #widget(Top Subjects) drilldown
    #
    def ddei_drilldown_of_top_subjects(self,start_time,end_time):
        print start_time
        print end_time
        response = self.ddei_http_post(
                self.url + '/detections/log_subjects.php?' ,
                start_time = start_time,
                end_time = end_time,
                ple_log_id = '1'
        )
        if response == None:
            return None
        return response

    #
    #widget(Top Callback URLs) drilldown
    #
    def ddei_drilldown_of_top_callback_urls(self,start_time,end_time):
        print start_time
        print end_time
        response = self.ddei_http_post(
                self.url + '/detections/suspicious_urls.php?' ,
                start_time = start_time,
                end_time = end_time,
                drilldown_type = 'callback_urls',
                ple_log_id = '1'
        )
        if response == None:
            return None
        return response

    #
    #widget(Top Callback Hosts) drilldown
    #
    def ddei_drilldown_of_top_callback_hosts(self,start_time,end_time):
        print start_time
        print end_time
        response = self.ddei_http_post(
                self.url + '/detections/suspicious_hosts.php?' ,
                start_time = start_time,
                end_time = end_time,
                ple_log_id = '1'
        )
        if response == None:
            return None
        return response

    #
    #widget(Suspicious Objects From Sandbox) drilldown
    #
    def ddei_drilldown_of_suspicious_objects(self,start_time,end_time):
        print start_time
        print end_time
        response = self.ddei_http_post(
                self.url + '/detections/suspicious_obj.php?' ,
                start_time = start_time,
                end_time = end_time
        )
        if response == None:
            return None
        return response

    #==========================================================================================end by yun_chai


    #
    # high risk message
    #
    def ddei_high_risk_message_widget_items_should_be_empty(self, target_wid):
        logger.info('Checking if the high risk message widget is empty...')

        response = self.ddei_get_items_of_widget_by_id(target_wid)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the infomation')
        logger.info(response['widget_data'])
        for item in response['widget_data']:
            if item[4] != 0:
                return False
        return True


    #
    # detected message
    #
    def ddei_detected_message_widget_items_should_be_empty(self, target_wid):
        logger.info('Checking if the high risk message widget is empty...')

        response = self.ddei_get_items_of_widget_by_id(target_wid)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the infomation')
        logger.info(response['widget_data'])
        for item in response['widget_data']:
            if item[4] != 0:
                return False
            if item[5] != 0:
                return False
            if item[6] != 0:
                return False
        return True

    #item[4],item[5],item[6]represent high/medium/low threat
    def ddei_detected_message_widget_get_items(self, target_wid):
        """

        :rtype : object
        """
        logger.info('Getting the high risk message widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the infomation')

        high = 0
        medium = 0
        low = 0
        for item in response['widget_data']:
            if item[4] != 0:
                high += int(item[4])
            if item[5] != 0:
                medium += int(item[5])
            if item[6] != 0:
                low += int(item[6])

        return [high, medium, low]


    #
    # quarantined message
    #
    def ddei_quarantine_message_widget_should_be_empty(self, target_wid):
        logger.info('Getting the quarantine message widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the infomation')
        logger.info(response['widget_data'])
        for item in response['widget_data']:
            if item[4] != 0:
                logger.info('data not zero')
                return False
        return True

    def ddei_quarantine_message_widget_get_items(self, target_wid):
        logger.info('Getting the quarantine message widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the infomation')
        logger.info(response['widget_data'])
        quar = 0
        for item in response['widget_data']:
            #if item[4] != 0:
            quar += 1
        return quar


    #
    # top affected recipients
    #
    def ddei_top_affected_recipients_widget_should_be_empty(self, target_wid, grid_type):
        logger.info('Getting the top affected recipients message widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid, grid_type)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the infomation')
        logger.info(response['widget_data'])
        if response['widget_data']['data'] == []:
            return True
        else:
            return False

    def ddei_top_affected_recipients_widget_get_items(self, target_wid, grid_type):
        logger.info('Getting the top affected recipients message widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid, grid_type)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the infomation')
        logger.info(response['widget_data'])
        if response['widget_data']['data'] == []:
            return [0, 0, 0, 0, 0, 0]

        datas = response['widget_data']['data']
        logger.info('return the top 1 information')
        data = datas[0]
        return [data['0'], data['1'], data['2'], data['recipient'], data['count_detection'], data['high_count']]


    #
    # top attack ip
    #
    def ddei_top_attack_ip_widget_should_be_empty(self, target_wid, grid_type):
        logger.info('Getting the top attack ip widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid, grid_type)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the infomation')
        logger.info(response['widget_data'])
        if response['widget_data']['data'] == []:
            return True
        else:
            return False

    def ddei_top_attack_ip_widget_get_items(self, target_wid, grid_type):
        logger.info('Getting the top attack ip widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid, grid_type)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')
        logger.info(response['widget_data'])
        if response['widget_data']['data'] == []:
            return [0, 0]

        datas = response['widget_data']['data']
        logger.info('return the top 1 information')
        data = datas[0]
        return [data['ip'], data['country']]


    #
    # attack ip map
    #


    def ddei_attack_map_widget_get_items(self, target_wid):
        logger.info('Getting the attack map widget item...')

        res = self.ddei_http_get(self.url + '/dashboard/widget/repository/widgetPool/wp1/widget/modAttackerMap/ddei_map.php?period=1')
        if res == None:
            return None

        logger.info('Seems we have got the data')
        logger.info(res)

        data_index = res.index('{', 1) # ignore the first {
        data = res[data_index:]
        data = json.loads(data)
        logger.info(data)
        if data['direction'] == [[]]:
            logger.info('the widget is empty')
            return [0, 0, 0]

        country = data['direction'][0]['countries'][0]['name']
        ip = data['direction'][0]['countries'][0]['ips']
        count = data['direction'][0]['countries'][0]['ipscount']

        return [country, ip, count]

    def ddei_attack_map_widget_get_items_proxy(self, widget_id, grid_type):
        logger.info('Getting the attack map widget item...')

        res = self.ddei_http_post_params_return_json(
                self.url + '/dashboard/widget/proxy_controller.php?',
                module = 'modWidgetGrid',
                widget_id = widget_id,
                grid_type = grid_type
                )
        if res == None:
            return None

        logger.info('Seems we have got the data')
        logger.info(res)
        data = res['widget_data']['data']
        #logger.info(data)
        #dic = json.loads(data)
        #country = dic['city']
        #ip = dic['ip']
        #count = dic['highcount']

        return data

    #
    # top email subjects
    #
    def ddei_top_email_subjects_widget_should_be_empty(self, target_wid, grid_type):
        logger.info('Getting the top email subjects widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid, grid_type)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')
        logger.info(response['widget_data'])
        if response['widget_data']['data'] == []:
            return True
        else:
            return False

    def ddei_top_email_subjects_widget_get_items(self, target_wid, grid_type):
        logger.info('Getting the top email subjects widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid, grid_type)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')
        logger.info(response['widget_data'])
        if response['widget_data']['data'] == []:
            return [0, 0]

        datas = response['widget_data']['data']

        data = datas[0]
        return [data['subject'], data['count_detection']]

    #
    # top attachment types
    #
    def ddei_top_attachment_types_widget_should_be_empty(self, target_wid, grid_type):
        logger.info('Getting the top attachment types widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid, grid_type)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')
        logger.info(response['widget_data'])
        if response['widget_data']['data'] == []:
            return True
        else:
            return False

    def ddei_top_attachment_types_widget_get_items(self, target_wid, grid_type):
        logger.info('Getting the top attachment types widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid, grid_type)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')
        logger.info(response['widget_data'])
        if response['widget_data']['data'] == []:
            return [0, 0, 0]

        datas = response['widget_data']['data']
        logger.info('attachment data is here')
        data = datas[0]
        return [data['attach_type'], data['count_detection'], data['high_count']]


    #
    # top attachment names
    #
    def ddei_top_attachment_names_widget_should_be_empty(self, target_wid, grid_type):
        logger.info('Getting the top attachment names widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid, grid_type)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')
        logger.info(response['widget_data'])
        if response['widget_data']['data'] == []:
            return True
        else:
            return False

    def ddei_top_attachment_names_widget_get_items(self, target_wid, grid_type):
        logger.info('Getting the top attachment names widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid, grid_type)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')
        logger.info(response['widget_data'])
        if response['widget_data']['data'] == []:
            return [0,0,0]

        datas = response['widget_data']['data']
        logger.info('attachment data is here')
        data = datas[0]
        return [data['attach_name'], data['count_detection'], data['high_count']]

    #
    # processed message by risk edit by Lynn Lin
    #
    def ddei_processed_message_by_risk_widget_items_should_be_empty(self, target_wid):
        logger.info('Checking if the processed message by risk widget is empty...')

        response = self.ddei_get_items_of_widget_by_id(target_wid)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')
        logger.info(response['widget_data'])
        data = response['widget_data']['data']
        #high = data[1]
        #medium = data[2]
        #low = data[3]



        #if high == 0 and medium == 0 and low == 0:
        #    return True
        #else:
        #   return False

        # Edit by Lynn Lin

        for x in data:
            if x != 0:
               return False




    def ddei_processed_message_by_risk_widget_get_items(self, target_wid):
        logger.info('Getting the processed message by risk widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')
        logger.info(response['widget_data'])
        data = response['widget_data']['data']
        #if data == []:
        #    return [0, 0, 0]
        #high = data[1]
        #medium = data[2]
        #low = data[3]
        #return [high, medium, low]

        #Edit by Lynn Lin
        return data



    #
    # Top Callback Urls from Virtual Analyzer
    #
    def ddei_top_callback_urls_widget_should_be_empty(self, target_wid, grid_type):
        logger.info('Getting the top callback urls from VA widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid, grid_type)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')
        logger.info(response['widget_data'])
        if response['widget_data']['data'] == []:
            return True
        else:
            return False

    def ddei_top_callback_urls_widget_get_items(self, target_wid, grid_type):
        logger.info('Getting the top callback urls from VA widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid, grid_type)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the infomation')
        logger.info(response['widget_data'])
        if response['widget_data']['data'] == []:
            return [0,0,0]

        datas = response['widget_data']['data']
        logger.info('attachment data is here')
        data = datas[0]
        return [data['content'], data['count_detection'], data['high_count']]

    #
    # Top Callback Hosts from VA
    #
    def ddei_top_callback_hosts_widget_should_be_empty(self, target_wid, grid_type):
        logger.info('Getting the top callback hosts from VA widget item...')
        logger.info('A fake call of callback urls...')
        return self.ddei_top_callback_urls_widget_should_be_empty(target_wid, grid_type)

    def ddei_top_callback_hosts_widget_get_items(self, target_wid, grid_type):
        logger.info('Getting the top callback hosts from VA widget item...')
        logger.info('A fake call of callback urls...')
        return self.ddei_top_callback_urls_widget_get_items(target_wid, grid_type)

    #
    # Suspicious Objects from VA
    #
    def ddei_suspicious_objects_widget_should_be_empty(self, target_wid):
        logger.info('Getting the suspicious objects from VA widget item...')
        logger.info('A fake call of detected message...')
        return self.ddei_detected_message_widget_items_should_be_empty(target_wid)

    def ddei_suspicious_objects_widget_get_items(self, target_wid):
        logger.info('Getting the suspicious objects from VA widget item...')
        logger.info('A fake call of detected message...')
        return self.ddei_detected_message_widget_get_items(target_wid)

    #
    # Delivery Queue
    #
    def ddei_delivery_queue_widget_get_items(self, target_wid):
        logger.info('Getting the delivery queue widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')
        logger.info(response['widget_data'])
        datas = response['widget_data']
        datas = datas['mail_count']
        logger.info(datas)
        count = 0
        for i in range(0, 2):
            data = datas[i]
            count += 1

        return count

    #
    # processing volumn
    #
    def ddei_processing_volumn_widget_should_be_empty(self, target_wid):
        logger.info('Getting the processing volumn widget item...')
        logger.info('A fake call of detected message...')
        return self.ddei_detected_message_widget_items_should_be_empty(target_wid)

    def ddei_processing_volumn_widget_get_items(self, target_wid):
        logger.info('Getting the processing volumn widget item...')
        logger.info('A fake call of detected message...')
        return self.ddei_detected_message_widget_get_items(target_wid)

    #
    # Virtual Analyzer Queue
    #
    def ddei_VA_queue_widget_get_items(self, target_wid):
        pass

    #
    # Advanced Threat Indicator
    #
    def ddei_advanced_threat_widget_get_items(self, target_wid, indicator):
        logger.info('Getting the Advanced Threat Indicator widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')
        logger.info(response['widget_data'])
        datas = response['widget_data']['data']
        for data in datas:
            if data['threat_characteristic_id'] == indicator:
                count = data['count_detection']
                high = data['high']
                medium = data['medium']
                low = data['low']
                return [count, high, medium, low]


    #
    # Detection Summary widget add by Lynn Lin
    #
    def ddei_detection_summary_widget_should_be_empty(self, target_wid):
        logger.info('Getting the detection summary widget item... ')

        response = self.ddei_get_items_of_widget_by_id(target_wid)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')
        logger.info(response['widget_data'])
        for item in response['widget_data']:
            if item[4] != 0:
                return False
            if item[5] != 0:
                return False
            if item[6] != 0:
                return False
            if item[7] != 0:
                return False
            if item[8] != 0:
                return False
            if item[9] != 0:
                return False
            if item[10] != 0:
                return False
            if item[11] != 0:
                return False
        return True

    def ddei_detection_summary_widget_get_items(self,target_wid):
        logger.info('Getting the detection summary widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')

        targeted_malware = 0
        malware = 0
        malicious_url = 0
        suspicious_file = 0
        suspicious_url = 0
        phishing = 0
        spam_graymail = 0
        content_violation = 0

        for item in response['widget_data']:
            if item[4] != 0:
                targeted_malware += int(item[4])
            if item[5] != 0:
                malware += int(item[5])
            if item[6] != 0:
                malicious_url += int(item[6])
            if item[7] != 0:
                suspicious_file += int(item[7])
            if item[8] != 0:
                suspicious_url += int(item[8])
            if item[9] != 0:
                phishing += int(item[9])
            if item[10] != 0:
                spam_graymail += int(item[10])
            if item[11] != 0:
                content_violation += int(item[11])

        return [targeted_malware, malware, malicious_url,suspicious_file,suspicious_url,phishing,spam_graymail,content_violation]


    #
    # Top Policy Violations widget add by Lynn Lin
    #

    def ddei_top_policy_violations_widget_should_be_empty(self,target_wid):

        logger.info('Getting the policy violations widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')
        logger.info(response['widget_data'])
        if response['widget_data']['data'] == []:
            return True
        else:
            return False


    def ddei_top_policy_violations_widget_get_items(self,target_wid):

        logger.info('Getting the top policy violations widget item...')

        response = self.ddei_get_items_of_widget_by_id(target_wid)
        if response == None:
            logger.info('Fail to get items of the widget')
            return None
        if 'widget_data' in response:
            pass
        else:
            return None

        logger.info('Seems got the information')
        logger.info(response['widget_data'])
        if response['widget_data']['data'] == []:
            return [0,0,0]

        datas = response['widget_data']['data']
        logger.info('policy and rule data is here')
        data = datas[0]
        return [data['policy_name'], data['rule_name_0'], data['violation_count']]







class HttpSession():
    '''
    low level http get/post, internal use only
    '''
    def __init__(self):
        self.s = requests.Session()
        self.csrftoken = ''

    def post(self, url, kwargs):
        try:
            r = self.s.post(url, data=kwargs, headers={'X-CSRFTOKEN':self.csrftoken}, verify=False)
            return r.text
        except:
            return None

    def get(self, url):
        try:
            r = self.s.get(url, verify=False)

            if 'wf_CSRF_token' in self.s.cookies:
                self.csrftoken = self.s.cookies['wf_CSRF_token']
            return r.text
        except:
            return None

    def post_json_return_json(self, url, dic):
        try:
            r = self.s.post(url, data=json.dumps(dic), headers={'X-CSRFTOKEN':self.csrftoken}, verify=False)
            return r.json()
        except:
            return None

    def post_params_return_json(self, url, kwargs):
        try:
            r = self.s.post(url, data=kwargs, headers={'X-CSRFTOKEN':self.csrftoken}, verify=False)
            return r.json()
        except:
            return None


###################################
############# TEST ################
###################################
def test_login(w):

    if w.ddei_http_login('admin', 'ddei') == True:
        print 'login successful'
        return True
    else:
        print 'login failed'
        return False

def test_logout(w):
    if w.ddei_http_logout() == True:
        print 'logout successful'
    else:
        print 'logout failed'
        return

def test_getwidgetofTab(w):
    dic = w.ddei_get_all_widgets_of_tab(2)
    print 'get widget of tab result: ' + dic['response']

def test_checkwidgetitems(w):
    dic = w.ddei_get_items_of_widget_by_id(13)
    print dic

def test_addwidget(w):
    result, wid = w.ddei_add_widget(2, 'modThreatProfiles')
    print 'add widget result: ' + result
    return wid


def test_closewidget(w):
    print 'close widget result: ' + w.ddei_close_widget(2, 'modThreatProfiles')

def test_changeandcheckwidgetname(w, last_wid):
    print 'change widget name result: ' + w.ddei_change_widget_name(2, last_wid, 'nihaoya ')
    print 'widget name now is: ' + w.ddei_check_widget_name(2, last_wid)

def test_changeWidgetPeriod(w, wid, new_period):
    print 'New period is ' + w.ddei_change_period_time(wid, new_period)

if __name__ == '__main__':
    domain = '10.204.63.22'
    w = WidgetLib(domain)
    if test_login(w) == False:
        raise Exception('Exit')

    # need to call to get some cookies
    w.ddei_enter_dashboard()

    test_getwidgetofTab(w)
    test_checkwidgetitems(w)
    last_wid = test_addwidget(w)

    test_changeandcheckwidgetname(w, last_wid)
    test_changeWidgetPeriod(w, last_wid, 2)
    test_closewidget(w)
