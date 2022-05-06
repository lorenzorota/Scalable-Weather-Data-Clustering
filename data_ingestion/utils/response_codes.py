from enum import Enum

class ResponseCode(Enum):
	DONE = 1
	UNASSIGNED = 2
	OFFLINE = 3
	FAILED = 4
	WORKING = 5
	EXISTS = 6
	NOT_EXISTS = 7
	ERROR = 8