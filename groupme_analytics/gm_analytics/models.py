from django.db import models

from djangotoolbox.fields import ListField, DictField, EmbeddedModelField, RawField

# Create your models here.
class Group(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    messages = ListField(EmbeddedModelField('Message'))
    analysis = EmbeddedModelField('GroupAnalysis')

    def get_absolute_url(self):
        return "/group/%s" % str(self.id)

    def __unicode__(self):
        return self.id

class Message(models.Model):
    created = models.DateTimeField()
    author = models.PositiveIntegerField()
    text = models.TextField()
    img = models.URLField(null=True)
    likes = ListField(models.IntegerField())

    def __unicode__(self):
        return "%s: %s" % (self.author, self.text)

class GroupAnalysis(models.Model):
    msgs_per = DictField(models.PositiveSmallIntegerField())
    msg_perc = DictField(models.FloatField())
    likes_rec = DictField(models.SmallIntegerField())
    likes_give = DictField(models.SmallIntegerField())
    ratio = DictField(models.FloatField())
    prank = DictField(models.FloatField()) #pagerank
    like_network = RawField() #only works in MongoDB
