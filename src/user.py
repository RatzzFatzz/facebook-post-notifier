class User:
    def __init__(self, username: str, page_url: str = "", ice_cream_flavors: list[str] = list()):
        self.username = username
        self.page_url = page_url
        self.ice_cream_flavors = ice_cream_flavors

    username: str
    page_url: str
    ice_cream_flavors: list[str]
