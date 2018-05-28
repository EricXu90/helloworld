__author__ = 'wentao_song'

from _baselib import KeywordBase
import conf
import time

backup_version=1
rollback_version=1
class UpgradeKeywords(KeywordBase):
    """
    This library contain all related keywords about update function: Hotfix/firmware
    """
    
    def is_file_uploaded(self, filename):
        """ Check if the file has been uploaded

        """
        get_file_num_cmd = "find %s -name %s | wc -l" % (conf.DIR_FILE_UPLOAD,filename)
        filenum_after_uploaded = self.exec_command_on_DDEI(get_file_num_cmd)
       
        if int(filenum_after_uploaded) == 1:
            return True
        else:
            raise AssertionError('Upload hotfix file fail.')



    def update_or_rollback_hotfix(self, file, filename,action='apply'):
        """ Update or rollback hotfix

        @Param:

            file:  hotfix file

            action:     update or rollback action

        Return:

            None

        Example:

        | Update Or Rollback hotfix | filepath |  filename | apply |

        """
        self.upload_file_to_DDEI(file,conf.DIR_FILE_UPLOAD)

        self.is_file_uploaded(filename)

        if action == 'apply':
            cmd = "%s apply" %(conf.CMD_HOTFIX_UPGRADE + conf.DIR_FILE_UPLOAD + filename)
        else:
            cmd = conf.CMD_HOTFIX_ROLLBACK

        self.exec_command_on_DDEI(cmd)

        #if not self._is_update_finish_apply():
        #    raise AssertionError("Fail to apply components: %s" % components)


    def upgrade_or_rollback_should_be_successful(self,appliednum):
        """ Check the upgrade or rollback should be successful

        @Param:

            appliednum:  the version num should be updated,default is 1

        Return:

            None

        Example:

        | upgrade or rollback should be successful| 2019 |

        """
        file_content = self.exec_command_on_DDEI("grep AppBuildNum %s" %(conf.PATCH_FILE))
        if file_content.strip() == '' and appliednum == "1":
            return True
        elif file_content.strip() == '' and appliednum != "1":
            raise AssertionError("upgrade or rollback failed")     
        dic = dict([(i.strip().split('=')[0],i.strip().split('=')[1]) for i in file_content.split('\n')])
        if dic['AppBuildNum'] == appliednum:
            return True
        else:
            raise AssertionError(dic['AppBuildNum'])

    def upgrade_file_should_be_delete(self,appliednum):
        """ Check the upgrade temp file should be deleted

        @Param:

            appliednum:  the version num should be updated,default is 1

        Return:

            None

        Example:

        | upgrade file should be delete | 2019 |

        """
        data_dir_cmd = self.exec_command_on_DDEI("grep DataDirectory %s" %(conf.PACKAGE_CONFIG))
        if data_dir_cmd.strip() == '':
           raise AssertionError("file /var/tmp/config.ini not exist")
        else:
           dic = dict([(i.strip().split('=')[0],i.strip().split('=')[1]) for i in data_dir_cmd.split('\n')])
           data_dir=dic['DataDirectory']
           
        pbagent_num = self.exec_command_on_DDEI("ls /tmp/pbagent | wc -l")
        
        if pbagent_num.strip() == "1":
            raise AssertionError("delete tmp file failed:/var/pbagent")
        else:
            print "OK"
            
        patch_id_tmp_dir = data_dir + "/openva-update-tools/patch_backup/" + appliednum + "_tmp"
        patch_id_tmp = self.exec_command_on_DDEI("ls %s | wc -l" %(patch_id_tmp_dir))
        
        if patch_id_tmp.strip() == "1":
            raise AssertionError("delete tmp file failed:patch_id_tmp")
        else:
            print "OK"
            
        patch_backup_app_file_path = data_dir + "/openva-update-tools/patch_backup/files/app_backup.tar.gz"
        patch_backup_os_file_path = data_dir + "/openva-update-tools/patch_backup/files/os_backup.tar.gz"
        patch_backup_app_file=self.exec_command_on_DDEI("ls %s | wc -l" %(patch_backup_app_file_path))
        patch_backup_os_file = self.exec_command_on_DDEI("ls %s | wc -l" %(patch_backup_os_file_path))
        
        if patch_backup_app_file.strip() == "1" or patch_backup_os_file.strip() == "1":
            raise AssertionError("delete tmp file failed:patch_backup_file")
        else:
            return True
        
           
                
                           

        
