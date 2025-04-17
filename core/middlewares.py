from django.contrib.sessions.middleware import SessionMiddleware

class SeparateSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        if request.path.startswith("/admin/"):  # Nếu là trang admin
            request.session_cookie_name = "admin_sessionid"
        else:  # Nếu là trang user
            request.session_cookie_name = "user_sessionid"
        super().process_request(request)
