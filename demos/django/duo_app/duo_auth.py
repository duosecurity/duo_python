from functools import wraps

from django.http import HttpResponseRedirect
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.utils.decorators import available_attrs
from django.contrib.auth.decorators import login_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlquote
from django.shortcuts import render
from django.utils.translation import ugettext as _

import duo_web
from six.moves.urllib.parse import urlencode


def duo_username(user):
    """ Return the Duo username for user. """
    return user.username


def duo_authenticated(request):
    """
    Return True if a session shows the user has authenticated with Duo.
    """
    if request.session.get('duo_authenticated') == request.user.username:
        return True
    return False


def duo_authenticate(request):
    """
    Record in the session that the user has authenticated with Duo.
    """
    request.session['duo_authenticated'] = request.user.username


def duo_unauthenticate(request):
    """
    Record in the session that the user has not authenticated with Duo.
    """
    try:
        del request.session['duo_authenticated']
    except KeyError:
        pass


# We could use just use django.contrib.auth.decorators.user_passes_test here
# if Duo authenticatedness was a property of the user, and there's probably
# a way to do that.
def duo_auth_required(view_func, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user has been authenticated with
    Duo, redirecting to the Duo authentication page if necessary.
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if duo_authenticated(request):
                return view_func(request, *args, **kwargs)
            path = urlquote(request.get_full_path())
            return HttpResponseRedirect(
                '%s?%s=%s' % (
                    settings.DUO_LOGIN_URL, redirect_field_name, path))
        return _wrapped_view
    return decorator(view_func)


# There are a few more validations which could be done here as in
# django.contrib.auth.login, such as checking the form and redirect,
# and setting a test cookie.
@login_required
@require_http_methods(['GET', 'POST'])
def login(request):
    """
    View to authenticate the user locally and with Duo, redirecting to the next
    argument if given.
    For a GET, show the Duo form, which posts back with the Duo token.
    For a POST with successful authorization, redirect to the next argument,
    or show some default content.  Without successful authorization, redirect
    back here to try again.
    """
    if request.method == 'GET':
        message = request.GET.get(
            'message', 'Secondary authorization required.')
        next_page = request.GET.get('next')
        sig_request = duo_web.sign_request(
            settings.DUO_IKEY, settings.DUO_SKEY, settings.DUO_AKEY,
            duo_username(request.user))
        context = {
            'message': message,
            'next': next_page,
            'duo_css_src': '/'.join([settings.STATIC_URL,
                                     'Duo-Frame.css']),
            'duo_js_src': '/'.join([settings.STATIC_URL,
                                     'Duo-Web-v2.js']),
            'duo_host': settings.DUO_HOST,
            'post_action': request.path,
            'sig_request': sig_request
        }
        return render(request, 'duo_login.html', context)
    elif request.method == 'POST':
        sig_response = request.POST.get('sig_response', '')
        duo_user = duo_web.verify_response(
            settings.DUO_IKEY, settings.DUO_SKEY, settings.DUO_AKEY,
            sig_response)
        next_page = request.POST.get('next')
        if duo_user is None:
            # Redirect user to try again, keeping the next argument.
            # Note that we don't keep any other arguments.
            arg_map = {'message': 'Duo access denied.'}
            if next_page:
                arg_map['next'] = next_page
            redirect_url = '%s?%s' % (
                request.path, urlencode(arg_map))
            return HttpResponseRedirect(redirect_url)
        else:
            duo_authenticate(request)
            if not next_page:
                next_page = settings.LOGIN_REDIRECT_URL
            return HttpResponseRedirect(next_page)


def logout(request, next_page=None,
           template_name='duo_logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME):
    """
    View to remove Duo authentication.
    """
    duo_unauthenticate(request)
    if next_page is None:
        redirect_to = request.GET.get(redirect_field_name, '')
        if redirect_to:
            return HttpResponseRedirect(redirect_to)
        else:
            current_site = get_current_site(request)
            return render(request, template_name, {
                'site': current_site,
                'site_name': current_site.name,
                'title': _('Logged out')
            })
    else:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page or request.path)
