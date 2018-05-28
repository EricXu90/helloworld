import sys
import commands

import VSAPI_001_pb2      #schema_id VASPI_001
import DDI_001_pb2        #schema_id DDI_001
import SAL_001_pb2        #schema_id SAL_001
import usandbox_pb2       #schema_id Usandbox_001

UNPACK_TOOL="tmfbeunpack"
REMOVE_FILE="rm -f "

def parse_blob(parseHandle,offset,file_name,show_ori_string):
	
	python_path = '/'.join(sys.argv[0].split('/')[:-1])
	cmd = "%s/%s %s"%(python_path,UNPACK_TOOL,file_name)
	commands.getoutput(cmd)

        cmd = 'pwd'
        current_path = commands.getoutput(cmd)
	file_name =  "%s/%s.raw" % (current_path,file_name.split('/')[-1])

	parse_raw_with_header(parseHandle,offset,file_name,show_ori_string)

	cmd = REMOVE_FILE + file_name
	commands.getoutput(cmd)
	
	
def parse_raw_with_header(parseHandle,offset,file_name,show_ori_string):
	
	f = open(file_name, "rb")
	tmfbed_data=f.readlines()
	
	if show_ori_string == True:
		print "\n"
		print "original file data.................................."
		print tmfbed_data
		print "\n"
	
	messages=tmfbed_data[offset:]
	
	for line in tmfbed_data[0:offset-1]:
		print line.strip('\n')

	if show_ori_string == True:
		print "parsing data.................................."
		print messages
		print "\n"
	
	data="".join(messages)

	parseHandle.ParseFromString(data)

	f.close()

	print parseHandle
	
def parse_raw(parseHandle,offset,file_name,show_ori_string):
	
	f = open(file_name, "rb")
	tmfbed_data=f.readlines()
	
	if show_ori_string == True:
		print "\n"
		print "original file data.................................."
		print tmfbed_data
		print "\n"
	
	messages=tmfbed_data[0:]
	
	if show_ori_string == True:
		print "parsing data.................................."
		print messages
		print "\n"
	
	data="".join(messages)

	parseHandle.ParseFromString(data)

	f.close()

#	print parseHandle

def run():
	if len(sys.argv)<3:
		print "\n\tUsage: python  parse_blob.py  -s=schema  -f=file_path  -i=input_type -p=print_original_data\n"
		print "\tschema(required):             V(SAPI) / D(DI) / S(AL) / U(sandbox)"
		print "\tinput_type(optional):         B(lob) / H(raw_with_head) / R(aw)   default:B"
		print "\tshow_original_data(optional): Y(es) / N(o)                        default:N\n"
		print "\tex: python  parse_blob.py  -s=V  -d=blob_file/DDEI/b.2fdda5c5c033f62e6f5ced81c4afe3cebda5e11d  -i=B -p=Y\n"
		exit(0);
	
	parseMethod_id = "B" #default to parse blob file
	show_ori_string = False
	offset = 10 #default skip 10 lines
	
	for argv in sys.argv:
		if argv.split('=')[0] == "-s":
			schema_id = argv.split('=')[1]
			if schema_id == "S":
				offset = 9
		if argv.split('=')[0] == "-f":
			file_name = argv.split('=')[1]
		if argv.split('=')[0] == "-i":
			parseMethod_id = argv.split('=')[1]
		if argv.split('=')[0] == "-p" and argv.split('=')[1] == "Y":
			show_ori_string = True
	
	
	schema = {"V":VSAPI_001_pb2.VsapiFeedBackInfo,"D":DDI_001_pb2.DDIFeedBackInfo,"S":SAL_001_pb2.BEPFeedBack,"U":usandbox_pb2.UsandboxBlacklist}
	parseMethod = {"B":parse_blob,"H":parse_raw_with_header,"R":parse_raw}
	
	parseHandle = schema.get(schema_id,schema[schema_id])()
	parseMethod.get(parseMethod_id,parseMethod[parseMethod_id])(parseHandle,offset,file_name,show_ori_string)

	
if __name__ == '__main__':
	run()

	










