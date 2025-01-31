import json
import logging

from twisted.internet import defer, reactor

from stompest.config import StompConfig
from stompest.protocol import StompSpec

from stompest.asynchronous import Stomp
from stompest.asynchronous.listener import SubscriptionListener


class Consumer(object):
    QUEUE = '/queue/testOut'
    ERROR_QUEUE = '/queue/testConsumerError'

    def __init__(self, config=None):
        if config is None:
            config = StompConfig('tcp://localhost:61613')
        self.config = config

    @defer.inlineCallbacks
    def run(self):
        client = Stomp(self.config)
        yield client.connect()
        headers = {
            # client-individual mode is necessary for concurrent processing
            # (requires ActiveMQ >= 5.2)
            StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL,
            # the maximal number of messages the broker will let you work on at the same time
            'activemq.prefetchSize': '100',
        }
        client.subscribe(self.QUEUE, headers, listener=SubscriptionListener(self.consume, errorDestination=self.ERROR_QUEUE))

    def consume(self, client, frame):
        """
        NOTE: you can return a Deferred here
        """
        data = json.loads(frame.body.decode())
        print('Received frame with count %d' % data['count'])

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    Consumer().run()
    reactor.run()
