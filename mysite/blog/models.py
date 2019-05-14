
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models.signals import post_save



class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status="published")

# class ChoiceManager(models.Manager):
#     def get_queryset(self):
#         return super(ChoiceManager, self).get_queryset().filter(status="social")



# Create your models here.
class Post(models.Model):
    objects = models.Manager()      #Our default Manager
    published = PublishedManager()  #Our Custom Model Manager
    # Social  =   ChoiceManager()

    STATUS_CHOICE=(
    ('draft','Draft'),
    ('published','Published')
    )
    EXTRA_CHOICE=(
    ('social','Social'),
    ('science','science'),
    )
    title   =   models.CharField(max_length=100)
    slug    =   models.SlugField(max_length=120)
    author  =   models.ForeignKey(User,related_name='blog_posts',on_delete=models.CASCADE)
    body    =   models.TextField()
    created =   models.DateTimeField(auto_now_add=True)
    update  =   models.DateTimeField(auto_now=True)
    status  =   models.CharField(max_length=10,choices=STATUS_CHOICE)
    restrict_comment    =       models.BooleanField(default=False)
    favourite           =       models.ManyToManyField(User, related_name='favourite', blank=True)
    likes               =       models.ManyToManyField(User, related_name='likes', blank=True)
    option              =       models.CharField(max_length=10,choices=EXTRA_CHOICE)


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[self.id, self.slug])

    def total_likes(self):
        return self.likes.count()




@receiver(pre_save, sender=Post)
def pre_save_slug(sender, **kwargs):
    slug = slugify(kwargs['instance'].title)
    kwargs['instance'].slug = slug


class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    dob = models.DateField(null=True, blank=True)
    photo = models.ImageField(null=True, blank=True)


    def __str__(self):
        return "Profile of user {}".format(self.user.username)


def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = Profile.objects.create(user=kwargs['instance'])

post_save.connect(create_profile, sender=User)


class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    reply = models.ForeignKey('Comment', null=True, related_name="replies",on_delete=models.CASCADE)
    content = models.TextField(max_length=160)
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return '{}-{}'.format(self.post.title, str(self.user.username))
