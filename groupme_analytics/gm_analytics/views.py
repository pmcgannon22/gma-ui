# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.core.cache import cache
from libs.groupme_tools.groupme_fetch import get_user_access, get_groups, messages, get_group
from utils import analysis
from models import Group, Message, GroupAnalysis
from forms import LoginForm, MessageForm

import networkx as nx
from networkx.readwrite import json_graph

from datetime import datetime, timedelta
from operator import itemgetter
import json
import string
import random
from collections import Counter, OrderedDict


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
    c['group_info'] = group_info
    c['member_map'] = {member[u'user_id']: member[u'nickname'] for member in group_info[u'members']}
    request.session['member_map'] = c['member_map']

    if cache.get('group-%s' % id):
        c['group'] = cache.get('group-%s' % id)
        return render(request, 'group.html', c)
    if request.GET.get('ajaxLoad', '0') == '0':
        return render(request, 'group-loader.html', c)
    try:
        group = Group.objects.get(id=id)
        msgs = list(Message.objects.filter(group=group))
        group.analysis = analysis(request, msgs, group_info)
    except Group.DoesNotExist:
        get_attachment = lambda x: x[0].get('url', None) if len(x) else None
        msgs = [Message(
                created=datetime.fromtimestamp(float(msg[u'created_at'])),
                author=msg[u'user_id'] if msg[u'user_id'] != 'system' else 0,
                text=msg[u'text'],
                img=get_attachment(msg[u'attachments']),
                likes=msg[u'favorited_by'],
                n_likes=len(msg[u'favorited_by'])
                ) for msg in messages(request.session['token'], id)]
        group = Group(id=id, analysis=analysis(request, msgs, group_info))
        def save_msg(m):
            m.group = group
            m.save()
        map(lambda m: save_msg(m), msgs)
    cache.set('group-%s' % id, group, 180)
    group.save()
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
        c['messages'] = Message.objects.filter(group=id).filter(
                            created__lte=d['end_date']).filter(
                            created__gte=d['start_date']).filter(
                            n_likes__gte=d['min_likes']).filter(
                            n_likes__lte=d['max_likes']).filter(
                            author__in=d['sent_by'])
        if d['img']:
            c['messages'] = c['messages'].exclude(img__isnull=True)
        if d['random']:
            c['messages'] = list(c['messages'])
            random.shuffle(c['messages'])
            c['messages'] = c['messages'][:int(d['limit'])]
        else:
            c['messages'] = c['messages'].order_by('-n_likes', '-created')[:int(d['limit'])]
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
def get_conversation(request, id):
    group_info = get_group(request.session['token'], id)
    member_map = {member[u'user_id']: member[u'nickname'] for member in group_info[u'members']}
    avatar_map = {member[u'user_id']: member[u'image_url'] for member in group_info[u'members']}
    day = request.GET.get('day', datetime.today().strftime("%m/%d/%Y"))
    d = datetime.strptime(day, "%m/%d/%Y") + timedelta(hours=-2)
    d2 = d + timedelta(hours=28)
    messages = Message.objects.filter(group=id).filter(created__lt=d2).filter(created__gt=d).order_by('created')
    return render(request, 'conversation.html',
        {'day1':d, 'day2':d2, 'msgs':messages, 'member_map':member_map, 'self_id':request.session[u'user_id'], 'avatar_map':avatar_map})

@groupme_login_required
def get_personal_data(request, id):
    if request.GET.get('uid', False):
        u = request.GET['uid']
        days = int(request.GET.get('limit',50))
        d = datetime.now() + timedelta(days=-days)
        msgs = Message.objects.filter(group=id).filter(author=int(u)).filter(created__gt=d)

        daily_msgs = Counter([m.created.strftime('%Y-%m-%d') for m in msgs])
        daily_msgs = [{'date': m[0], 'total': m[1]} for m in sorted(daily_msgs.items(), key=itemgetter(0))]

        daily_likes = OrderedDict()
        for m in msgs:
            d = m.created.strftime('%Y-%m-%d')
            daily_likes[d] = daily_likes.get(d, 0) + m.n_likes
        daily_likes = [{'date':k, 'total':v} for k,v in daily_likes.iteritems()]
        return HttpResponse(json.dumps({'likes': daily_likes, 'messages': daily_msgs}), content_type='text/json')

@groupme_login_required
def get_daily_data(request, id):
    limit = request.GET.get('limit', 30)
    sort_by = request.GET.get('sort', None)
    msgs = Message.objects.filter(group=id)
    daily_likes = {}
    for m in msgs:
        d = m.created.strftime('%Y-%m-%d')
        daily_likes[d] = daily_likes.get(d, 0) + m.n_likes
    daily_likes = Counter(daily_likes)
    daily_msgs = Counter([m.created.strftime('%Y-%m-%d') for m in msgs])
    likes_sorted = daily_likes.most_common(int(limit))
    print likes_sorted[0]
    msgs_sorted = daily_msgs.most_common(int(limit))
    data = [{'date': m[0], 'Messages': m[1]} for m in msgs_sorted]
    for m in data:
        m['Likes'] = daily_likes[m['date']]
    data.extend([{'date':m[0], 'Messages': daily_msgs[m[0]], 'Likes': m[1]} for m in likes_sorted])
    return HttpResponse(json.dumps(data), content_type="text/json")
