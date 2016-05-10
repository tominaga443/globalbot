# -*- coding: utf-8 -*-

import json
import os
import requests
import falcon
import pyoxford
import urllib.request
from urllib.parse import urlparse
from logging import DEBUG, StreamHandler, getLogger
from globalbot.user_profile import UserProfile
from microsofttranslator import Translator
from mstranslator.mstranslator import MSTranslator
from mstranslator.language import Language
from linebot.line import Line
from linebot.models.line_types import EventType, ContentType
import redis

ms_client_id = os.getenv("MS_CLIENT_ID")
ms_client_secret = os.getenv("MS_CLIENT_SECRET")
oxford_primary_key = os.getenv("OXFORD_PRIMARY_KEY")
oxford_secondary_key = os.getenv("OXFORD_SECONDARY_KEY")

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
            if req.event_type is EventType.operation:
                request_msg = req.content
                self.__resist_user(line, request_msg)
            elif req.event_type is EventType.message:
                request_msg = req.content
                self.__reply_message(line, request_msg)

    def __resist_user(self, line, request_msg):
        translator = MSTranslator(ms_client_id, ms_client_secret)
        r = redis.from_url(os.environ.get("REDIS_URL"))

        user_id = request_msg.from_mid
        contact = line.get_user_profile(user_id)
        profile = UserProfile(contact.name, contact.mid)
        reply_msg = "こんにちは、" + profile.name + "さん！"
        self.__post_reply(line, request_msg, reply_msg)

        lang = translator.detect(profile.name)
        profile.lang = lang.code
        reply_msg = "あなたの言語を" + lang.name + "に設定しました"
        self.__post_reply(line, request_msg, reply_msg)

        reply_msg = "言語を変更するには「@reset」と発言してください。その次に発言した言語で再設定されます。"
        self.__post_reply(line, request_msg, reply_msg)

        profile.to_user = profile.mid  #TODO:selectable
        dic = profile.__dict__
        logger.debug("profile: {}".format(dic))
        print(dic.__class__.__name__)
        r.hmset(profile.mid, dic)

    def __reply_message(self, line, request_msg):
        translator = MSTranslator(ms_client_id, ms_client_secret)
        r = redis.from_url(url=os.environ.get("REDIS_URL"))


        user_id = request_msg.from_mid
        data = r.hgetall(user_id)
        profile = self.__dict_to_str(data)
        logger.debug("profile: {}".format(profile))
        profile = UserProfile(**profile)
        target_lang = Language(profile.lang)

        if request_msg.content_type is ContentType.text:
            text = request_msg.text

            src_lang = translator.detect(text)
            reply_msg = src_lang.name + "から" + target_lang.name + "に翻訳します"
            self.__post_reply(line, request_msg, reply_msg)

            reply_msg = translator.translate(text, target_lang.code)
            self.__post_reply(line, request_msg, reply_msg)

    def __post_reply(self, line, request_msg, reply_msg):
        response = request_msg.reply()
        response.set_text(reply_msg)
        line.post(response)

    def __get_line_keys(self):
        channel_id = os.getenv("LINE_CHANNEL_ID")
        channel_secret = os.getenv("LINE_CHANNEL_SECRET")
        channel_mid = os.getenv("LINE_CHANNEL_MID")
        proxy = os.getenv("FIXIE_URL")  # for heroku

        keys = (channel_id, channel_secret, channel_mid, proxy)
        return keys

    def __dict_to_str(self, data):
        dic = {}
        for k, v in data.items():
            key = k.decode("utf-8")
            value = v.decode("utf-8")
            dic[key] = value
        return dic


api = falcon.API()
api.add_route('/callback', Application())
