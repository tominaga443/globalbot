# -*- coding: utf-8 -*-

import json
import os
import requests
import falcon
import pyoxford
import urllib.request
from logging import DEBUG, StreamHandler, getLogger
from mstranslator.mstranslator import MSTranslator
from linebot.line import Line
from linebot.models.line_types import ContentType

# logger
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class Application(object):
    def on_post(self, req, resp):
        line_keys = self.__get_line_keys()
        line = Line(*line_keys)
        ms_client_id = os.getenv("MS_CLIENT_ID")
        ms_client_secret = os.getenv("MS_CLIENT_SECRET")
        oxford_primary_key = os.getenv("OXFORD_PRIMARY_KEY")
        oxford_secondary_key = os.getenv("OXFORD_SECONDARY_KEY")
        translator = MSTranslator(ms_client_id, ms_client_secret)

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        receive_params = json.loads(body.decode('utf-8'))
        logger.debug('receive_params: {}'.format(receive_params))

        reqests = line.receive(receive_params)
        if len(reqests) == 0:
                raise Exception("No message is received")

        for req in reqests:
            text = ""
            request_msg = req.content
            print(vars(req))
            print(vars(request_msg))
            print(oxford_primary_key)
            print(oxford_secondary_key)

            if request_msg.content_type is ContentType.audio:
                content = line.get_content(request_msg.message_id)
                speech_api = pyoxford.speech(oxford_primary_key, oxford_secondary_key)
                reply = speech_api.speech_to_text(binary_or_path=content, lang="ja-JP")
                response = request_msg.reply()
                response.set_text(reply)
                line.post(response)

                text = reply
            else:
                text = request_msg.text

            response = request_msg.reply()
            src_lang = translator.detect(text)
            reply = "言語は" + src_lang + "です"
            response.set_text(reply)
            line.post(response)

            response = request_msg.reply()
            reply = translator.translate(text)
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
