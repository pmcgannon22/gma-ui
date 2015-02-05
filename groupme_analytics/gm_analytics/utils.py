import networkx as nx
from networkx.readwrite import json_graph

from libs.groupme_tools.groupme_fetch import get_user_access, get_groups, messages, get_group

from models import GroupAnalysis
from collections import Counter
from datetime import datetime, timedelta
from django.db.models import Max, Avg, Count

def analysis(request, msgs, group_info):
    members = group_info[u'members']
    member_map = request.session['member_map']

    (total_messages, total_likes, likes_given, likes_rec, like_graph, prank) = basics_count(msgs, [m[u'user_id'] for m in members])

    like_ratio, msg_percentage = {},{}
    total_group_msgs = float(group_info[u'messages'][u'count'])
    for member in members:
        m = member[u'user_id']
        msg_percentage[m] = float(total_messages[m])/total_group_msgs
        try:
            like_ratio[m] = float(likes_rec[m])/float(likes_given[m])
        except:
            like_ratio[m] = 0.0
    #pers = {member[u'user_id']: (1-msg_percentage[member[u'user_id']]) for member in members}
    #avg = sum(pers.values())/len(pers)
    #pers = {n: (pers[n] if n in pers else avg) for n in like_graph.nodes_iter()}
    #pagerank = nx.pagerank(like_graph, alpha=.95, personalization=pers)
    return GroupAnalysis(msgs_per=total_messages, likes_rec=likes_rec, likes_give=likes_given,
                    prank=prank,
                    msg_perc=msg_percentage, ratio=like_ratio, like_network=json_graph.dumps(like_graph))

def basics_count(msgs, members):
    total_messages = {member: 0 for member in members}
    likes_given = {member: 0 for member in members}
    likes_rec = {member: 0 for member in members}
    like_graph = nx.DiGraph()
    like_graph.add_nodes_from(members)
    total_likes = 0

    week = timedelta(days=7)
    week_count = [0]
    week_likes = [0]
    n_week = 0
    end_date = msgs[0].created + week
    for msg in msgs:
        if msg.created > end_date:
            end_date += week
            n_week += 1
            week_count.append(0)
            week_likes.append(0)

        author = unicode(msg.author)
        total_likes += len(msg.likes)
        if author in total_messages:
            total_messages[author] += 1
        if author in likes_rec:
            likes_rec[author] += len(msg.likes)

        week_count[n_week] += 1
        week_likes[n_week] += msg.n_likes

        for like in msg.likes:
            l = unicode(like)
            if l in members and author in members:
                if like_graph.has_edge(l, author):
                    like_graph[l][author]['weight'] += 1
                else:
                    like_graph.add_edge(l, author, {'weight':1})
            if l in likes_given:
                likes_given[l] += 1
    prank = power_rank(msgs, members, week_count, week_likes)

    return (total_messages, total_likes, likes_given, likes_rec, like_graph, prank)

def power_rank(msgs, members, week_count, week_likes):
    week = timedelta(days=7);
    end_date = msgs[0].created + week
    points = {member: 0 for member in members}

    week_avg = []
    for i in range(len(week_count)):
        if week_count[i] != 0:
            week_avg.append(float(week_likes[i])/week_count[i])
        else:
            week_avg.append(0)

    n_week = 0
    for msg in msgs:
        author = unicode(msg.author)
        if msg.created > end_date:
            end_date = end_date + week
            n_week += 1
        if author in points:
            points[author] += msg.n_likes - week_avg[n_week]

    for key, val in points.iteritems():
        print "%s: %f" % (key, val)

    return points
