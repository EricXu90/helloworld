__author__ = 'jone_zhang'

from _baselib import KeywordBase
import conf
import time


class UpdateKeywords(KeywordBase):
    """
    This library contain all related keywords about update function: AU/Hotfix/Upgrade
    """

    def set_au_source(self, au_source):
        """ Set Custom AU server

        @Param:

            au_source:    the custom au source server

        Return:

            None

        Example:

        | Set AU Source | http://1.1.1.1/update |

        """
        sql_set_au_source = "update tb_global_setting set value='%s' where name='user_defined_update_server'" % au_source.strip()
        sql_check_custom_au = "select count(*) from tb_global_setting where name='user_defined_update_server'"
        sql_enable_custom_au = "update tb_global_setting set value='no' where name='DefaultServer'"
        sql_insert_au = "insert into tb_global_setting (section, name, value, inifile) values ('Update', 'user_defined_update_server', '%s', 'imss.ini')" % au_source.strip()

        if int(self.exec_sql_command_on_DDEI(sql_check_custom_au)) == 0:
            self.exec_sql_command_on_DDEI(sql_insert_au)
        else:
            self.exec_sql_command_on_DDEI(sql_set_au_source)
        self.exec_sql_command_on_DDEI(sql_enable_custom_au)


    def disable_schedule_update(self):
        """ Disable schedule update

        @Param:

            None

        Return:

            None

        Example:

        | Disable Schedule Update |

        """
        sql_enable_schedule_au = "update tb_global_setting set value='no' where name='EnableUpdateSchedule'"
        self.exec_sql_command_on_DDEI(sql_enable_schedule_au)


    def enable_schedule_update(self):
        """ Enable schedule update

        @Param:

            None

        Return:

            None

        Example:

        | Enable Schedule Update |

        """
        sql_enable_schedule_au = "update tb_global_setting set value='yes' where name='EnableUpdateSchedule'"
        self.exec_sql_command_on_DDEI(sql_enable_schedule_au)


    def set_au_proxy_server(self, server=conf.LAB_PROXY_SERVER, port=conf.LAB_PROXY_PORT, proxy_type=conf.LAB_PROXY_TYPE):
        """ Config AU proxy setting

        @Param:

            server:  proxy server ip address

            port:    proxy server port number

            type:    proxy type

        Return:

            None

        Example:

        | Set Au Proxy Server | ${Proxy_Server} | ${Proxy_Port} | ${Proxy_Type} |

        """
        sql_enable_proxy = "update tb_global_setting set value='yes' where name ='UseProxySetting'"
        sql_set_proxy_server = "update tb_global_setting set value='%s' where name ='HTTPProxy'" % server
        sql_set_proxy_port = "update tb_global_setting set value='%s' where name ='HTTPPort'" % port
        sql_set_proxy_type = "update tb_global_setting set value='%s' where name ='ProxyType'" % proxy_type

        self.exec_sql_command_on_DDEI(sql_enable_proxy)
        self.exec_sql_command_on_DDEI(sql_set_proxy_server)
        self.exec_sql_command_on_DDEI(sql_set_proxy_port)
        self.exec_sql_command_on_DDEI(sql_set_proxy_type)


    def _is_update_finish_apply(self):
        """ Check if finishing applying new components

        """
        get_au_sync_num = "grep 'au_synch_number' /opt/trend/ddei/config/scanner.info | awk -F '=' '{print $2}'"
        num_before_update = self.exec_command_on_DDEI(get_au_sync_num)
        retry = 1

        while True and retry <= 600:
            num_after_update = self.exec_command_on_DDEI(get_au_sync_num)
            if int(num_after_update) > int(num_before_update):
                return True
            time.sleep(1)
            retry += 1

    def _get_au_componnets_info(self):
        """ Get all components version info from AU server

        """
        au_info = self.exec_command_on_DDEI(conf.CMD_AU_GET_VERSION)
        return dict([(conf.UPDATABLE_COMPONENTS_COMMANDS.get(i.split()[0])[1], i.split()[1]) for i in au_info.split('\n')])


    def _get_loaded_components_info(self):
        """ Get all current loading components version

        """
        get_local_version = "grep 'version' /opt/trend/ddei/config/scanner.info"
        local_info = self.exec_command_on_DDEI(get_local_version)

        return dict([(i.split('=')[0], i.split('=')[1]) for i in local_info.split('\n')])


    def update_or_rollback_component(self, components, action='update'):
        """ Update one specific or all components

        @Param:

            components:  one or all components to be updated

            action:     update or rollback action

        Return:

            None

        Example:

        | Update Or Rollback Component | {AU_Virus_Pattern} | update |

        """
        if conf.UPDATABLE_COMPONENTS_COMMANDS.get(components) is None:
            print "The specified AU components '%s' could not be identified." % components

        if action == 'update':
            cmd = conf.CMD_AU_UPDATE
        else:
            cmd = conf.CMD_AU_ROLLBACK

        update_components_cmd = "%s %s" % (cmd, conf.UPDATABLE_COMPONENTS_COMMANDS.get(components)[0])
        result = self.exec_command_on_DDEI(update_components_cmd)

        if action == 'update' and result.find("successfully updated") == -1:
            print "Components are already up-to-date. No need to update."
            return

        if action == 'rollback':
            status_code = "".join([i.split()[1] for i in result.split('\n')])
            if status_code.find('1') == -1:
                print "No backup components to rollback."
                return

        #if not self._is_update_finish_apply():
        #    raise AssertionError("Fail to apply components: %s" % components)


    def update_should_be_successful(self, components, action='update'):
        """ Check the final loaded components should be up-to-date

        @Param:

            components:  one or all components to be updated

            action:     for update or rollback

        Return:

            None

        Example:

        | Update Should Be Successful | {AU_Virus_Pattern} | update |

        """
        au_version = self._get_au_componnets_info()
        local_version = self._get_loaded_components_info()

        if components != 'all':
            component_name = conf.UPDATABLE_COMPONENTS_COMMANDS.get(components)[1]
            self._compare_two_version(action, local_version[component_name], au_version[component_name])

        elif components == 'all':
            filter_local_version = dict([(name, local_version[name]) for name in au_version.keys()])
            for name in filter_local_version.keys():
                self._compare_two_version(action, filter_local_version[name], au_version[name])

                            
    def _compare_two_version(self, action, first_ver, second_ver):
        """ Compare the version numbers
            if action is upade, first_ver should be bigger or same as second_ver
            if action is rollback, first_ver should be smaller than second_ver

        """
        if action == 'update':
            for i in range (0, len(first_ver.split('.'))):
                if int(first_ver.split('.')[i]) < int(second_ver.split('.')[i]):
                    print first_ver + '<' + second_ver
                    raise AssertionError('Update components fail.')
                elif int(first_ver.split('.')[i]) > int(second_ver.split('.')[i]):
                    return
        elif action == 'rollback':
            for i in range (0, len(first_ver.split('.'))):
                if int(first_ver.split('.')[i]) > int(second_ver.split('.')[i]):
                    print first_ver + '>' + second_ver
                    raise AssertionError('Rollback components fail.')
                elif int(first_ver.split('.')[i]) < int(second_ver.split('.')[i]):
                    return
        else:
            raise AssertionError('Action input wrong!')


    def DB_check_should_be_successful(self, components, action='update'):
        """ Check the DB that if components are up-to-date

        @Param:

            components:  one or all components to be updated

            action:     for update or rollback

        Return:

            None

        Example:

        | DB Check Should Be Successful | {AU_Virus_Pattern} | update |

        """
        db_info = self.exec_command_on_DDEI('/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "select * from tb_active_update;"')

        loaded_ver = dict([(conf.UPDATABLE_COMPONENTS_COMMANDS.get(i.split('|')[1].strip())[1], i.split('|')[4].strip()) for i in db_info.split('\n')[2:-1] if len(i.split('|')[1].strip()) <= 2])
 
        rollback_ver = dict([(conf.UPDATABLE_COMPONENTS_COMMANDS.get(i.split('|')[1].strip()[1:].lstrip('0'))[1], i.split('|')[4].strip()) for i in db_info.split('\n')[2:-1] if len(i.split('|')[1].strip()) == 3])

        if components != 'all':
            component_name = conf.UPDATABLE_COMPONENTS_COMMANDS.get(components)[1]

            if action == 'update':
                if not rollback_ver.has_key(component_name):
                    au_ver = self._get_loaded_components_info()
                    self._compare_two_version(action, loaded_ver[component_name], au_ver[component_name])
                    return
                self._compare_two_version(action, loaded_ver[component_name], rollback_ver[component_name])
            elif action == 'rollback':
                if rollback_ver.has_key(component_name):
                    raise AssertionError("Rollback components fail.")

        elif components == 'all':
            filter_loaded_ver = dict([(name, loaded_ver[name]) for name in rollback_ver.keys()])

            if action == 'update':
                for name in rollback_ver.keys():
                    self._compare_two_version(action, filter_loaded_ver[name], rollback_ver[name])
            elif action == 'rollback':
                for name in loaded_ver.keys():
                    if rollback_ver.has_key(name):
                        raise AssertionError("Rollback components fail.")

        
