# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from libs.groupme_tools.groupme_fetch import get_user_access, get_groups, messages, get_group
from utils import analysis
from models import Group, Message, GroupAnalysis
from forms import LoginForm, MessageForm

import networkx as nx
from networkx.readwrite import json_graph

from datetime import datetime, timedelta
import operator
import json
import string
from random import choice as random_element
from collections import Counter

import logging

logger = logging.getLogger(__name__)

def network(request):
    return render_to_response("network.html", {}, RequestContext(request))

def groupme_login_required(function):
    def wrapper(request, *args, **kw):
        if not request.session.get('token'):
            return HttpResponseRedirect('/')
        else:
            return function(request, *args, **kw)
    return wrapper

def home(request):
    if request.session.get('token'):
        return HttpResponseRedirect('/groups')
    form = LoginForm()
    return render_to_response('login.html', {'form':form},RequestContext(request))

def login(request):
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            login_info = get_user_access(cd['username'],cd['password'])
            if login_info[u'response']:
                request.session['token'] = login_info[u'response'][u'access_token']
                request.session['user_id'] = login_info[u'response'][u'user_id']
                request.session['user_name'] = login_info[u'response'][u'user_name']
            elif u'meta' in login_info:
                return render(request, 'login.html',
                    {'form':LoginForm(), 'error': login_info[u'meta'][u'errors'][0]})
            else:
                return render(request, 'login.html',
                    {'form':LoginForm(), 'error': "Unknown Error. Try again."})

        else:
            print form.errors
        return HttpResponseRedirect('/groups')
    else:
        form=LoginForm()
        return render_to_response('login.html', {'form':form}, RequestContext(request))

def logout(request):
    request.session.flush()
    return HttpResponseRedirect("/login")

@groupme_login_required
def groups(request):
    user_groups = get_groups(request.session['token'])
    return render(request, 'groups.html', {'groups':user_groups})

@groupme_login_required
def group(request, id):
    c = {}
    group_info = get_group(request.session['token'], id)
    c['member_map'] = {member[u'user_id']: member[u'nickname'] for member in group_info[u'members']}
    request.session['member_map'] = c['member_map']
    try:
        group = Group.objects.get(id=id)
        messages = list(Message.objects.filter(group=group))
        group.analysis = analysis(request, messages, group_info)
        group.save()
    except Group.DoesNotExist:
        msgs = [Message(
                created=datetime.fromtimestamp(float(msg[u'created_at'])),
                author=msg[u'user_id'] if msg[u'user_id'] != 'system' else 0,
                text=msg[u'text'],
                img=None,
                likes=msg[u'favorited_by'],
                n_likes=len(msg[u'favorited_by'])
                ) for msg in messages(request.session['token'], id)]
        group = Group(id=id, analysis=analysis(request, msgs, group_info))
        def save_msg(m):
            m.group = group
            m.save()
        map(lambda m: save_msg(m), msgs)
    group.save()
    c['group_info'] = group_info
    c['group'] = group
    return render(request, 'group.html', c)

@groupme_login_required
def msq_query(request, id):
    c = {}
    group_info = get_group(request.session['token'], id)
    c['member_map'] = {member[u'user_id']: member[u'nickname'] for member in group_info[u'members']}
    form = MessageForm(request.GET, members=c['member_map'])
    if form.is_valid():
        d = form.cleaned_data
        c['messages'] = Message.objects.filter(
                            created__lte=d['end_date']).filter(
                            created__gte=d['start_date']).filter(
                            n_likes__gte=d['min_likes']).filter(
                            n_likes__lte=d['max_likes']).filter(
                            author__in=d['sent_by']).order_by('-n_likes', '-created')[:int(d['limit'])]
        return render(request, 'message_table.html', c)
    else:
        return HttpResponse("");

@groupme_login_required
def group_messages(request, id):
    c = {}
    group_info = get_group(request.session['token'], id)
    c['member_map'] = {member[u'user_id']: member[u'nickname'] for member in group_info[u'members']}
    c['group_info'] = group_info
    c['form'] = MessageForm(members=c['member_map'])
    try:
        c['group'] = Group.objects.get(id=id)
    except Group.DoesNotExist:
        return HttpResponseRedirect('/group/%s' % id)
    return render(request, 'messages.html', c)

@groupme_login_required
def get_graph_json(request, id):
    group_info = get_group(request.session['token'], id)
    member_map = {member[u'user_id']: (member[u'nickname'], member[u'image_url']) for member in group_info[u'members']}
    analysis = Group.objects.get(id=id).analysis
    d = json_graph.loads(analysis.like_network)
    g = nx.Graph()
    g.add_nodes_from(d)
    #convert to undirected
    for u,v,d in d.edges(data=True):
        if g.has_edge(u,v):
            g[u][v]['weight']+=d['weight']
        else:
            g.add_edge(u,v,d)
    graph = json.loads(json_graph.dumps(g))
    graph[u'nodes'] = [{u'id':n[u'id'], u'name':member_map[n[u'id']][0], u'img':member_map[n[u'id']][1]} for n in graph[u'nodes']]
    return HttpResponse(json.dumps(graph), content_type='application/csv')

@groupme_login_required
def get_percentage_json(request, id):
    group_info = get_group(request.session['token'], id)
    member_map = {member[u'user_id']: member[u'nickname'] for member in group_info[u'members']}
    analysis = Group.objects.get(id=id).analysis
    total_likes = float(sum([v for v in analysis.likes_give.itervalues()]))
    likes_rec_percentage = {k: (v/total_likes) for (k,v) in analysis.likes_rec.iteritems()}
    likes_give_percentage = {k: (v/total_likes) for (k,v) in analysis.likes_give.iteritems()}
    js = {"name":"", "children":[]}
    for k,v in member_map.iteritems():
        js["children"].append({"name":v, "messages":"{:3.4f}".format(analysis.msg_perc[k] * 100),
                                "likes_rec": "{:3.4f}".format(likes_rec_percentage[k] * 100),
                                "likes_given":"{:3.4f}".format(likes_give_percentage[k] * 100)})
    return HttpResponse(json.dumps(js), content_type="application/csv")

@groupme_login_required
def get_msgs(request, id, count):
    d = datetime.now() + timedelta(-30)
    messages = (Group.objects.get(id=id).messages)[:100]
    words = " ".join([m.text.strip(string.punctuation) for m in messages if m.text]).split()
    print Counter(words)
    return HttpResponse(" ".join([m.text.strip(string.punctuation) for m in messages if m.text]), content_type="text/plain")

@groupme_login_required
def get_daily_data(request, id):
    limit = request.GET.get('limit', None)
    msgs = Message.objects.filter(group=id)
    daily_msgs = Counter([m.created.strftime('%Y-%m-%d') for m in msgs])
    daily_msgs = daily_msgs.most_common(int(limit)) if limit else daily_msgs
    return HttpResponse(json.dumps(dict(daily_msgs)), content_type="text/json")
