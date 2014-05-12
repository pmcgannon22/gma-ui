from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from gm_analytics import views

urlpatterns = patterns('',
                       url(r'^$', views.home, name='home'),
                       url(r'^login$', views.login, name='login'),
                       url(r'^logout$', views.logout, name='logout'),
                       url(r'^groups$', views.groups, name='groups'),
                       url(r'^group/(?P<id>\d+)$', views.group, name='group'),
                       url(r'^group/(?P<id>\d+)/graph$', views.get_graph_json, name='graph_csv'),
                       url(r'^network$', views.network),
)
