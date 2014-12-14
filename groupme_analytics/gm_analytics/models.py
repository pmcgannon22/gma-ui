from django.db import models

from djangotoolbox.fields import ListField, DictField, EmbeddedModelField, RawField
from django_mongodb_engine.contrib import MongoDBManager

# Create your models here.
class Group(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    analysis = EmbeddedModelField('GroupAnalysis')

    objects = MongoDBManager()

    def get_absolute_url(self):
        return "/group/%s" % str(self.id)

    def __unicode__(self):
        return self.id

class Message(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    created = models.DateTimeField()
    group = models.ForeignKey(Group)
    author = models.PositiveIntegerField()
    text = models.TextField(null=True)
    img = models.URLField(null=True)
    likes = ListField(models.IntegerField())
    n_likes = models.SmallIntegerField()

    def __unicode__(self):
        return "[@{}] {}: {} ({})".format(self.created,self.author, self.text, self.n_likes)

class GroupAnalysis(models.Model):
    msgs_per = DictField(models.PositiveSmallIntegerField())
    msg_perc = DictField(models.FloatField())
    likes_rec = DictField(models.SmallIntegerField())
    likes_give = DictField(models.SmallIntegerField())
    ratio = DictField(models.FloatField())
    prank = DictField(models.FloatField()) #pagerank
    like_network = RawField() #only works in MongoDB
