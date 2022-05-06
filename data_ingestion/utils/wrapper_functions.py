import time
import logging

from utils.response_codes import ResponseCode
from utils.kafka_utils import *
from utils.hadoop_utils import *

def exec_kill_connector(connector_name):
	logging.info('Trying to kill connector: {} ...'.format(connector_name))
	try:
		resp = kill_connector(connector_name)
	except Exception as err:
		logging.warn('-> Something bad happened')
		logging.warn(err)
		exit(1)
	if resp == ResponseCode.NOT_EXISTS or resp == ResponseCode.DONE:
		logging.info('-> Done')

def exec_delete_topic(topic_name):
	logging.info('Trying to delete topic: {} ...'.format(topic_name))
	resp = delete_topic(topic_name)
	if resp == ResponseCode.DONE:
		logging.info('-> Done')
	elif resp == ResponseCode.NOT_EXISTS:
		logging.info('-> Doesn\'t exist')

def exec_delete_dir(dir_name):
	logging.info('Trying to delete directory hdfs://namenode:9000/user/root/{} ...'.format(dir_name))
	resp = delete_dir(dir_name)
	if resp == ResponseCode.DONE:
		logging.info('-> Done')
	elif resp == ResponseCode.NOT_EXISTS:
		logging.info('-> Doesn\'t exist')

def exec_init_connector(config, connector_name):
	# now we start the source connector
	logging.info('Trying to initialize connector: {} ...'.format(connector_name))
	try:
		resp = init_connector(config)
	except Exception as err:
		logging.warn('-> Something bad happened')
		logging.warn(err)
		exit(1)

	if resp == ResponseCode.DONE:
		logging.info('-> Done')
	else:
		logging.info('-> Failed')

def exec_block_until_done_source(connector_name):
	logging.info('Waiting for connector {} to finish...'.format(connector_name))
	while True:
		try:
			res = get_status(connector_name)
			if res == ResponseCode.DONE:
				logging.info('-> Done')
				break
			elif res == ResponseCode.FAILED:
				logging.info('-> One of the nodes failed')
				break
			elif res == ResponseCode.WORKING:
				time.sleep(1)
			elif res == ResponseCode.OFFLINE:
				logging.info('-> Connector offline')
				break
		except requests.exceptions.ConnectionError as err:
			logging.warn('Unable to make GET request to ' + url )
		except Exception as err:
			logging.warn('Something bad happened')
			logging.warn(err)

def exec_block_until_done_sink(topic_name, connector_name):
	logging.info('Waiting for connector {} to finish...'.format(connector_name))
	source_offset = int(get_topic_offset(topic_name))
	while True:
		resp = get_consumer_offset(connector_name)
		if resp != ResponseCode.NOT_EXISTS and resp != '-' and resp != 'out':
			sink_offset = int(resp)
			if (source_offset // sink_offset == 1):
				logging.info('-> Done')
				break
			else:
				time.sleep(1)
