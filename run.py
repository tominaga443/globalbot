import json
import os
import requests
import falcon
from logging import DEBUG, StreamHandler, getLogger
from linebot.line import Line

# logger
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class Application(object):
    def on_post(self, req, resp):
        keys = self.__get_line_keys()
        line = Line(*keys)

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        receive_params = json.loads(body.decode('utf-8'))
        logger.debug('receive_params: {}'.format(receive_params))

        reqs = line.receive(receive_params)
        if len(reqs) == 0:
                raise Exception("No message is received")

        for r in reqs:
            request_msg = r.content
            response = request_msg.reply()
            reply = request_msg.text
            response.set_text(reply)
            line.post(response)

    def __get_line_keys(self):
        channel_id = os.getenv("LINE_CHANNEL_ID")
        channel_secret = os.getenv("LINE_CHANNEL_SECRET")
        channel_mid = os.getenv("LINE_CHANNEL_MID")
        proxy = os.getenv("FIXIE_URL")  # for heroku

        keys = (channel_id, channel_secret, channel_mid, proxy)
        return keys


api = falcon.API()
api.add_route('/callback', Application())
