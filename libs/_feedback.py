from _baselib import KeywordBase

import sys
import os
import SSHLibrary
import commands
from subprocess import check_output
import time
import conf


class FeedbackKeyWords(KeywordBase):
	"""
	This library contains all feedback related keywords.
	"""
	def get_value_from_DB(self,table,field,condition = None):
		""" Get value from DB

		@Param:

			table:    The table name

			field:   The field going to be read

			condition:   The query condition, can be null

		Return:

			If no error occur, queried value from DB will be returned

		Example:

		| Get Value From Db | tb_object_file | file_type |

		"""

		if condition:
			cmd = '%s -U %s -d %s -c "select %s from %s where %s"' % (conf.PSQL_BIN, conf.DB_USER, conf.DB_NAME, field, table, condition)
		else:
			cmd = '%s -U %s -d %s -c "select %s from %s"' % (conf.PSQL_BIN, conf.DB_USER, conf.DB_NAME, field, table)
		#result = commands.getoutput(cmd)
		result = self.ssh_conn.execute_command(cmd)
		get_value = ''.join(result.split('\n')[2:3]).strip()
		return get_value

	def get_value_from_xml(self,filename,module,param):
		""" Get value from file in xml format

		@Param:

			filename:    The source file name

			module:   The module section going to be read

			param:   The parameter going to be read

		Return:

			If no error occur, parameter value will be returned

		Example:

		| Get Value From Xml | tmfbed_guid.conf | tmfbed | guid |

		"""
		cmd = '%s %s val %s %s' % (conf.GLCFG, filename, module, param)
		#result = commands.getoutput(cmd)
		result = self.ssh_conn.execute_command(cmd)
		if result.strip() == '':
			raise AssertionError("%s in %s is blank" %(param,filename))
		print result.strip()
		return result.strip()

	def set_value_to_xml(self,filename,module,param,value):
		""" Set value to file in xml format

		@Param:

			filename:    The source file name

			module:   The module section going to be written

			param:   The parameter going to be written

			value:   The value going to be set

		Return:

			None

		Example:

		| Set Value To Xml | tmfbed.conf | tmfbed | fb_server | 10.10.10.10 |

		"""
		cmd = '%s %s set %s %s %s' % (conf.GLCFG, filename, module, param, value)
		#result = commands.getoutput(cmd)
		result = self.ssh_conn.execute_command(cmd)
		check_value = self.get_value_from_xml(filename, module, param)
		if check_value != value :
			raise AssertionError("value of %s can't be set" % value)

	def wait_till_usbx_finish(self):
		""" Wait usanbox until it finishes analyzing

		@Param:

			None

		Return:

			None

		Example:

		| Wait Till Usbx Finish |

		"""
                while True:
                        status = int(self.get_value_from_DB('tb_sandbox_task_details','status'))
                        if status in (2,3):
                                break
                        elif status in (0,1):
                                time.sleep(5)

	def enable_feedback(self):
		""" Enable feedback function from backend

		@Param:

			None

		Return:

			None

		Example:

		| Enable Feedback |

		"""
		self.set_value_to_xml(conf.TMFBED_CONFIG, 'tmfbed', 'enable', '1')

		cmd = '%s --switch ON --sample 0' % conf.USBX_FEEDBACK
		self.ssh_conn.execute_command(cmd)

		cmd = '%s restart' % conf.S99TMFBED
		self.ssh_conn.execute_command(cmd)

		cmd = 'ls %s' % conf.TMFBED_FOLDER
                result = self.ssh_conn.execute_command(cmd)

                if result != '':
                        cmd = 'rm -rf %s' % conf.TMFBED_FOLDER
                        self.ssh_conn.execute_command(cmd)

                cmd = 'rm -f %s*' % conf.BLOB_FOLDER
                self.ssh_conn.execute_command(cmd)

                cmd = 'mkdir %s' % conf.TMFBED_FOLDER
                self.ssh_conn.execute_command(cmd)

		self.upload_file_to_DDEI(os.path.join(conf.AUTO_ROOT,r'libs\feedback\*'),'/root/tmfbed/')

                cmd  = 'chmod a+x %s/tmfbeunpack' % conf.TMFBED_FOLDER
                self.ssh_conn.execute_command(cmd)

		time.sleep(3)

	def disable_feedback(self):
		""" Disable feedback function from backend

		@Param:

			None

		Return:

			None

		Example:

		| Disable feedback |

		"""
		self.set_value_to_xml(conf.TMFBED_CONFIG, 'tmfbed', 'enable', '0')

                cmd = '%s --switch OFF' % conf.USBX_FEEDBACK
		self.ssh_conn.execute_command(cmd)

		cmd = '%s restart' % conf.S99TMFBED
		self.ssh_conn.execute_command(cmd)

		cmd = 'rm -rf %s' % conf.TMFBED_FOLDER
		self.ssh_conn.execute_command(cmd)
		
		time.sleep(3)

	def check_file_existence(self, path):
		""" Check if file exists under the giving path

		@Param:

			path: the folder path to check file

		Return:

			is_exist: 1(exist) / 0(not exist)

		Example:

		| Check File Existence | /var/tmfbed_tmp |

		"""
		cmd = "ls -l %s|awk '{print $2}'" % path
		result = self.ssh_conn.execute_command(cmd)
		if result.strip() == '0':
			return 0
		else:
			return 1

	def verify_blob_atse(self):
		""" Verify blob file containing atse detection

		@Param:

			None

		Return:

			None

		Example:

		| Verify Blob Atse |

		"""
		value_from_db_engine = []
		value_from_db_detection = ['VSAPI_001']

		#query engine info from tb_active_update
		value_from_db_engine.append(self.get_value_from_DB('tb_active_update', 'file_name', 'type = 1'))
		value_from_db_engine.append(self.get_value_from_DB('tb_active_update', 'version', 'type = 1').replace('.',''))
		enginever = self.get_value_from_DB('tb_active_update', 'version', 'type = 9')
                if enginever == '':
                        raise AssertionError('No atse engine version in DB!')
                        
		value_from_db_engine.append(enginever.split('.')[0])
		value_from_db_engine.append(enginever.split('.')[1])
		value_from_db_engine.append(enginever.split('.')[2])
		value_from_db_engine.append('2')

		#query detection info from tb_object_file
		value_from_db_detection.append(self.get_value_from_DB('tb_object_file', 'threat_name'))
		file_type = self.get_value_from_DB('tb_object_file', 'file_type')
		value_from_db_detection.append(file_type.split(':')[0])
		value_from_db_detection.append(file_type.split(':')[1])
		value_from_db_detection.append(self.get_value_from_DB('tb_object_file', 'file_size'))
		value_from_db_detection.append(self.get_value_from_DB('tb_object_file', 'sha1'))


		#query info from atse blob file
		cmd  = 'ls %sb.*' % conf.BLOB_FOLDER
                blob_name = self.ssh_conn.execute_command(cmd)
                if blob_name == '':
                        raise AssertionError('no blob file exist.')

		cmd  = 'python %s/parse_blob.py -s=V -f=%s' % (conf.TMFBED_FOLDER, blob_name)
		stdout,stderr = self.ssh_conn.execute_command(cmd,return_stderr = 'yes')
		result = stdout.split('\n')
		if stderr != '':
                        raise AssertionError('Parse blob file error: %s' % stderr)

		value_from_blob_engine = []
		value_from_blob_detection = []

		value_from_blob_engine.append(''.join(result[11]).split('"')[1])
		value_from_blob_engine.append(''.join(result[12]).split(':')[1].strip())
		value_from_blob_engine.append(''.join(result[15]).split(':')[1].strip())
		value_from_blob_engine.append(''.join(result[16]).split(':')[1].strip())
		value_from_blob_engine.append(''.join(result[17]).split(':')[1].strip())
		value_from_blob_engine.append(''.join(result[23]).split(':')[1].strip())
		
		value_from_blob_detection.append(''.join(result[0]).split('=')[1])
		value_from_blob_detection.append(''.join(result[10]).split('"')[1])
		value_from_blob_detection.append(''.join(result[19]).split(':')[1].strip())
		value_from_blob_detection.append(''.join(result[20]).split(':')[1].strip())
		value_from_blob_detection.append(''.join(result[21]).split(':')[1].strip())
		value_from_blob_detection.append(''.join(result[22]).split('"')[1])
		
		if value_from_blob_engine != value_from_db_engine:
			print 'engine value from blob = ' + ' '.join(value_from_blob_engine)
			print 'engine value from DB   = ' + ' '.join(value_from_db_engine)
			raise AssertionError('ATSE engine info is different from DB to blob')

		if value_from_blob_detection != value_from_db_detection:
			print 'detection value from blob = ' + ' '.join(value_from_blob_detection)
			print 'detection value from DB   = ' + ' '.join(value_from_db_detection)
			raise AssertionError('ATSE detection info is different from DB to blob')

        def make_fake_wrs_detect(self):
		""" Make fake wrs_detect data in tb_sandbox_urlfilter_cache table.

		@Param:

			None

		Return:

			None

		Example:

                | Make Fake Wrs Detect |

		"""
                cmd_1 = "insert into tb_sandbox_urlfilter_cache (url,create_time,scan_time,finish_time,"
                cmd_2 = "wrs_detected) values ('http://www.yobdance.com/i3r.snf33','2014-06-16 01:28:10.511381',"
                cmd_3 = "'2014-06-16 01:27:43.658074','2014-06-16 01:27:48.053468',1);"
                cmd = '%s -U %s -d %s -c "%s%s%s"' % (conf.PSQL_BIN, conf.DB_USER, conf.DB_NAME, cmd_1,cmd_2,cmd_3)
		result,err = self.ssh_conn.execute_command(cmd,return_stderr=True)
		print 'insert result:'+result

	def verify_blob_SAL(self):
		""" Verify blob file containing sal detection

		@Param:

			None

		Return:

			None

		Example:

		| Verify Blob SAL |

		"""
		value_from_db_detection = ['SAL_001']
		value_from_blob_detection = []
		
		#query info from sal blob file
		cmd  = 'ls %sb.*' % conf.BLOB_FOLDER
                blob_name = self.ssh_conn.execute_command(cmd)
                if blob_name == '':
                        raise AssertionError('no blob file exist.')

		cmd  = 'python %s/parse_blob.py -s=S -f=%s' % (conf.TMFBED_FOLDER, blob_name)
		stdout,stderr = self.ssh_conn.execute_command(cmd,return_stderr = 'yes')
		result = stdout.split('\n')
		if stderr != '':
                        print 'Parse blob file error: %s' % stderr

		value_from_blob_detection.append(''.join(result[0]).split('=')[1])
		
		if value_from_blob_detection != value_from_db_detection:
			print 'detection value from blob = ' + ' '.join(value_from_blob_detection)
			print 'detection value from DB   = ' + ' '.join(value_from_db_detection)
			raise AssertionError('ATSE detection info is different from DB to blob')

	def verify_blob_usbx(self):
		""" Verify blob file containing usandbox detection

		@Param:

			None

		Return:

			None

		Example:

		| Verify Blob Usbx |

		"""
		value_from_db_detection = ['Usandbox_001']
		value_from_blob_detection = []
		
		cmd  = 'ls %sb.*' % conf.BLOB_FOLDER
                blob_name = self.ssh_conn.execute_command(cmd)
                if blob_name == '':
                        raise AssertionError('no blob file exist.')

		cmd  = 'python %s/parse_blob.py -s=U -f=%s' % (conf.TMFBED_FOLDER, blob_name)
		stdout,stderr = self.ssh_conn.execute_command(cmd,return_stderr = 'yes')
		result = stdout.split('\n')
		if stderr != '':
                        raise AssertionError('Parse blob file error: %s' % stderr)

		value_from_blob_detection.append(''.join(result[0]).split('=')[1])
		
		if value_from_blob_detection != value_from_db_detection:
			print 'detection value from blob = ' + ' '.join(value_from_blob_detection)
			print 'detection value from DB   = ' + ' '.join(value_from_db_detection)
			raise AssertionError('ATSE detection info is different from DB to blob')

	def verify_blob_product_info(self):
		""" Verify the product default info in blob header

		@Param:

			None

		Return:

			None

		Example:

		| Verify Blob Product Info |

		"""
		value_default = [conf.PRODUCT_ID, conf.PRODUCT_VERSION, conf.PRODUCT_LANG, conf.PRODUCT_PLATFORM]
		value_from_blob = []
		
		cmd  = 'ls /var/tmfbed_tmp/b.*'
                blob_name = self.ssh_conn.execute_command(cmd)
                if blob_name == '':
                        raise AssertionError('no blob file exist.')

		cmd  = 'python /root/tmfbed/parse_blob.py -s=V -f=%s' % blob_name
		stdout,stderr = self.ssh_conn.execute_command(cmd,return_stderr = 'yes')
		result = stdout.split('\n')
		if stderr != '':
                        raise AssertionError('Parse blob file error: %s' % stderr)

		value_from_blob.append(''.join(result[1]).split('=')[1])
		value_from_blob.append(''.join(result[2]).split('=')[1])
		value_from_blob.append(''.join(result[3]).split('=')[1])
		value_from_blob.append(''.join(result[4]).split('=')[1])
		
		if value_default != value_from_blob:
			print 'product default value   = ' + ' '.join(value_default)
			print 'product value from blob = ' + ' '.join(value_from_blob)
			raise AssertionError('Product info is different from blob to default')	
		


