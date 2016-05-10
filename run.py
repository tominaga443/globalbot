# -*- coding: utf-8 -*-

import json
import os
import re
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
                text = request_msg.text
                result = re.match("@", text)
                if result is None:
                    self.__translate_message(line, request_msg)
                else:
                    self.__set_config(line, request_msg)

    def __resist_user(self, line, request_msg):
        translator = MSTranslator(ms_client_id, ms_client_secret)
        r = redis.from_url(os.environ.get("REDIS_URL"))

        user_id = request_msg.from_mid
        contact = line.get_user_profile(user_id)
        profile = UserProfile(contact.name, contact.mid, image_url=contact.picture_url)
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

    def __translate_message(self, line, request_msg):
        translator = MSTranslator(ms_client_id, ms_client_secret)
        r = redis.from_url(url=os.environ.get("REDIS_URL"))


        user_id = request_msg.from_mid
        data = r.hgetall(user_id)
        profile = self.__decode(data)
        logger.debug("profile: {}".format(profile))
        profile = UserProfile(**profile)

        target_profile = self.__get_user_profile(id=profile.to_user)
        target_lang = Language(target_profile.lang)

        if request_msg.content_type is ContentType.text:
            text = request_msg.text

            # Detect
            #src_lang = translator.detect(text)
            #reply_msg = src_lang.name + "から" + target_lang.name + "に翻訳します"
            #self.__post_reply(line, request_msg, reply_msg)

            reply_msg = translator.translate(text, target_lang.code)
            self.__post_reply(line, request_msg, reply_msg, profile.to_user)

    def __set_config(self, line, request_msg):
        text = request_msg.text
        command = text[1:]

        user_id = request_msg.from_mid
        dist_user = command
        dist_profile = self.__get_user_profile(name=dist_user)
        print("dist_user: " + dist_profile.name)
        self.__set_dist_user(user_id, dist_profile.mid)

        reply_msg = dist_profile.name + "さんとつながりました"
        self.__post_reply(line, request_msg, reply_msg, user_id)

    def __post_reply(self, line, request_msg, reply_msg, target=""):
        response = request_msg.reply()
        response.set_text(reply_msg)
        if target:
            response.to_mids = [target]
        line.post(response)

    def __get_user_profile(self, id="", name=""):
        list = self.__get_user_list()
        if id:
            for prof in list:
                if prof.mid == id:
                    return prof
        elif name:
            for prof in list:
                if prof.name == name:
                    return prof
        else:
            return None

    def __get_user_list(self):
        r = redis.from_url(url=os.environ.get("REDIS_URL"))

        keys = r.keys()
        list = []
        for key in keys:
            data = r.hgetall(key)
            profile = self.__decode(data)
            p = UserProfile(**profile)
            list.append(p)

        return list

    def __get_line_keys(self):
        channel_id = os.getenv("LINE_CHANNEL_ID")
        channel_secret = os.getenv("LINE_CHANNEL_SECRET")
        channel_mid = os.getenv("LINE_CHANNEL_MID")
        proxy = os.getenv("FIXIE_URL")  # for heroku

        keys = (channel_id, channel_secret, channel_mid, proxy)
        return keys

    def __set_dist_user(self, src_id, dist_id):
        r = redis.from_url(url=os.environ.get("REDIS_URL"))
        data = r.hgetall(src_id)
        profile = self.__decode(data)
        logger.debug("profile: {}".format(profile))

        profile = UserProfile(**profile)
        profile.to_user = dist_id
        dic = profile.__dict__
        logger.debug("profile: {}".format(dic))

        r.hmset(profile.mid, dic)

    def __decode(self, data):
        dic = {}
        for k, v in data.items():
            key = k.decode("utf-8")
            value = v.decode("utf-8")
            dic[key] = value
        return dic


api = falcon.API()
api.add_route('/callback', Application())
