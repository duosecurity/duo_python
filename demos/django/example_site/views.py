from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from duo_app import duo_auth


@login_required
@duo_auth.duo_auth_required
def duo_private(request):
    """
    View which requires a login and Duo authentication.
    """
    return HttpResponse(
        '<p>Content protected by Django and Duo auth.'
        '<p><a href="/accounts/logout">Log out of primary Django auth.</a>'
        '<p><a href="/accounts/duo_logout">Log out of secondary Duo auth.</a>'
    )


@login_required
def duo_private_manual(request):
    """
    View which requires a login, and manually checks for Duo authentication.
    """
    if not duo_auth.duo_authenticated(request):
        return HttpResponseRedirect(
            '%s?next=%s' % (settings.DUO_LOGIN_URL, request.path))
    return HttpResponse(
        '<p>Content protected by Django and Duo auth.'
        '<p><a href="/accounts/logout">Log out of primary Django auth.</a>'
        '<p><a href="/accounts/duo_logout">Log out of secondary Duo auth.</a>'
    )


@login_required
def private(request):
    """
    View which requires a login.
    """
    return HttpResponse(
        '<p>Content protected by Django auth.</p>'
        '<p><a href="/duo_private">Continue to secondary auth content.</a></p>'
        '<p><a href="/accounts/logout">Log out of primary Django auth.</a>'
    )


def public(request):
    """
    Public view.
    """
    return HttpResponse('Public content.')


def profile(request):
    """
    View for all Django profiles.
    """
    return HttpResponse('Profile view.')
