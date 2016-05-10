class UserProfile():

    def __init__(self, contact, lang=None, to_user=""):
        self.contact = contact
        self.name = contact.name
        self.mid = contact.mid
        self.lang = lang
        self.to_user = to_user
