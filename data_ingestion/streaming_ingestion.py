import json
import time
import logging
import sys, getopt

from utils.wrapper_functions import *

def main(argv):

	# parse arguments and options
	try:
		opts, args = getopt.getopt(argv, "hsSR", ["help", "start", "stop", "reset"])
	except getopt.GetoptError:
		print('invalid option')
		print('Try `python streaming_ingestion.py -h\' for more information.')
		sys.exit(2)

	if opts == []:
	    print('No options passed. Expected [\'--help\', \'--start\', \'--stop\', \'--reset\']')
	    print('Try `python streaming_ingestion.py -h\' for more information.')
	    sys.exit()

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print('usage: ./streaming_ingestion.py [options]')
			print('-h or --help\t: displays information on options and arguments')
			print('-s or --start\t: start the streaming process')
			print('-S or --stop\t: stop the streaming process')
			print('-R or --reset\t: reset the kafka topic and hdfs directory')
			exit()
		elif opt in ("-s", "--start"):
			return 'start'
		elif opt in ("-S", "--stop"):
			return 'stop'
		elif opt in ("-R", "--reset"):
			return 'reset'
if __name__ == '__main__':

	mode = main(sys.argv[1:])

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

	if mode == 'start':
		logging.info('--- Begin streaming ---')
		exec_init_connector(stream_source_config, 'stream-source')
		exec_init_connector(stream_sink_config, 'stream-sink')
	elif mode == 'stop':
		logging.info('--- Stop streaming ---')
		exec_kill_connector('stream-source')
		exec_kill_connector('stream-sink')
	elif mode == 'reset':
		logging.info('--- Begin clean-up ---')
		exec_kill_connector('stream-source')
		exec_kill_connector('stream-sink')
		exec_delete_topic('stream')
		exec_delete_dir('topics/stream/')
		logging.info('--- Finished clean-up ---')