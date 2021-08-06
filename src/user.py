class User:
    def __init__(self, username: str, chat_id: int, page_url: str = "", ice_cream_flavors: list[str] = list()):
        self.username = username
        self.chat_id = chat_id
        self.page_url = page_url
        self.ice_cream_flavors = ice_cream_flavors

    username: str
    chat_id: int
    page_url: str
    ice_cream_flavors: list[str]
