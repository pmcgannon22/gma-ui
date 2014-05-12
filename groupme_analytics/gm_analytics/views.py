# Create your views here.
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from libs.groupme_tools.groupme_fetch import get_access_token, get_groups, messages, get_group
from models import Group, Message, GroupAnalysis

from datetime import datetime
import operator
import csv
import json

import networkx as nx
from networkx.readwrite import json_graph

import logging

logger = logging.getLogger(__name__)

def network(request):
    return render_to_response("network.html", {}, RequestContext(request))

def groupme_login_required(function):
    def wrapper(request, *args, **kw):
        if not request.session.get('token'):
            return redirect('/')
        else:
            return function(request, *args, **kw)
    return wrapper



class LoginForm(forms.Form):
    username = forms.CharField()
    username.widget = forms.TextInput(attrs={
            'placeholder':'Username/Phone Number',
            'required':'',
            'autofocus':'',
            'class':'form-control',
            })
    password = forms.CharField()
    password.widget = forms.PasswordInput(attrs={
            'class':'form-control',
            'placeholder':'Password',
            'required':''
            })

def home(request):
    if request.session.get('token'):
        return redirect('/groups')
    form = LoginForm()
    return render_to_response('login.html', {'form':form},RequestContext(request))

def login(request):
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            access_token = get_access_token(cd['username'],cd['password'])
            request.session['token'] = access_token
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
    try:
        group = Group.objects.get(id=id)
    except Group.DoesNotExist:
        msgs = [Message(
                created=datetime.fromtimestamp(float(msg[u'created_at'])),
                author=msg[u'sender_id'],
                text=msg[u'text'],
                img=None,
                likes=msg[u'favorited_by']
                ) for msg in messages(request.session['token'], id)]
        group = Group(id=id, messages=msgs, analysis=analysis(msgs, group_info))
        group.save()
    c['group_info'] = group_info
    c['group'] = group
    c['member_map'] = {member[u'user_id']: member[u'nickname'] for member in group_info[u'members']}
    logger.debug(c['member_map'])
    return render(request, 'group.html', c)


def analysis(msgs, group_info):
    members = group_info[u'members']
    member_map = {member[u'user_id'] : member[u'nickname'] for member in members}
    total_messages = {member[u'user_id']: 0 for member in members}
    likes_given = {member[u'user_id']: 0 for member in members}
    likes_rec = {member[u'user_id']: 0 for member in members}
    like_graph = nx.DiGraph()
    like_graph.add_nodes_from(member_map.keys())
    for msg in msgs:
        if msg.author in total_messages:
            total_messages[msg.author] += 1
        if msg.author in likes_rec:
            likes_rec[msg.author] += len(msg.likes)
        for like in msg.likes:
            if like in member_map and msg.author in member_map:
                if like_graph.has_edge(like, msg.author):
                    like_graph[like][msg.author]['weight'] += 1
                else:
                    like_graph.add_edge(like, msg.author, {'weight':1})
            if like in likes_given:
                likes_given[like] += 1
    like_ratio = {}
    msg_percentage = {}
    total_group_msgs = float(group_info[u'messages'][u'count'])
    for member in members:
        m = member[u'user_id']
        msg_percentage[m] = float(total_messages[m])/total_group_msgs
        try:
            like_ratio[m] = float(likes_rec[m])/float(likes_given[m])
        except:
            like_ratio[m] = 0.0
    pers = {member[u'user_id']: (1-msg_percentage[member[u'user_id']]) for member in members}
    avg = sum(pers.values())/len(pers)
    pers = {n: (pers[n] if n in pers else avg) for n in like_graph.nodes_iter()}
    logger.debug(pers)
    pagerank = nx.pagerank(like_graph, alpha=.95, personalization=pers)
    return GroupAnalysis(msgs_per=total_messages, likes_rec=likes_rec, likes_give=likes_given,
                    prank=pagerank,
                    msg_perc=msg_percentage, ratio=like_ratio, like_network=json_graph.dumps(like_graph))

def get_graph_json(request, id):
    group_info = get_group(request.session['token'], id)
    member_map = {member[u'user_id'] : (member[u'nickname'], member[u'image_url']) for member in group_info[u'members']}
    analysis = Group.objects.get(id=id).analysis
    graph = json.loads(analysis.like_network)
    graph[u'nodes'] = [{u'id':n[u'id'], u'name':member_map[n[u'id']][0], u'img':member_map[n[u'id']][1]} 
                                for n in graph[u'nodes']]
    #for edge in graph[u'links']:
    #    n_graph.append({'source':graph[u'nodes'][edge[u'source']][u'id'],
    #                    'target':graph[u'nodes'][edge[u'target']][u'id'],
    #                    'weight':edge[u'weight']})
    return HttpResponse(json.dumps(graph), content_type='application/csv')
