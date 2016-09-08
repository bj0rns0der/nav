"""NAV web common package."""

from django.db.models import Count
from django.http import HttpResponse, Http404

from nav.models.profiles import AccountDashboard

DEFAULT_WIDGET_COLUMNS = 2


def get_widget_columns(account):
    """Get the preference for widget columns"""
    return int(account.preferences.get(account.PREFERENCE_KEY_WIDGET_COLUMNS,
                                       DEFAULT_WIDGET_COLUMNS))


def find_dashboard(account, dashboard_id=None):
    """Find a dashboard for this account

    Either find a specific one or the default one. If none of those exist we
    find the one with the most widgets.
    """
    kwargs = {'pk': dashboard_id} if dashboard_id else {'is_default': True}
    try:
        dashboard = AccountDashboard.objects.get(account=account, **kwargs)
    except AccountDashboard.DoesNotExist:
        if dashboard_id:
            raise Http404
        # No default dashboard? Find the one with the most widgets
        dashboard = AccountDashboard.objects.filter(account=account).annotate(
                Count('widgets')).order_by('-widgets__count')[0]

    return dashboard
