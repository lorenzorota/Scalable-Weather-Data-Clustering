import json
import time
import logging

from utils.wrapper_functions import *

if __name__ == '__main__':

	logging.basicConfig(level=logging.INFO)

	batch_sink_config_file = 'configs/batch-sink.json'
	batch_source_config_file = 'configs/batch-source.json'
	stream_sink_config_file = 'configs/stream-sink.json'
	stream_source_config_file = 'configs/stream-source.json'

	with open(batch_sink_config_file) as json_file:
		batch_sink_config = json.load(json_file)

	with open(batch_source_config_file) as json_file:
		batch_source_config = json.load(json_file)

	with open(stream_sink_config_file) as json_file:
		stream_sink_config = json.load(json_file)

	with open(stream_source_config_file) as json_file:
		stream_source_config = json.load(json_file)

	# clean up
	logging.info('--- Begin clean-up ---')
	exec_kill_connector('batch-source')
	exec_kill_connector('batch-sink')
	exec_delete_topic('common')
	exec_delete_dir('topics/common/')
	logging.info('--- Finished clean-up ---')

	# data ingestion here we go
	exec_init_connector(batch_source_config, 'batch-source')
	time.sleep(5)
	exec_block_until_done_source('batch-source')
	exec_kill_connector('batch-source')
	exec_init_connector(batch_sink_config, 'batch-sink')


	exec_block_until_done_sink('common', 'connect-batch-sink')
	exec_kill_connector('batch-sink')
	exec_delete_topic('common')
	