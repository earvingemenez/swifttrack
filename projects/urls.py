from django.conf.urls import url
from .views import ProjectView, WorkDiaryView
from . import views

urlpatterns = [
    url(r'^$', ProjectView.as_view(), name='project'),
    url(r'^work_diary/(?P<id>[0-9]+)/$', WorkDiaryView.as_view(), name='work-diary'),
]