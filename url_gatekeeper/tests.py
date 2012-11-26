from django.test import TestCase
import middleware as middle
from django.http import (HttpResponseForbidden, HttpRequest,
                         HttpResponseRedirect, HttpResponse)
from . import add_token
from django.contrib.auth.models import User, AnonymousUser

class Mock(object):
    """Used to supply settings.TOKEN_REQUIRED_URLS via mock settings object.
    """

class _TestCase(TestCase):
    def assertForbidden(self, response):
        assert(isinstance(response, HttpResponseForbidden))
        self.assertEquals(403, response.status_code)

    def assertRedirect(self, response):
        assert(isinstance(response, HttpResponseRedirect))
        self.assertEquals(302, response.status_code)

    def assertNone(self, response):
        assert(response == None)

    def assertOK(self, response):
        self.assertEquals(200, response.status_code)
        self.assertEquals("OK", str(response.content))

class TestLoginRequired(_TestCase):
    def setUp(self):
        settings = Mock()
        settings.LOGIN_EXEMPT_URLS = (r'/public/.*$',)
        settings.LOGIN_URL = '/accounts/login/'
        settings.LOGOUT_URL = '/accounts/logout/'
        self.middle = middle.LoginRequiredMiddleware(_settings=settings)
        self.request = HttpRequest()

    def test_login_required(self):
        self.request.path_info = "/private/foo"
        self.request.user = AnonymousUser()
        self.assertRedirect(self.middle.process_request(self.request))

    def test_login_successful(self):
        self.request.path_info = "/public/foo"
        self.request.user = User()
        self.assertNone(self.middle.process_request(self.request))

    def test_login_not_required(self):
        self.request.path_info = "/public/foo"
        self.request.user = AnonymousUser()
        self.assertNone(self.middle.process_request(self.request))

class TestRequirePermission(_TestCase):
    def setUp(self):
        settings = Mock()
        settings.RESTRICTED_URLS = (
            (r'^/.*x.*/$', 'url_gatekeeper.x'),
            (r'^/.*z.*/$', 'url_gatekeeper.z'),
            (r'^/staff/*$', 'is_staff'),
        )
        settings.RESTRICTED_URLS_EXCEPTIONS = (
            r'^/login/$',
            r'^/logout/$',
        )
        self.middle = middle.RequirePermissionMiddleware(_settings=settings)
        self.request = HttpRequest()
        user = User()
        user.save()
        self.request.user = user

    def test_view_OK(self):
        def view(request): return HttpResponse("OK")
        self.request.path_info = "/login/"
        self.assertNone(self.middle.process_view(self.request, view, [], {}))

    def test_view_permitted(self):
        def view(request): return HttpResponse("OK")
        self.request.path_info = "/x/"
        self.request.user.has_perm = lambda x: x == 'url_gatekeeper.x'
        self.assertOK(self.middle.process_view(self.request, view, [], {}))

    def test_view_restricted(self):
        def view(request): return HttpResponse("OK")
        self.request.path_info = "/x/"
        self.request.user.has_perm = lambda x: x == 'url_gatekeeper.y' #*#
        self.assertForbidden(self.middle.process_view(self.request, view, [], {}))

    def test_view_is_staff(self):
        def view(request): return HttpResponse("OK")
        self.request.path_info = "/staff/"
        self.assertForbidden(self.middle.process_view(self.request, view, [], {}))
        self.request.user.is_staff = True
        self.assertOK(self.middle.process_view(self.request, view, [], {}))

    def test_view_unlisted(self):
        def view(request): return HttpResponse("OK")
        self.request.path_info = "/jj/"
        self.request.user.has_perm = lambda x: True
        self.assertForbidden(self.middle.process_view(self.request, view, [], {}))

    def test_view_restricted_twice(self):
        def view(request): return HttpResponse("OK")
        self.request.path_info = "/xz/"
        self.request.user.has_perm = lambda x: x == 'url_gatekeeper.x' #*#
        self.assertForbidden(self.middle.process_view(self.request, view, [], {}))
        self.request.user.has_perm = lambda x: x == 'url_gatekeeper.y' #*#
        self.assertForbidden(self.middle.process_view(self.request, view, [], {}))
        self.request.user.has_perm = lambda x: x in ['url_gatekeeper.z',
                                                     'url_gatekeeper.x']#*#
        self.assertOK(self.middle.process_view(self.request, view, [], {}))

class TestTokenRequired(_TestCase):
    def setUp(self):
        settings = Mock()
        settings.TOKEN_REQUIRED_URLS = (r'/image/.*$', r'/img/.*')
        self.middle = middle.TokenRequiredMiddleware(_settings=settings)
        self.request = HttpRequest()
        self.request.path_info = "/image/23/"

    def add_token(self):
        url = add_token('/image/23/')
        params = url.split('?')[1]
        key, value = params.split('=')
        self.request.GET[key] = value

    def test_token_missing(self):
        self.assertForbidden(self.middle.process_request(self.request))

    def test_token_present(self):
        self.add_token()
        self.assertNone(self.middle.process_request(self.request))

    def test_token_present_url_wrong(self):
        self.add_token()
        self.request.path_info = "/img/23/"
        self.assertForbidden(self.middle.process_request(self.request))

    def test_token_not_required(self):
        self.add_token()
        self.request.path_info = "/acceptable/23/"
        self.assertNone(self.middle.process_request(self.request))
