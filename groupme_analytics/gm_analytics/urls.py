from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from gm_analytics import views


urlpatterns = patterns('',
                       url(r'^$', views.home, name='home'),
                       url(r'^login$', views.login, name='login'),
                       url(r'^logout$', views.logout, name='logout'),
                       url(r'^groups$', views.groups, name='groups'),
                       url(r'^group/(?P<id>\d+)$', views.group, name='group'),
                       url(r'^group/(?P<id>\d+)/messages$', views.group_messages, name='group_messages'),
                       url(r'^group/(?P<id>\d+)/messages/query$', views.msq_query, name='msg_query'),
                       url(r'^group/(?P<id>\d+)/graph$', views.get_graph_json, name='graph_json'),
                       url(r'^group/(?P<id>\d+)/percentages$', views.get_percentage_json, name='percentage_json'),
                       url(r'^group/(?P<id>\d+)/messages/conversation$', views.get_conversation, name='msgs_text'),
                       url(r'^group/(?P<id>\d+)/dailydata$', views.get_daily_data, name="daily_data"),
                       url(r'^group/(?P<id>\d+)/user$', views.get_personal_data, name="personal_data"),
                       url(r'^group/(?P<id>\d+)/users$', views.get_users, name="group_users"),
                       url(r'^group/(?P<id>\d+)/names$', views.get_names_history, name="names_history"),
                       url(r'^network$', views.network),
)
