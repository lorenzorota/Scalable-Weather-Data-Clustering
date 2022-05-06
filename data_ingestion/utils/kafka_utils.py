import requests
import json
import subprocess
from utils.response_codes import ResponseCode

connect_endpoint = "http://localhost:8083/connectors/"

def get_status(connector_name):
	
	url = connect_endpoint + "{}/status".format(connector_name)
	payload={}
	headers = {}
	response = requests.request("GET", url, headers=headers, data=payload)
	resp = response.json()

	if 'error_code' in resp.keys():
		if resp['error_code'] == 404:
			return ResponseCode.OFFLINE
		else:
			raise Exception('some error (code: {}) occured'.format(resp['error_code']))
	else:
		tasks = resp['tasks']
		count = 0
		failed = False
		for task in tasks:
			if task['state'] == 'UNASSIGNED':
				count += 1
			if task['state'] == 'FAILED':
				failed = True
		if failed:
			return ResponseCode.FAILED
		elif count == len(tasks):
			return ResponseCode.DONE
		else:
			return ResponseCode.WORKING

def init_connector(config):
	url = connect_endpoint
	payload = config
	headers = {'Content-Type': 'application/json'}
	response = requests.request("POST", url, headers=headers, json=payload)
	if response.status_code != 204:
		resp = response.json()
		if 'error_code' in resp.keys():
			if resp['error_code'] == 409:
				return ResponseCode.EXISTS
			else:
				raise Exception('some error (code: {}) occured'.format(resp['error_code']))
		else:
			return ResponseCode.DONE

def kill_connector(connector_name):
	url = connect_endpoint + "{}".format(connector_name)
	payload={}
	headers = {}
	response = requests.request("DELETE", url, headers=headers, data=payload)
	if response.status_code != 204:
		resp = response.json()
		if 'error_code' in resp.keys():
			if resp['error_code'] == 404:
				return ResponseCode.NOT_EXISTS
			else:
				raise Exception('some error (code: {}) occured'.format(resp['error_code']))
	return ResponseCode.DONE

def delete_topic(topic_name):
	result = subprocess.run(["docker", "exec", "-it", "zookeeper", \
		"kafka-topics", \
		"--bootstrap-server", "kafka:9092", \
		"--delete", \
		"--topic", \
		topic_name], capture_output=True, text=True)

	if 'not exist' in result.stdout:
		return ResponseCode.NOT_EXISTS
	elif result.stdout == '':
		return ResponseCode.DONE
	else:
		return ResponseCode.ERROR


# we use topic common
def get_topic_offset(topic_name):
	result = subprocess.run(["docker", "exec", "-it", "zookeeper", \
		"kafka-run-class", \
		"kafka.tools.GetOffsetShell", \
		"--broker-list", "kafka:9092", \
		"--topic", topic_name], capture_output=True, text=True)

	if result.stdout == '':
		return ResponseCode.NOT_EXISTS
	else:
		string = result.stdout
		out = string.split(':')[2].strip()
		return out

# here we use group connect-batch-sink
def get_consumer_offset(group_name):
	result = subprocess.run(["docker", "exec", "-it", "zookeeper", \
		"kafka-consumer-groups", \
		"--bootstrap-server", "kafka:9092", \
		"--group", group_name, \
		"--describe"], capture_output=True, text=True)
	if result.stdout == '':
		return ResponseCode.NOT_EXISTS
	else:
		string = result.stdout
		# this is just a very compact way of extracting the CURRENT-OFFSET :)
		out = ' '.join(string.split('\n')[2].split()).split(' ')[3]
		return out