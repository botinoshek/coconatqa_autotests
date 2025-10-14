from Modul_4.Cinescope.api.auth_api import AuthAPI
from Modul_4.Cinescope.api.user_api import UserAPI
from Modul_4.Cinescope.api.admin_user_api import AdminAuthAPI
from Modul_4.Cinescope.api.movies_api import MoviesAPI



class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthAPI(session)
        self.user_api = UserAPI(session)
        self.admin_user_api = AdminAuthAPI(session)
        self.movies_api = MoviesAPI(session)

    def close_session(self):
        self.session.close()
