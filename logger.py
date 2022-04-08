import logging

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

streamHandler = logging.FileHandler('PROJECTS/tcp chat/trend.txt') #use your path
logger.addHandler(streamHandler)

formatter = logging.Formatter('%(asctime)s - %(message)s - %(levelname)s - %(name)s')
streamHandler.setFormatter(formatter)

