# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.core.cache import cache
from django.conf import settings
from django.db.models import Count
from libs.groupme_tools.groupme_fetch import get_user_access, get_groups, msg_concurrent, get_group, messages
from utils import analysis
from models import Group, Message, GroupAnalysis
from forms import LoginForm, MessageForm

import networkx as nx
from networkx.readwrite import json_graph

from datetime import datetime, timedelta, date
from operator import itemgetter
from itertools import chain
import json
import string
import re
import pdb
import random
from collections import Counter, OrderedDict


import logging

logger = logging.getLogger(__name__)

def network(request):
    id = "1732457"
    '''
    start = datetime(2012, 8, 1)
    end = datetime(2012, 8, 8)
    week = timedelta(days=7)
    points = {}
    while start < datetime.today():
        msgs = Message.objects.filter(group=id).filter(created__gt=start).filter(created__lt=end)
        count = len(msgs)
        likes = sum([int(m.n_likes) for m in msgs])
        if count > 0:
            avg = float(likes)/count
        else:
            avg = 0
        print avg

        for m in msgs:
            if m.author in points:
                points[m.author] += m.n_likes - avg
            else:
                points[m.author] = m.n_likes - avg
        start = start + week
        end = end + week
    spoints = sorted(points.items(), key=itemgetter(1))
    for name, score in spoints:
        print "%s: %f" % (name, score)
    points = {}
    val = 1
    last = msgs[0].n_likes
    for msg in msgs:
        if msg.n_likes != last:
            last = msg.n_likes
            val += 1
        if points.get(msg.author, False):
            points[msg.author] += val
        else:
            points[msg.author] = val

    sorted_points = sorted(points.items(), key=itemgetter(1))
    total = 0
    for author, pts in sorted_points:
        print "%s: %d" % (author, pts)
        total += pts
    '''

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

    if cache.get('group-%s' % id) and settings.CACHE_ENABLED:
        c['group'] = cache.get('group-%s' % id)
        return render(request, 'group.html', c)
    if request.GET.get('ajaxLoad', '0') == '0' and settings.CACHE_ENABLED:
        return render(request, 'group-loader.html', c)
    get_attachment = lambda x: x[0].get('url', None) if len(x) else None
    try:
        group = Group.objects.get(id=id)
        msgs = list(Message.objects.filter(group=group).order_by('created'))
        if msgs:
            after_id = msgs[-1].id
            if not str(after_id).isdigit():
                after_id = 0
            elif str(after_id) != str(group_info[u'messages'][u'last_message_id']):
                msgs += [Message(
                        id=msg[u'id'],
                        created=datetime.fromtimestamp(float(msg[u'created_at'])),
                        author=msg[u'user_id'] if msg[u'user_id'] != 'system' else 0,
                        text=msg[u'text'],
                        img=get_attachment(msg[u'attachments']),
                        likes=msg[u'favorited_by'],
                        n_likes=len(msg[u'favorited_by'])
                        ) for msg in msg_concurrent(request.session['token'], id, after_id=after_id, n_workers=(int(group_info[u'messages'][u'count'])/10 + 1))]
        group.analysis = analysis(request, msgs, group_info)

    except Group.DoesNotExist:
        msgs = [Message(
                id=msg[u'id'],
                created=datetime.fromtimestamp(float(msg[u'created_at'])),
                author=msg[u'user_id'] if msg[u'user_id'] != 'system' else 0,
                text=msg[u'text'],
                img=get_attachment(msg[u'attachments']),
                likes=msg[u'favorited_by'],
                n_likes=len(msg[u'favorited_by'])
                ) for msg in msg_concurrent(request.session['token'], id, n_workers=(int(group_info[u'messages'][u'count'])/10 + 1))]

        group = Group(id=id, analysis=analysis(request, msgs, group_info))
        def save_msg(m):
            m.group = group
            m.save()
        map(lambda m: save_msg(m), msgs)
    if settings.CACHE_ENABLED:
        cache.set('group-%s' % id, group, 180)
    group.save()
    c['group'] = group
    return render(request, 'group.html', c)

@groupme_login_required
def msq_query(request, id):
    c = {}
    group_info = get_group(request.session['token'], id)
    c['member_map'] = {member[u'user_id']: member[u'nickname'] for member in group_info[u'members']}
    form = MessageForm(request.GET, created=group_info['created_at'], members=c['member_map'])
    if form.is_valid():
        d = form.cleaned_data

        c['messages'] = Message.objects.filter(group=id, created__lte=d['end_date'],
                            created__gte=d['start_date'],
                            n_likes__gte=d['min_likes'],
                            n_likes__lte=d['max_likes'],
                            author__in=d['sent_by'],
                            text__icontains=d['text_contains'])
        if d['text_not_contain']:
            c['messages'] = c['messages'].exclude(text__icontains=d['text_not_contain'])
        if d['img']:
            c['messages'] = c['messages'].exclude(img__isnull=True)
        if d['random']:
            c['messages'] = list(c['messages'])
            random.shuffle(c['messages'])
            c['messages'] = c['messages'][:int(d['limit'])]
        else:
            sort = '-' + d['sort_by'] if d['sort_order'] else d['sort_by']
            sort = (sort, '-created') if d['sort_by'] == 'n_likes' else (sort, '-n_likes')
            c['messages'] = c['messages'].order_by(sort[0], sort[1])[:int(d['limit'])]
        return render(request, 'message_table.html', c)
    else:
        return HttpResponse("");

@groupme_login_required
def group_messages(request, id):
    c = {}
    group_info = get_group(request.session['token'], id)
    c['member_map'] = {member[u'user_id']: member[u'nickname'] for member in group_info[u'members']}
    c['group_info'] = group_info
    c['form'] = MessageForm(created=group_info['created_at'], members=c['member_map'])
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
    graph = json.loads(analysis.like_network)
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
def get_names_history(request, id):
    group_info = get_group(request.session['token'], id)
    sys_msgs = Message.objects.filter(group=id).filter(author='0').order_by('created')
    changes = filter(lambda m: "group's name" in m.text, sys_msgs)
    m = re.compile("name to (.+)")
    last = datetime.fromtimestamp(group_info['created_at']).strftime("%Y-%m-%d")
    data = []
    for i, msg in enumerate(changes):
        if i+1 < len(changes):
            end = changes[i+1].created.strftime("%Y-%m-%d")
        else:
            end = datetime.today().strftime("%Y-%m-%d")
        data.append({
            'name': m.search(msg.text).groups()[0],
            'begin': msg.created.strftime("%Y-%m-%d"),
            'end': end
        })

    if len(changes) == 0:
        data = [{
            'name': group_info['name'],
            'begin': date.fromtimestamp(float(group_info['created_at'])).strftime("%Y-%m-%d"),
            'end': date.today().strftime("%Y-%m-%d")
        }]
    return HttpResponse(json.dumps(data), content_type="text/json")

def get_users(request, id):
    group_info = get_group(request.session['token'], id)
    users = []
    member_map = {member[u'user_id']: member[u'nickname'] for member in group_info[u'members']}
    group = Group.objects.get(id=id)
    for member in group_info[u'members']:
        uid = member['user_id']
        try: 
            most_liked = Message.objects.filter(group=id, author=uid).order_by('-n_likes')[0]
        except IndexError:
            most_liked = None
        likers = Message.objects.filter(group=id, author=uid, n_likes__gt=0).values('likes')

        high_likers = Counter(list(chain(*[msg['likes'] for msg in likers]))).most_common(3)

        users.append({
            'user_id': uid,
            'nickname': member['nickname'],
            'image_url': member['image_url'],
            'msgs_per': group.analysis.msgs_per[uid],
            'msg_perc': group.analysis.msg_perc[uid],
            'likes_rec': group.analysis.likes_rec[uid],
            'likes_give': group.analysis.likes_give[uid],
            'ratio': group.analysis.ratio[uid],
            'prank': group.analysis.prank[uid],
            'most_liked': {
                'text': most_liked.text,
                'created': most_liked.created.strftime("%I:%M, %m/%d/%Y"),
                'n_likes': most_liked.n_likes
            } if most_liked else None,
            'highest_likers': [(member_map[unicode(n[0])], n[1]) for n in high_likers]
        })

    return HttpResponse(json.dumps(users), content_type="text/json")

@groupme_login_required
def get_personal_data(request, id):
    if request.GET.get('uid', False):
        u = request.GET['uid']
        days = int(request.GET.get('limit',50))
        d = datetime.now() + timedelta(days=-days)
        msgs = Message.objects.filter(group=id).filter(author=int(u)).filter(created__gt=d)

        daily_likes = {d.strftime("%Y-%m-%d"): 0 for d in (datetime.now() + timedelta(days=-n) for n in range(days+1))} #zeros
        for m in msgs:
            if m.n_likes > 0:
                d = m.created.strftime('%Y-%m-%d')
                daily_likes[d] += m.n_likes
        daily_likes = OrderedDict(sorted(daily_likes.items()))
        daily_likes = [{'date':k, 'total':v} for k,v in daily_likes.iteritems()]

        daily_msgs = Counter([m.created.strftime('%Y-%m-%d') for m in msgs])
        daily_msgs = [{'date': d.strftime("%Y-%m-%d"), 'total': daily_msgs.get(d.strftime("%Y-%m-%d"), 0)} for d in (datetime.now() + timedelta(days=-n) for n in range(days))]
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
    msgs_sorted = daily_msgs.most_common(int(limit))
    data = [{'date': m[0], 'Messages': m[1]} for m in msgs_sorted]
    for m in data:
        m['Likes'] = daily_likes[m['date']]
    data.extend([{'date':m[0], 'Messages': daily_msgs[m[0]], 'Likes': m[1]} for m in likes_sorted])
    return HttpResponse(json.dumps(data), content_type="text/json")
