from django.conf.urls import patterns, url

from .views import HistoryListView
from .views import HistoryDetailView
from .views import HistoryCreateView
from .views import HistoryUpdateView
from .views import HistoryDeleteView
from .views import MangaListView
from .views import MangaDetailView
from .views import MangaCreateView
from .views import MangaUpdateView
from .views import MangaDeleteView
from .views import SubscriptionListView
from .views import SubscriptionDetailView
from .views import SubscriptionCreateView
from .views import SubscriptionUpdateView
from .views import SubscriptionDeleteView


urlpatterns = [
    # Manga
    url(r'^manga/$', MangaListView.as_view(),
        name='manga-list'),
    url(r'^manga/(?P<pk>\d+)$', MangaDetailView.as_view(),
        name='manga-read'),
    url(r'^manga/new/$', MangaCreateView.as_view(),
        name='manga-create'),
    url(r'^manga/edit/(?P<pk>\d+)$', MangaUpdateView.as_view(),
        name='manga-update'),
    url(r'^manga/delete/(?P<pk>\d+)$', MangaDeleteView.as_view(),
        name='manga-delete'),

    # Subscription
    url(r'^subscription/$', SubscriptionListView.as_view(),
        name='subscription-list'),
    url(r'^subscription/(?P<pk>\d+)$', SubscriptionDetailView.as_view(),
        name='subscription-read'),
    url(r'^subscription/new/$', SubscriptionCreateView.as_view(),
        name='subscription-create'),
    url(r'^subscription/edit/(?P<pk>\d+)$', SubscriptionUpdateView.as_view(),
        name='subscription-update'),
    url(r'^subscription/delete/(?P<pk>\d+)$', SubscriptionDeleteView.as_view(),
        name='subscription-delete'),

    # History
    url(r'^history/$', HistoryListView.as_view(), name='history-list'),
    url(r'^history/(?P<pk>\d+)$', HistoryDetailView.as_view(),
        name='history-read'),
    url(r'^history/new/$', HistoryCreateView.as_view(), name='history-create'),
    url(r'^history/edit/(?P<pk>\d+)$', HistoryUpdateView.as_view(),
        name='history-update'),
    url(r'^history/delete/(?P<pk>\d+)$', HistoryDeleteView.as_view(),
        name='history-delete'),
    ]

urlpatterns = patterns('', *urlpatterns)
