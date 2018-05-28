#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-04-05 17:31:22
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Version : 2.5SP1

# System modules
import os
import time

# Custom modules
from _baselib import KeywordBase
import conf

class SpsKeywords(KeywordBase):
    """ Keywords for integrating with wanSmart Protection Server """

    def add_sps(self, server_uuid, sps_ip, sps_port):
        """ Insert a Smart Protection Server info into database

        Param:

            server_uuid: 	id used for identify a Smart Protection Server
            sps_ip: 		IP address of a Smart Protection Server
            sps_port: 		port lisent by a Smart Protection Server

        Return:

            None

        Example:

            | Add SPS | 78918c9a-1a05-4710-bff1-3dbaa066dac7 | 192.168.1.1 | 5274 |

        """
        # Local variables
        sql_add_sps = "insert into tb_smart_protection_server (server_uuid, host, port_wr, enable_proxy, support_rp, use_certificate, use_crl) values('%s', '%s', %s, 0, 1, 0, 0)"

        # Prepare SQL statement
        # SQL for insert a SPS server
        stmt = sql_add_sps % (server_uuid, sps_ip, sps_port)

        # Execute SQL statement
        try:
            self.exec_sql_command_on_DDEI(stmt)
        except Exception as err:
            print("Fail to add a Smart Protection Server to DB for: %s" % err)
            raise

    def delete_sps(self, server_uuid=None):
        """ Delete the Smart Protection Server from DB

        Param:

            server_uuid:    id used for identify a Smart Protection Server

        Return:

            None

        Example:

            | Delete SPS | 78918c9a-1a05-4710-bff1-3dbaa066dac7 |

        """
        # Prepare SQL statment
        # SQL for delete a SPS server
        if not server_uuid:
            sql_remove_sps = "delete from tb_smart_protection_server;"
        else:
            sql_remove_sps = "delete from tb_smart_protection_server where server_uuid='%s';" % server_uuid

        # Execute SQL statment
        try:
            self.exec_sql_command_on_DDEI(sql_remove_sps)
        except Exception as err:
            print("Fail to delete a Smart Protection Server for: %s" % err)
            raise

    def enable_sps(self):
        """ Enable to use local Smart Protection Server

        Param:

            None

        Return:

            None

        Example:

            | Enable SPS |

        """
        sql_enable_sps = "update tb_global_setting set value=1 where section='smart_scan' and name='use_local';"
        # Execute SQL statment
        try:
            self.exec_sql_command_on_DDEI(sql_enable_sps)
        except Exception as err:
            print("Fail to enable to use local Smart Protection Server for: %s" % err)
            raise

    def disable_sps(self):
        """ Disable to use local Smart Protection Server

        Param:

            None

        Return:

            None

        Example:

            | Disable SPS |
        """
        sql_disable_sps = "update tb_global_setting set value=0 where section='smart_scan' and name='use_local';"

        # Execute SQL statment
        try:
            self.exec_sql_command_on_DDEI(sql_disable_sps)
        except Exception as err:
            print("Fail to disable to use local Smart Protection Server for: %s" % err)
            raise

    def support_reverse_proxy(self):
        """ Enable to support reverse proxy

        Param:

            None

        Return:

            None

        Example:

            | Support Reverse Proxy |
        """
        sql_support_rp = "update tb_smart_protection_server set support_rp=1;"
        try:
            self.exec_sql_command_on_DDEI(sql_support_rp)
        except Exception as err:
            print "Fail to set support reverse proxy for %s." % err
            raise

    def not_support_reverse_proxy(self):
        """ set not to support reverse proxy

        Param:

            None

        Return:

            None

        Example:

            | Not Support Reverse Proxy |
        """
        sql_not_support_rp = "update tb_smart_protection_server set support_rp=0;"
        try:
            self.exec_sql_command_on_DDEI(sql_not_support_rp)
        except Exception as err:
            print "Fail to set not to support reverse proxy for %s." % err
            raise

    def enable_reverse_proxy(self):
        """ Enable to use local Smart Protection Server

        Param:

            None

        Return:

            None

        Example:

            | Enable Reverse Proxy |

        """
        sql_enable_RP = "update tb_global_setting set value=1 where section='smart_scan' and name='use_sps_as_proxy';"
        # Execute SQL statment
        try:
            self.exec_sql_command_on_DDEI(sql_enable_RP)
        except Exception as err:
            print("Fail to enable reverse proxy for: %s" % err)
            raise

    def disable_reverse_proxy(self):
        """ Disable to use local Smart Protection Server

        Param:

            None

        Return:

            None

        Example:

            | Disable Reverse Proxy |
        """
        sql_disable_RP = "update tb_global_setting set value=0 where section='smart_scan' and name='use_sps_as_proxy';"
        # Execute SQL statment
        try:
            self.exec_sql_command_on_DDEI(sql_disable_RP)
        except Exception as err:
            print("Fail to disable reverse proxy for: %s" % err)
            raise

    def import_certificate(self, ca_file):
        """ Import a root certificate

        Param:

            ca_file: certificate file (along with absolute path)

        Return:

            None

        Example:

            | Import Certificate | /root/testdata/ca-chain.pem |
        """
        # Destinate location of certificate file after importing
        dst = conf.RP_CERT_PATH

        # Upload certificate file to product
        try:
            self.upload_file_to_DDEI(ca_file, dst)
        except Exception as err:
            print("Fail to upload certificate file for: %s" % err)
            raise

    def import_crl(self, crl_file):
        """ Import a certificate revocation list

        Param:

            crl_file: certificate revocation list

        Return:

            None

        Example:

            | Import CRL | /root/testdate/crl.pem |
        """
        # Destinate location of CRL list after importing
        dst = conf.RP_CRL_PATH

        # Upload CRL to product
        try:
            self.upload_file_to_DDEI(crl_file, dst)
        except Exception as err:
            print("Fail to upload CRL for: %s" % err)
            raise

    def enable_sps_use_proxy(self):
        """ Enable connect Smart Protection Server through proxy

        Param:

            None

        Return:

            None

        Example:

            | Enable SPS Use Proxy |
        """
        sql_enable_thr_proxy = "Update tb_smart_protection_server set enable_proxy=1;"
        try:
            self.exec_sql_command_on_DDEI(sql_enable_thr_proxy)
        except Exception as err:
            print "Fail to enable connect Smart Protection Server through proxy for: %s" % err
            raise

    def disable_sps_use_proxy(self):
        """ Disable connect Smart Protection Server through proxy

        Param:

            None

        Return:

            None

        Example:

            | Disable SPS Use Proxy |
        """
        sql_disable_thr_proxy = "Update tb_smart_protection_server set enable_proxy=0;"
        try:
            self.exec_sql_command_on_DDEI(sql_disable_thr_proxy)
        except Exception as err:
            print "Fail to disable connect Smart Protection Server through proxy for: %s" % err
            raise

    def reload_sps_settings(self):
        """ Restart corresponding service to reload Smart Protection Server settings, include:
            1. Wrsagent
            2. saagent
            3. TaskProcessor
            4. U-sandbox

        Param:

            None

        Return:

            None

        Example:

            | Reload SPS Settings |
        """
        # Restart services
        # 1. wrsagent
        cmd = conf.CMD_RESTART_WRSAGENT
        try:
            self.exec_command_on_DDEI(cmd)
        except Exception as err:
            print("Stop WRSAGENT fail for : %s" % err)
            raise

        # 2. saagent
        cmd = conf.CMD_RESTART_SAAGENT
        try:
            self.exec_command_on_DDEI(cmd)
        except Exception as err:
            print("Stop SAAGENT fail for : %s" % err)
            raise

        # 3. TaskProcessor
        cmd_stop = conf.CMD_RESTART_TASKPROCESSOR
        cmd_start = "python /opt/trend/ddei/bin/sandbox/TaskProcessor.pyc >/dev/null 2>&1 &"

        try:
            self.exec_command_on_DDEI(cmd_stop)
            time.sleep(1)
        except Exception as err:
            print("Stop TaskProcessor fail for : %s" % err)
            raise

        # inline function to sync sps settings to u-sandbox
        def notify_usbx():
            # Notify u-sandbox
            # SQL preparation
            # Status about if local SPS was enabled or not.
            sql_sps_enable = "select value from tb_global_setting where section='smart_scan' and name='use_local';"
            # Enable connect through proxy or not
            sql_sps_use_proxy = "select enable_proxy from tb_smart_protection_server;"
            # Status about if local SPS supports reverse proxy or not
            sql_sps_support_rp = "select support_rp from tb_smart_protection_server;"
            # Enable use reverse proxy or not
            sql_sps_use_rp = "select value from tb_global_setting where section='smart_scan' and name='use_sps_as_proxy';"
            # Use certificate or not
            sql_sps_use_ca = "select use_certificate from tb_smart_protection_server;"
            # Use CRL or not
            sql_sps_use_crl = "select use_crl from tb_smart_protection_server;"
            # SPS server FQDN/IP
            sql_sps_server = "select host from tb_smart_protection_server;"
            # SPS server port
            sql_sps_port = "select port_wr from tb_smart_protection_server;"

            # Get value for each settings
            try:
                sps_enable = int(self.exec_sql_command_on_DDEI(sql_sps_enable))
                sps_use_proxy = int(self.exec_sql_command_on_DDEI(sql_sps_use_proxy))
                sps_support_rp = int(self.exec_sql_command_on_DDEI(sql_sps_support_rp))
                sps_use_rp = int(self.exec_sql_command_on_DDEI(sql_sps_use_rp))
                sps_use_ca = int(self.exec_sql_command_on_DDEI(sql_sps_use_ca))
                sps_use_crl = int(self.exec_sql_command_on_DDEI(sql_sps_use_crl))
                sps_server_port = ''.join([self.exec_sql_command_on_DDEI(sql_sps_server), ":", self.exec_sql_command_on_DDEI(sql_sps_port)])
            except Exception as err:
                print "Get TMSPS settings from DB fail for %s." % err
                raise

            # Sync settings to u-sandbox
            options = ""

            if sps_use_proxy == 0:    # not connect use proxy
                options = " --skipproxy " + options

            if sps_enable == 0:    # SPS disabled, use global mode
                options = " --mode global"
            elif sps_support_rp == 0 or (sps_support_rp == 1 and sps_use_rp == 0):    # Not support rp or (support rp but disabled)
                options = " --mode local --lwrsserver " + sps_server_port + " --clientip 127.0.0.1 " + options
            else:    # support reverse proxy and enable
                options = options + " --verifyserver OFF"
                options = " --mode localex --lwrsserver " + sps_server_port + " --clientip 127.0.0.1 " + options
                if sps_use_ca == 1:    # enable use certificate
                    options = options + " --castore " + conf.RP_CERT_PATH
                    if sps_use_crl == 1:    # enable use crl
                        options = options + " --crl " + conf.RP_CRL_PATH

            # Set sps configurations to u-sandbox
            cmd = conf.CMD_USBX_SET_EXTSERVICES + options
            try:
                self.exec_command_on_DDEI(cmd)
            except Exception as err:
                print "Fail to sync sps settings into u-sandbox for %s." % err
                raise

        notify_usbx()

    def parse_url_rating_result(self, wrs_ret):
        """ Parse the URL rating result, include:
            1. WRS (Web Reputation)
            2. WIS (Web Inspection)

        Param:

            wrs_ret: URL rating result

        Return:

            ret_dict: dictionary object which stores URL rating result which includes keys:
                      1. original_url
                      2. wrs_score
                      3. wrs_category
                      4. wis_severity
                      5. wis_threat_name

        Example:

            | Parse URL Rating Result | 2016/04/11 03:49:02 GMT+00:00   [19799:4050889536] [DIAGNOSTIC]LOG_LEVEL_DEBUG: [RequestHandler.h][37][~RequestHandler] Write WRS response... WRS-RET:ALL:1:L28:http://wrs21.winshipway.com/:21:0:74:9:TSPY_KEYLOG.GC|\r\n |
        """
        try:
            # dictionary for return
            ret_dict = {}

            # Split wrs_ret by string "Write WRS response..."
            wrs_ret_tmp = wrs_ret.split("Write WRS response...")[1].strip()

            # Split tmp ret by character ":" and save the specific split result into dictionary
            ori_url = ''.join([wrs_ret_tmp.split(":")[4].strip(), ":", wrs_ret_tmp.split(":")[5].strip()])
            wrs_score = wrs_ret_tmp.split(":")[6].strip()
            wrs_category = wrs_ret_tmp.split(":")[8].strip()
            wis_severity = wrs_ret_tmp.split(":")[9].strip()
            wis_threat_name = wrs_ret_tmp.split(":")[10].split("\\")[0].strip()

            # Initialize return dictionary
            ret_dict["original_url"] = ori_url
            ret_dict["wrs_score"] = wrs_score
            ret_dict["wrs_category"] = wrs_category
            ret_dict["wis_severity"] = wis_severity
            ret_dict["wis_threat_name"] = wis_threat_name
        except Exception as err:
            print "Parse URL rating result fail for %s." % err
            raise

        return ret_dict

    def switch_va_type(self, source=0, ip_address="192.168.0.1", apikey="0578D46D-F6F1-48B3-A4CE-68CBBB920213", proxy=0, quota=50):
        """  Switch the virtual analysis module between internal and external

        Params:

            type: 0 or 1.  0: internal; 1: external

        Return:

            None

        Example:
            | Switch Va Type | 0 |
        """
        options = "--action=restart --ui_source=%s --ui_address=%s --ui_apikey=%s --ui_proxy_enable=%s --ui_quota=%s"

        cmd = ' '.join([conf.USBX_VA_UTILS, options % (source, ip_address, apikey, proxy, quota)])
        print cmd

        try:
            self.exec_command_on_DDEI(cmd)
        except Exception as err:
            print "Switch virtual analyzer fail for %s." % err
            raise

if __name__ == '__main__':
    pass