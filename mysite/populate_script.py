import os,random,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')
django.setup()

from faker import Faker
from blog.models import Post
from django.contrib.auth.models import User
from django.utils import timezone


def create_faker(N):
    fake=Faker()
    for _ in range(N):
        id      =   random.choice([1,2,3,4,5])
        title   =   fake.name()
        slug    =   '-'.join(title.lower().split())
        body    =   fake.text()
        created =   timezone.now()
        status  =   random.choice(['published','draft'])
        Post.objects.create(title=title,slug=slug,
                                author=User.objects.get(id=id),body=body,
                                created=created,status=status)

create_faker(100)
print('done faker')
