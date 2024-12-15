from django.contrib import admin
from django import forms
from .models import *

admin.site.register(Board)
admin.site.register(List)
admin.site.register(Task)
admin.site.register(TaskComment)
admin.site.register(TaskCommentLike)

