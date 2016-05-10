from linebot.models.line_types import EventType
from linebot.models.message import Message
from linebot.models.operation import Operation


class LineRequest():

    def __init__(self,
                 from_id="",
                 from_channel="",
                 to_mid="",
                 to_channel="",
                 event_type=EventType.message,
                 event_id="",
                 content=None):
        self.from_id = from_id  # Fixed
        self.from_channel = from_channel  # Fixed
        self.to_mid = to_mid
        self.to_channel = to_channel  # this id means bot api server
        self.event_type = event_type
        self.event_id = event_id
        self.content = content

    @classmethod
    def parse(cls, body):
        requests = []
        if "result" in body:
            for r in body["result"]:
                req = LineRequest(
                    r["from"],
                    r["fromChannel"],
                    r["to"],
                    r["toChannel"],
                    EventType(r["eventType"]),
                    r["id"],
                )
                if req.event_type is EventType.message:
                    req.content = Message.parse(r["content"])
                elif req.event_type is EventType.operation:
                    req.content = Operation.parse(r["content"])
                requests.append(req)

        return requests
