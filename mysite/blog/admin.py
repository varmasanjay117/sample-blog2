from django.contrib import admin
from .models import Post,Profile,Comment
class PostAdmin(admin.ModelAdmin):
    list_display =('title','slug','author','status')
    list_filter=('status','created','update')
    search_fields=('author__username','title')
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ('status',)
    date_hierarchy = 'created'
# Register your models here.

admin.site.register(Post,PostAdmin)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'dob', 'photo')


admin.site.register(Comment)
admin.site.register(Profile, ProfileAdmin)
