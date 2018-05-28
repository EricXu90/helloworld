 # -*- coding: utf-8 -*-
from __future__ import division
import os
import sys
from libs import conf
from libs.logger import logerror,loginfo,logwarning,init
import xml.etree.ElementTree as etree
import json
import SSHLibrary
import re
from subprocess import Popen, PIPE
from ftplib import FTP,error_perm
import shutil
import time
from datetime import datetime

#first run global variables
#=============================
_pass = 0
_fail = 0
total_case = 0
total_fail_case = 0
fail_case_list = []
suite_summary=[]
fail_suit_summary=[]
all_start_time=''
all_end_time=''
suite_case_summary=[]
suite_name=''
#=============================

#re run global variables
#=============================
_re_pass = 0
_re_fail = 0
re_total_case = 0
re_total_fail_case = 0
re_fail_case_list = []
re_suite_summary=[]
re_fail_suit_summary=[]
re_all_start_time=''
re_all_end_time=''
re_suite_case_summary=[]
re_suite_name=''
#=============================

init()

class SshCon(object):
	"""docstring for Ssh"""
	def __init__(self):

		self.ssh_conn = SSHLibrary.SSHLibrary()
		self.ssh_conn.open_connection(conf.DDEI_IP, '#')
		self.ssh_conn.login(conf.SSH_USR, conf.SSH_PWD)


	def exec_command(self, cmd):
		""" Execute remote command and return the result

		"""
		try:
			result = self.ssh_conn.execute_command(cmd).strip()
		except:
			self.ssh_conn.open_connection(conf.DDEI_IP, '#')
			self.ssh_conn.login(conf.SSH_USR, conf.SSH_PWD)
			result = self.ssh_conn.execute_command(cmd).strip()
			return result
		return result

	def close_con(self):
		self.ssh_conn.close_connection()
		

class RobotXML2SCTMResult(SshCon):
	def __init__(self):
		super(RobotXML2SCTMResult,self).__init__()
		self.result={}
		self.re_result={}
		self.total=0
		self.fail=0
		self.starttime=''
		self.endtime=''
		self.ftp_report=True
		self.recieve_remote_files=[]
		self.fail_send_result_machine=[]
		self.ftp_log=True
		self.rerun_state=True
		self.log=''
		self.ip=re.search('\d+\.\d+\.\d+\.\d+',Popen('ipconfig', stdout=PIPE).stdout.read()).group(0)
		self.build=super(RobotXML2SCTMResult,self).exec_command('env|grep PRODUCT_BUILD').split('=')[1]
		self.version=super(RobotXML2SCTMResult,self).exec_command('env|grep PRODUCT_VER').split('=')[1]
		super(RobotXML2SCTMResult,self).close_con()

	def write_send_results(self,root):
		global suite_summary,fail_suit_summary
		global total_case, total_fail_case
		global _fail
		global suite_name
		global fail_case_list
		global all_end_time,all_start_time

		self.parseTest_summary(root)
		file=os.path.join(conf.RESULTS_DIR_TEMP,'%s_%s.json')%(self.build,(self.ip).split('.')[-1])
		if os.path.exists(file):
			os.remove(file)
		else:
			if not os.path.exists(conf.RESULTS_DIR_TEMP):
				os.makedirs(conf.RESULTS_DIR_TEMP)

		for suite in suite_summary:
			temp={}
			for case in suite['cases']:
				temp[case.keys()[0]]=case.values()[0]
			index=suite_summary.index(suite)
			suite_summary[index]['cases']=temp

		self.result['suite_dict']=suite_summary
		self.result['fail_dict']=fail_suit_summary
		self.result['summary_dict']={'total_case':total_case,'fail_case':total_fail_case,'start_time':all_start_time,'end_time':all_end_time}
		fp=open(file,'w')
		fp.write(json.dumps(self.result))
		fp.close()
		loginfo('start parse rerun.xml')
		self.rerun_parse_result(os.path.join(conf.RERUN_LOG_DIR,'rerun.xml'))
		loginfo('finish parse rerun.xml')
		refile=os.path.join(conf.RESULTS_DIR_TEMP,'re_%s_%s.json')%(self.build,(self.ip).split('.')[-1])
		if self.rerun_state:		
			if not os.path.exists(refile):
				logerror('parse rerun.xml fail')
				pass
			else:
				self.merge_rerun_result(file,refile)

		if not self.ip==conf.FTP_SERVER:
			ftp=self.ftpconnect(conf.FTP_SERVER)
			bufsize=1024
			src=ftp.pwd()
			result_src=os.path.join(src,'\Report result')
			re_result_src=os.path.join(src,'rerun_result')
			#send merge result
			try:
				ftp.cwd(result_src)
			except error_perm:
				try:
					ftp.mkd(result_src)
					ftp.cwd(result_src)
				except error_perm:
					print 'u have no authority to make dir'	
			fp=open(file,'rb')
			ftp.storbinary('STOR %s'%os.path.basename(file),fp,bufsize)
			ftp.set_debuglevel(0)
			fp.close()
			if not os.path.exists(refile):
				logerror('not extist rerun result json,do not need to send it')
				pass
			else:
				try:
					ftp.cwd(re_result_src)
				except error_perm:
					try:
						ftp.mkd(re_result_src)
						ftp.cwd(re_result_src)
					except error_perm:
						print 'u have no authority to make dir'	
				fp=open(refile,'rb')
				ftp.storbinary('STOR %s'%os.path.basename(refile),fp,bufsize)
				ftp.set_debuglevel(0)
				fp.close()					
			ftp.quit()

	def merge_rerun_result(self,orginfile,rerunfile):
		#read first run result
		fp=open(orginfile,'r')
		result_dict=json.load(fp)
		fp.close()
		#read run failed case result
		fp=open(rerunfile,'r')
		re_result_dict=json.load(fp)
		fp.close()
		#merge rerun result into first run result
		for key,value in re_result_dict.items():
			if key=="fail_dict":
				result_dict[key]=value
			elif key=="summary_dict":
				result_dict[key]["fail_case"]=value["fail_case"]
			else:
				for re_suite in value:
					for suite in result_dict[key]:
						index=result_dict[key].index(suite)
						if re_suite["SuiteName"] == suite["SuiteName"]:
							result_dict[key][index]["Pass"]=re_suite["Pass"]+result_dict[key][index]["Pass"]
							result_dict[key][index]["Fail"]=re_suite["Fail"]
							for case_key,case_value in re_suite["cases"].items():
								if case_value==1:
									result_dict[key][index]["cases"][case_key]=case_value
		#rewrite first run result
		fp=open(orginfile,'w')
		fp.write(json.dumps(result_dict))
		fp.close()	

	def write_rerun_results(self,root):
		global re_suite_summary,re_fail_suit_summary
		global re_total_case, re_total_fail_case
		global _re_fail
		global re_suite_name
		global re_fail_case_list
		global re_all_end_time,re_all_start_time

		self.parseTest_rerun_summary(root)
		file=os.path.join(conf.RESULTS_DIR_TEMP,'re_%s_%s.json')%(self.build,(self.ip).split('.')[-1])
		if os.path.exists(file):
			os.remove(file)
		else:
			if not os.path.exists(conf.RESULTS_DIR_TEMP):
				os.makedirs(conf.RESULTS_DIR_TEMP)

		for suite in re_suite_summary:
			temp={}
			for case in suite['cases']:
				temp[case.keys()[0]]=case.values()[0]
			index=re_suite_summary.index(suite)
			re_suite_summary[index]['cases']=temp

		self.re_result['suite_dict']=re_suite_summary
		self.re_result['fail_dict']=re_fail_suit_summary
		self.re_result['summary_dict']={'total_case':re_total_case,'fail_case':re_total_fail_case,'start_time':re_all_start_time,'end_time':re_all_end_time}
		fp=open(file,'w')
		fp.write(json.dumps(self.re_result))
		fp.close()

	def send_detail_result_to_ftp(self):
		localdir=conf.REPORT_LOG_DIR
		ftp=self.ftpconnect(conf.FTP_28,conf.USER,conf.PWD)
		root_dir=ftp.pwd()
		remotedir=os.path.join(root_dir,'\Home\dcc\Anne\Automation\%s')%self.build
		try:
			ftp.cwd(remotedir)
		except Exception as e:
			try:
				ftp.mkd(remotedir)
				ftp.cwd(remotedir)
			except Exception as e:
				raise e
		self.log=r'\\10.204.16.28'+remotedir		
		remotedir=os.path.join(remotedir,'report_%s'%(self.ip.split(".")[-1]))
		try:
			self.uploaddir_to_ftp(ftp, localdir, remotedir)
		except Exception as e:
			logerror(e)	
		ftp.quit()

	def uploaddir_to_ftp(self,ftp,localdir,remotedir):
		if not os.path.isdir(localdir):
			return
		try:
			ftp.cwd(remotedir)
		except Exception as e:
			try:
				ftp.mkd(remotedir)
				ftp.cwd(remotedir)
			except Exception as e:
				logerror(e)
		for file in os.listdir(localdir):
			src=os.path.join(localdir,file)
			if os.path.isfile(src):
				self.uploadfile(ftp, src)
				loginfo(src)
			elif os.path.isdir(src):
				try:
					ftp.mkd(file)
					remotedir=os.path.join(remotedir,file)
				except Exception as e:
					logerror(e)
				self.uploaddir_to_ftp(ftp, src, remotedir)
		ftp.cwd('..')

	def uploadfile(self,ftp,localpath):
		if not os.path.isfile(localpath):
			return
		bufsize=1024
		fp=open(localpath,'rb')
		ftp.storbinary('STOR %s'%os.path.basename(localpath), fp,bufsize)
		fp.close()

	def ftpconnect(self,server,username='',password=''):
		ftp=FTP()  
		ftp.set_debuglevel(0) #打开调试级别2，显示详细信息 
		ftp.connect(server,21) #连接  
		ftp.login(username,password) #登录，如果匿名登录则用空串代替即可
		return ftp        

	def parseTest_summary(self, root):
		global total_case, total_fail_case
		global _pass
		global _fail
		global suite_name,suite_case_summary
		global fail_case_list, fail_suit_summary,suite_summary
		global all_end_time


		for child in root:
			if (child.tag == "suite"):
				suite_name = child.attrib["name"]
				self.parseTest_summary(child) # search deeper
			if (child.tag == "test"):
				total_case += 1
				test = child
				id =test.attrib["name"]
				#suite_case_summary.append(id)
				result = test.find("status").attrib["status"]
				if (result.lower() == "pass"):
					temp={}
					result = "Pass"
					_pass += 1
					temp[id]=1
					suite_case_summary.append(temp)
				else:
					temp={}
					result = "Fail"
					_fail += 1
					total_fail_case += 1
					fail_case_list.append(id)
					temp[id]=0
					suite_case_summary.append(temp)
			if (child.tag == "status" and suite_name != ""):

				all_end_time = child.attrib["endtime"].split(".")[0]
				if _fail !=0:
					fail_suit_summary.append({"Fail suite":suite_name,"Cases":fail_case_list})
				suite_summary.append({'cases':suite_case_summary,'SuiteName':suite_name,'Total':_pass+_fail,'Pass':_pass,'Fail':_fail,'StartTime':child.attrib["starttime"].split(".")[0],'EndTime':child.attrib["endtime"].split(".")[0]})
				_pass=0
				_fail=0
				fail_case_list = []
				suite_name = ""
				suite_case_summary=[]

	def parseTest_rerun_summary(self, root):
		global re_total_case, re_total_fail_case
		global _re_pass
		global _re_fail
		global re_suite_name,re_suite_case_summary
		global re_fail_case_list, re_fail_suit_summary,re_suite_summary
		global re_all_end_time


		for child in root:
			if (child.tag == "suite"):
				re_suite_name = child.attrib["name"]
				self.parseTest_rerun_summary(child) # search deeper
			if (child.tag == "test"):
				re_total_case += 1
				test = child
				id =test.attrib["name"]
				#re_suite_case_summary.append(id)
				result = test.find("status").attrib["status"]
				if (result.lower() == "pass"):
					temp={}
					result = "Pass"
					_re_pass += 1
					temp[id]=1
					re_suite_case_summary.append(temp)
				else:
					temp={}
					result = "Fail"
					_re_fail += 1
					re_total_fail_case += 1
					re_fail_case_list.append(id)
					temp[id]=0
					re_suite_case_summary.append(temp)
			if (child.tag == "status" and re_suite_name != ""):

				re_all_end_time = child.attrib["endtime"].split(".")[0]
				if _re_fail !=0:
					re_fail_suit_summary.append({"Fail suite":re_suite_name,"Cases":re_fail_case_list})
				re_suite_summary.append({'cases':re_suite_case_summary,'SuiteName':re_suite_name,'Total':_re_pass+_re_fail,'Pass':_re_pass,'Fail':_re_fail,'StartTime':child.attrib["starttime"].split(".")[0],'EndTime':child.attrib["endtime"].split(".")[0]})
				_re_pass=0
				_re_fail=0
				re_fail_case_list = []
				re_suite_name = ""
				re_suite_case_summary=[]

	def merge_result(self):
		if self.ip==conf.FTP_SERVER:
			remote_result_number=len(conf.AUTOMATION_CLINET_IP_LIST)-1
			loginfo('remote result count:')
			loginfo(remote_result_number)
			latest_result_file=os.path.join(conf.LATEST_RESULTS_DIR,'%s.json')%self.build
			loginfo('latest_result_file:')
			loginfo(latest_result_file)
			remote_result_files=[]
			for address in conf.AUTOMATION_CLINET_IP_LIST:
				if address == conf.FTP_SERVER:
					local_file=os.path.join(conf.RESULTS_DIR_TEMP,'%s_%s.json')%(self.build,address.split('.')[-1])
				else:
					remote_file_temp=os.path.join(conf.FTP_SERVER_DIR,'%s_%s.json')%(self.build,address.split('.')[-1])
					remote_result_files.append(remote_file_temp)
			start=time.time()
			loginfo('need receive remote results file:')
			loginfo(remote_result_files)
			loginfo('******start merge result*******')
			while time.time()-start < conf.TIME_OUT:
				if len(self.recieve_remote_files)==remote_result_number:
					break
				loginfo('******now remote_result_files:*********')
				loginfo(remote_result_files)
				for file in remote_result_files:
					loginfo('file name:')
					loginfo(file)
					if os.path.exists(file):
						loginfo('exist this file:')
						loginfo(file)
						self.recieve_remote_files.append(file)
						loginfo('recieve_remote_files:')
						loginfo(self.recieve_remote_files)
						remote_result_files.remove(file)
						loginfo('now remote_result_files:')
						loginfo(remote_result_files)
						#read 68 result
						fp_local=open(local_file,'r')
						#read remote result
						fp_remote=open(file,'r')
						result_dict_local=json.load(fp_local)
						result_dict_remote=json.load(fp_remote)
						fp_local.close()
						fp_remote.close()
						if os.path.exists(conf.LATEST_RESULTS_DIR):
							shutil.rmtree(conf.LATEST_RESULTS_DIR,True)
						os.makedirs(conf.LATEST_RESULTS_DIR)
						loginfo('start merge result:')			
						merge_excu_case=result_dict_local['summary_dict']['total_case']+result_dict_remote['summary_dict']['total_case']
						merge_fail_case=result_dict_local['summary_dict']['fail_case']+result_dict_remote['summary_dict']['fail_case']
						if result_dict_local['summary_dict']['start_time']<result_dict_remote['summary_dict']['start_time']:
							starttime=result_dict_local['summary_dict']['start_time']
						else:
							starttime=result_dict_remote['summary_dict']['start_time']
						if result_dict_local['summary_dict']['end_time']<result_dict_remote['summary_dict']['end_time']:
							endtime=result_dict_remote['summary_dict']['end_time']
						else:
							endtime=result_dict_local['summary_dict']['end_time']
						merge_dict={}
						merge_dict['suite_dict']=result_dict_local['suite_dict']+result_dict_remote['suite_dict']
						merge_dict['fail_dict']=result_dict_local['fail_dict']+result_dict_remote['fail_dict']
						merge_dict['summary_dict']={'total_case':merge_excu_case,'fail_case':merge_fail_case,'start_time':starttime,'end_time':endtime}

						loginfo(json.dumps(merge_dict))
						#rewrite local result
						fp=open(local_file,'w')
						fp.write(json.dumps(merge_dict))
						fp.close()

						#write latest result
						fp=open(latest_result_file,'w')
						fp.write(json.dumps(merge_dict))
						fp.close()
						if not os.path.exists(conf.HISTORY_RESULT_DIR):
							os.makedirs(conf.HISTORY_RESULT_DIR)
						shutil.copy(latest_result_file,conf.HISTORY_RESULT_DIR)						
				loginfo('wait another report')
				time.sleep(300)
			loginfo('have recieved remote files')
			loginfo(self.recieve_remote_files)

			if remote_result_files:
				self.ftp_report=False
				for file in remote_result_files:
					self.fail_send_result_machine.append(conf.REMOTE_IP[file.split('_')[-1].split('.')[0]])
				logerror('some machine result did not send to ftp server')
				logerror(self.fail_send_result_machine)
			else:
				return
			if len(self.recieve_remote_files)==0:			
				fp=open(local_file,'r')
				result_dict_local=json.load(fp)
				fp.close()
				if os.path.exists(conf.LATEST_RESULTS_DIR):
					shutil.rmtree(conf.LATEST_RESULTS_DIR,True)
				os.makedirs(conf.LATEST_RESULTS_DIR)
				fp=open(latest_result_file,'w')
				fp.write(json.dumps(result_dict_local))
				fp.close()
				if not os.path.exists(conf.HISTORY_RESULT_DIR):
					os.makedirs(conf.HISTORY_RESULT_DIR)
				shutil.copy(latest_result_file,conf.HISTORY_RESULT_DIR)

	def output_html(self,dest):
		self.merge_result()
		self.send_detail_result_to_ftp()
		if self.ip==conf.FTP_SERVER:
			
			latest_result=os.path.join(conf.LATEST_RESULTS_DIR,'%s.json')%self.build
			result_json=open(latest_result,'r')
			result_dict=json.load(result_json)
			result_json.close()
			try:
				if os.path.exists(dest):
					os.remove(dest)
				else:
					if not os.path.exists(conf.REPORT_LOG_DIR):
						os.makedirs(conf.REPORT_LOG_DIR)
				fp = open(dest, "a");

				fp.write("<html>");
				fp.write("  <body>");
				self.output_environment_info(fp)
				self.output_log_path(fp)
				self.output_exec_summary(fp,result_dict)
				self.output_suite_summary(fp,result_dict)
				self.output_exec_details(fp,result_dict)
				loginfo('start output_add_cases')
				self.output_add_cases(fp,result_dict)
				loginfo('finish output_add_cases')
				loginfo('start output_diff_result')
				self.output_diff_result(fp,result_dict)
				loginfo('finish output_diff_result')
				fp.write("  </body>");
				fp.write("</html>");
				fp.close();
			except Exception, e:
				logerror("[Exception] output_html() get exception: %s", sys.exc_info()[:2])

	def output_environment_info(self,fp):  
		indent = "    "
		try:
			fp.write('%s<div><font size=4><u><b><1> Environment Info</b></u></font></div>' % (indent))
			fp.write('%s<div>IP: %s</div>' % (indent, self.ip))
			fp.write('%s<div>Build: %s.%s</div>' % (indent, self.version, self.build))
			fp.write('%s<div><hr></div>' % (indent))
		except Exception, e:
			logerror("[Exception] output_environment_info() get exception: %s", sys.exc_info()[:2])
			print "[Exception] output_environment_info() get exception: ", sys.exc_info()[:2]

	def output_log_path(self,fp):
		indent = "    "
		try:
			fp.write('%s<br/><br/><div><font size=4><u><b><2> Execution Log Address</b></u></font></div>' % (indent))
			fp.write('%s<div>PATH: %s</div>' % (indent, self.log))
			if self.ftp_log==False:
				fp.write('%s<div><font size=3 color="red">There are some log that did not send to ftp.</font></div>' % (indent))
			fp.write('%s<div><hr></div>' % (indent))
		except Exception as e:
			raise e

	def add_case_check(self,result):
		total_case_file=os.path.join(conf.HISTORY_RESULT_DIR,'cases_exec.json')
		# turn into dict,easy to look up
		add_case={}
		result_to_dict={}
		result_to_dict['totalcase']=result['summary_dict']['total_case']
		for item in result['suite_dict']:
			result_to_dict[item['SuiteName']]=item['cases']
		loginfo('result_to_dict:')
		loginfo(result_to_dict)
		if not os.path.exists(total_case_file):
			fp=open(total_case_file,'w')
			fp.write(json.dumps(result_to_dict))
			fp.close()
			return add_case
		#read latest result
		fp=open(total_case_file,'r')
		latest_cases_dict=json.load(fp)
		fp.close()

		#rewrite latest result,latest result just compare with last result
		#if you need to compare with history running case,please cancel follow 3 annotations
		fp=open(total_case_file,'w')
		fp.write(json.dumps(result_to_dict))
		fp.close()

		if result_to_dict['totalcase']==latest_cases_dict['totalcase']:
			return add_case
		else:
			#rewrite_dict=latest_cases_dict
			diff={}
			for key,value in result_to_dict.items():
				if key not in latest_cases_dict:
					add_case[key]=value
					# rewrite_dict[key]=value
				else:
					if type(value)!=type(1):
						for k,v in value.items():
							if k not in latest_cases_dict[key]:
								temp={}
								temp.setdefault(k,v)
								diff=dict(diff.items()+temp.items())
								add_case[key]=diff
								# rewrite_dict[key]=dict(rewrite_dict[key].items()+dict(k=v).items())  
				diff={}
		loginfo('add_case')
		loginfo(add_case)
		return add_case

	def diff_latest_run(self,result):
		fail_case_file=os.path.join(conf.HISTORY_FAIL_DIR,'%s.json'%self.build)
		fail_case={}
		temp_dict={}
		for item in result['fail_dict']:
			temp_dict[item['Fail suite']]=dict.fromkeys(item['Cases'],0)
		if not os.path.exists(conf.HISTORY_FAIL_DIR):
			os.makedirs(conf.HISTORY_FAIL_DIR)
			fp=open(fail_case_file,'w')
			fp.write(json.dumps(temp_dict))
			fp.close()
			return fail_case
		files=os.listdir(conf.HISTORY_FAIL_DIR)
		if not files:
			fp=open(fail_case_file,'w')
			fp.write(json.dumps(temp_dict))
			fp.close()
			return fail_case
		files.sort()
		fp=open(os.path.join(conf.HISTORY_FAIL_DIR,files[-1]),'r')
		fail_result=json.load(fp)
		fp.close()

		#write latest fail reuslt
		fp=open(fail_case_file,'w')
		fp.write(json.dumps(temp_dict))
		fp.close()
		diff={}
		for key,value in temp_dict.items():
			if key not in fail_result:
				fail_case[key]=value
			else:
				for k,v in value.items():
					if k not in fail_result[key]:
						temp={}
						temp.setdefault(k,v)
						diff=dict(diff.items()+temp.items())
						fail_case[key]=diff
			diff={}
		return fail_case

	def output_exec_summary(self,fp,result):
		indent = "    "
		self.total=result['summary_dict']['total_case']
		self.fail=result['summary_dict']['fail_case']
		self.starttime=result['summary_dict']['start_time']
		self.endtime=result['summary_dict']['end_time']
		_pass=self.total-self.fail
		try:
			if _pass==0:
				total_pass_rate = 0
			else:
				total_pass_rate = format(float(self.total-self.fail)/float(self.total)*100,'.2f')
			
			fp.write('%s<br/><br/><div><font size=4><b><u><3> Execution Summary</u></b></font></div>' % (indent))
			if self.ftp_report==False:
				fp.write('%s<div><hr></div>' % (indent))
				fp.write('%s<div><font size=4 color="red"><b>Case execution machine("%s") did not send another report more than 6 hours,please check it.</b></font></div>' % (indent,str(self.fail_send_result_machine)))
				fp.write('%s<div><hr></div>' % (indent))
			fp.write('%s<div><table border=1 width=100%%>' % (indent))
			fp.write('%s  <tr>' % (indent));
			fp.write('%s    <th vlign=center><div><b>Total Case</b></div></th>' % (indent));
			fp.write('%s    <th vlign=center><div><b>Pass Case</b></div></th>' % (indent));
			fp.write('%s    <th vlign=center><div><b>Fail Case</b></div></th>' % (indent));
			fp.write('%s    <th vlign=center><div><b>Pass Rate</b></div></th>' % (indent));
			fp.write('%s    <th vlign=center><div><b>Total execution time</b></div></th>' % (indent));
			fp.write('%s  </tr><tr>' % (indent));
			fp.write('%s    <td align=center><div>%s</div></td>' % (indent, self.total))
			if _pass==0:
				fp.write('%s    <td align=center><div>%s</div></td>' % (indent, _pass))
			else:
				fp.write('%s    <td align=center><div><font color=%s><b>%s</b></font></div></td>' % (
				indent, self.get_result_color("pass"), _pass))
			if total_fail_case == 0:
				fp.write('%s    <td align=center><div>%s</div></td>' % (indent, self.fail))
			else:
				fp.write('%s    <td align=center><div><font color=%s><b>%s</b></font></div></td>' % (
				indent, self.get_result_color("fail"), self.fail));  

			fp.write('%s    <td align=center bgcolor=%s><div>%s%%</div></td>' % (indent, self.get_rate_color(total_pass_rate),total_pass_rate))
			fp.write('%s    <td align=center><div>%s</div></td>' % (indent, self.time_span(self.starttime,self.endtime)))

			fp.write('%s  </tr>' % (indent))
			fp.write('%s</table></div>' % (indent))
			fp.write('%s<div><hr></div>' % (indent))       
		except Exception as e:
			logerror("[Exception] output_exec_summary() get exception: %s", sys.exc_info()[:2])
			print "[Exception] output_exec_summary() get exception: ", sys.exc_info()[:2]

	def output_suite_summary(self,fp,result):
		indent = "    "

		try:
			fp.write('<br/><br/>%s<div><font size=4><b><u><4> Suite Execute Summary</u></b></font></div>' % (indent))
			fp.write('%s<div><table border=1 width=100%%>' % (indent))
			fp.write('%s  <tr>' % (indent))
			fp.write('%s    <td vlign=center align=center><div><b>SuiteName</b></div></td>' % (indent));
			fp.write('%s    <td vlign=center align=center><div><b>Total</b></div></td>' % (indent));
			fp.write('%s    <td vlign=center align=center><div><b>Pass</b></div></td>' % (indent));
			fp.write('%s    <td vlign=center align=center><div><b>Fail</b></div></td>' % (indent));
			fp.write('%s    <td vlign=center align=center><div><b>Execution time</b></div></td>' % (indent))
			fp.write('%s  </tr>' % (indent))

			for suite in result['suite_dict']:
				fp.write('%s  <tr>' % (indent))
				fp.write('%s    <td align=left vlign=center><div>%s</div></td>' % (indent, suite['SuiteName']))
				fp.write('%s    <td align=center vlign=center><div>%s</div></td>' % (indent, suite['Total']))
				fp.write('%s    <td align=center vlign=center><div><font color=%s>%s</font></div></td>' % (
				indent, self.get_result_color('pass'), suite['Pass']))              
				if suite['Fail']>0:
					fail_color = self.get_result_color('fail')
				else:
					fail_color = self.get_result_color('pass')
				fp.write('%s    <td align=center vlign=center><div><font color=%s>%s</font></div></td>' % (
				indent, fail_color, suite['Fail']))
				fp.write('%s    <td align=center vlign=center><div>%s</div></td>' % (indent, self.time_span(suite['StartTime'],suite['EndTime'])))
				fp.write('%s  </tr>' % (indent))

			fp.write('</table>')
			fp.write('%s<div><hr></div>' % (indent))  
							  

		except Exception as e:
			logerror("[Exception] output_exec_details() get exception: %s", sys.exc_info()[:2])

	def output_exec_details(self,fp,result):
		indent = "    "
		j=0
		try:
			fp.write('<br/><br/>%s<div><font size=4><b><u><5> Execution Details</u></b></font></div>' % (indent))

			for suite in result['fail_dict']:
				fp.write('<br/>%s<div><font size=3><b><u>%s</u></b></font></div>' % (
					indent, suite['Fail suite']))
				fp.write('%s<div><table border=1 width=100%%>' % (indent))
				fp.write('%s  <tr>' % (indent))
				fp.write('%s    <td vlign=center align=center><div><b>Index</b></div></td>' % (indent))
				fp.write('%s    <td vlign=center align=center><div><b>Result</b></div></td>' % (indent))
				fp.write('%s    <td vlign=center align=center><div><b>Case Name</b></div></td>' % (indent))
				fp.write('%s  </tr>' % (indent))

				j=1
				for case in suite['Cases']:
					fp.write('%s  <tr>' % (indent))
					fp.write('%s    <td align=center vlign=center><div>%s</div></td>' % (indent, str(j)))
					fp.write('%s    <td align=center vlign=center><div><font color=%s>%s</font></div></td>' % (
							indent, self.get_result_color('fail'), 'Fail'))
					fp.write('%s    <td vlign=center><div>%s</div></td>' % (indent, case))
					fp.write('%s  </tr>' % (indent))
					j+=1

				fp.write('</table>')

		except Exception as e:
			logerror("[Exception] output_exec_details() get exception: %s", sys.exc_info()[:2]);

	def output_add_cases(self,fp,result):
		indent = "    "
		add_dict=self.add_case_check(result)
		_total=0
		_pass=0
		_fail=0
		try:
			fp.write('<br/><br/>%s<div><font size=4><b><u><6> New Added Test Cases Summary:</u></b></font></div>' % (indent))
			if add_dict:
				fp.write('%s<div><table border=1 width=100%%>' % (indent))
				fp.write('%s  <tr>' % (indent))
				fp.write('%s    <td vlign=center align=center><div><b>SuiteName</b></div></td>' % (indent))
				fp.write('%s    <td vlign=center align=center><div><b>Total</b></div></td>' % (indent))
				fp.write('%s    <td vlign=center align=center><div><b>Pass</b></div></td>' % (indent))
				fp.write('%s    <td vlign=center align=center><div><b>Fail</b></div></td>' % (indent))
				fp.write('%s  </tr>' % (indent))
				for suite in add_dict:
					for case in add_dict[suite]:
						_total +=1
						if add_dict[suite][case]==1:
							_pass +=1
						else:
							_fail +=1
					fp.write('%s  <tr>' % (indent))
					fp.write('%s    <td align=left vlign=center><div>%s</div></td>' % (indent, suite))   
					fp.write('%s    <td align=center vlign=center><div>%s</div></td>' % (indent, _total))
					fp.write('%s    <td align=center vlign=center><div><font color=%s>%s</font></div></td>' % (
						indent, self.get_result_color('pass'), _pass))
					if _fail > 0:
						fail_color = self.get_result_color('fail')
					else:
						fail_color = self.get_result_color('pass')
					fp.write('%s    <td align=center vlign=center><div><font color=%s>%s</font></div></td>' % (
						indent, fail_color, _fail))
					fp.write('%s  </tr>' % (indent))
					_total=0
					_pass=0
					_fail=0
				fp.write('</table>')
			else:
				fp.write('%s<div><font size=3 color="red"> No new cases is added! </font></div>'%indent)
				fp.write('%s<div><hr></div>' % (indent))

		except Exception as e:
			logerror("[Exception] output_exec_details() get exception: %s", sys.exc_info()[:2])

	def output_diff_result(self,fp,result):
		indent = "    "
		diff_fail=self.diff_latest_run(result)
		print 'diff success'
		try:
			fp.write('<br/><br/>%s<div><font size=4><b><u><7> Different Status Comparing With Last Run:</u></b></font></div>' % (indent))
			if diff_fail:
				for suite in diff_fail:
					fp.write('<br/>%s<div><font size=3><b><u>%s</u></b></font></div>' % (
						indent, suite))
					fp.write('%s<div><table border=1 width=100%%>' % (indent))
					fp.write('%s    <td vlign=center align=center><div><b>Index</b></div></td>' % (indent))
					fp.write('%s    <td vlign=center align=center><div><b>Case Name</b></div></td>' % (indent))
					fp.write('%s    <td vlign=center align=center><div><b>Last Run</b></div></td>' % (indent))
					fp.write('%s    <td vlign=center align=center><div><b>This Run</b></div></td>' % (indent))
					fp.write('%s  </tr>' % (indent))

					j=1
					for case in diff_fail[suite]:
						fp.write('%s  <tr>' % (indent))
						fp.write('%s    <td align=center vlign=center><div>%s</div></td>' % (indent, str(j)))
						fp.write('%s    <td align=left vlign=center><div>%s</div></td>' % (indent, case))
						fp.write('%s    <td align=center vlign=center><div><font color=%s>%s</font></div></td>' % (
								indent, self.get_result_color('pass'), 'Pass'))
						fp.write('%s    <td align=center vlign=center><div><font color=%s>%s</font></div></td>' % (
								indent, self.get_result_color('fail'), 'Fail'))     
						fp.write('%s  </tr>' % (indent))
						j+=1
					fp.write('</table>')
			else:
				fp.write('%s<div><font size=3 color="red">The fail cases are not success in the last test !</font></div>'%indent)
				fp.write('%s<div><hr></div>' % (indent))

		except Exception as e:
			logerror("[Exception] output_exec_details() get exception: %s", sys.exc_info()[:2])

	def get_result_color(self, result):
		if cmp(result.upper(), "PASS") == 0:
			return "#0000FF";
		elif cmp(result.upper(), "FAIL") == 0:
			return "#FF0000";
		else:
			return "FFA000";

	def get_rate_color(self, grade):
		if grade >= 90:
			return "#00FF00";  # green
		elif grade >= 70:
			return "#FFFF00";  # yellow
		elif grade >= 40:
			return "#FFA000"  # orange
		else:
			return "#FF0000";  # red

	def time_span(self,start,end):
		s=datetime.strptime(start,"%Y%m%d %H:%M:%S")
		e=datetime.strptime(end,"%Y%m%d %H:%M:%S")
		return str(e-s)

	def parse_result(self, src):
		global all_start_time
		if (not os.path.isfile(src)):
			raise ValueError(ur"src file doesn't exist:" + src)  
		tree = etree.parse(src)
		root = tree.getroot()
		if (root.tag == 'robot'):
			all_start_time = root.attrib["generated"].split(".")[0]
		self.write_send_results(root)

	def rerun_parse_result(self,src):
		global re_all_start_time
		if not os.path.exists(src):
			self.rerun_state=False
			logerror('not extist rerun.xml')
			return
		tree = etree.parse(src)
		root = tree.getroot()
		if (root.tag == 'robot'):
			re_all_start_time = root.attrib["generated"].split(".")[0]
		self.write_rerun_results(root)

if (__name__ == "__main__"):
	if len(sys.argv)<3:
	    print "Error: need parameters: src dest"
	    sys.exit()
	src=sys.argv[1]
	dest=sys.argv[2]    
	parser = RobotXML2SCTMResult()

	parser.parse_result(src)
	parser.output_html(dest)
	
	# src=os.path.join(conf.REPORT_LOG_DIR, "output.xml")
	# dest=os.path.join(conf.REPORT_LOG_DIR, 'out.html')
	# parser=RobotXML2SCTMResult()
	# parser.parse_result(src)
	# parser.output_html(dest)
	# parser.send_detail_result_to_ftp()

	print "parse sucessfully"
