from linebot.models.line_response import LineResponse


class Operation():

    def __init__(self, message=None, from_mid=""):
        self.message = message
        self.from_mid = from_mid

    @classmethod
    def parse(cls, body):
        instance = Operation(body["message"], body["params"][0])
        return instance

    def reply(self) -> LineResponse:
        resp = LineResponse(self.from_mid)
        return resp
