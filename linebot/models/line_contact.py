class LineContact():

    def __init__(self,
                 name="",
                 mid="",
                 picture_url="",
                 status_message=""):
        self.name = name
        self.mid = mid
        self.picture_url = picture_url
        self.status_message = status_message

    @classmethod
    def parse(cls, body):
        contacts = []
        if "contacts" in body:
            for c in body["contacts"]:
                user = LineContact(
                    c["displayName"],
                    c["mid"],
                    c["pictureUrl"],
                    c["statusMessage"]
                )
                contacts.append(user)

        return contacts
