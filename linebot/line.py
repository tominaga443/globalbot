import json
import requests
from linebot.models.line_request import LineRequest
from linebot.models.line_response import LineResponse
from linebot.models.line_contact import LineContact

class Line():
    HOST = "trialbot-api.line.me"

    def __init__(self,
                 channel_id,
                 channel_secret,
                 mid,
                 proxy=""):
        self.channel_id = channel_id
        self.channel_secret = channel_secret
        self.mid = mid
        self.proxies = {}
        if proxy:
            self.proxies = {
                "http": proxy,
                "https": proxy
            }


    @classmethod
    def receive(cls, body) -> [LineRequest]:
        _b = body
        if _b is str:
            _b = json.loads(_b)

        return LineRequest.parse(_b)

    def get_content(self, message_id):
        url = self.__make_url("/v1/bot/message/" + message_id + "/content")
        headers = {
            "X-Line-ChannelID": self.channel_id,
            "X-Line-ChannelSecret": self.channel_secret,
            "X-Line-Trusted-User-With-ACL": self.mid
        }

        resp = requests.get(url, headers=headers, proxies=self.proxies)
        if not resp.ok:
            raise Exception("Url({0}), Status({1} {2}): header={3}, proxy={4}, body={5}".format(
                url, resp.status_code, resp.reason, headers, self.proxies, r_dict
            ))

        return resp.content

    def get_user_profile(self, user_mid):
        url = self.__make_url("/v1/profiles?mids=" + user_mid)
        headers = {
            "X-Line-ChannelID": self.channel_id,
            "X-Line-ChannelSecret": self.channel_secret,
            "X-Line-Trusted-User-With-ACL": self.mid
        }

        body = requests.get(url, headers=headers, proxies=self.proxies)

        receive_params = json.loads(body.text)
        print('receive_params: {}'.format(receive_params))

        contacts = LineContact.parse(receive_params)

        return contacts[0]

    def post(self, message: LineResponse):
        url = self.__make_url("/v1/events")
        headers = {
            "X-Line-ChannelID": self.channel_id,
            "X-Line-ChannelSecret": self.channel_secret,
            "X-Line-Trusted-User-With-ACL": self.mid,
            "Content-Type": "application/json; charset=UTF-8"
        }

        r_dict = message.to_dict()

        resp = requests.post(url, data=json.dumps(r_dict), headers=headers, proxies=self.proxies)
        if not resp.ok:
            raise Exception("Url({0}), Status({1} {2}): header={3}, proxy={4}, body={5}".format(
                url, resp.status_code, resp.reason, headers, self.proxies, r_dict
            ))

    def __make_url(self, path):
        url = "https://" + self.HOST + path
        return url
