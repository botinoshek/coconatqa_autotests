from .auth_api import AuthAPI
from .user_api import UserAPI
from .admin_user_api import AdminAuthAPI
from .movies_api import MoviesAPI



class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthAPI(session)
        self.user_api = UserAPI(session)
        self.admin_user_api = AdminAuthAPI(session)
        self.movies_api = MoviesAPI(session)

    def close_session(self):
        self.session.close()
