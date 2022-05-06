import requests
import json
import subprocess
from utils.response_codes import ResponseCode

connect_endpoint = "http://localhost:8083/connectors/"

def delete_dir(name_dir):
	result = subprocess.run(["docker", "exec", "-it", "namenode", \
		"hdfs", "dfs", "-rm", "-r", \
		"hdfs://namenode:9000/user/root/{}".format(name_dir)],
		capture_output=True, text=True)

	if 'No such file or directory' in result.stdout:
		return ResponseCode.NOT_EXISTS
	elif 'Deleted' in result.stdout:
		return ResponseCode.DONE
	else:
		return ResponseCode.ERROR