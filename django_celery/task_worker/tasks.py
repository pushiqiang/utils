
from django.apps import apps
from haystack import connections
from celery import Task

from notice.models import UserNotice
from follow.models import UserFollower

from task_worker.app import app


class PostNoticeFollowerTask(Task):
    name = "post.notcie.follower"

    def run(self, sender_id, sender_name, object_id, content, **kwargs):
        """
        发送post创建事件给followers
        """
        follower_records = UserFollower.objects.get_followers(user_id=sender_id)
        notices = [UserNotice(receiver=record.follower, sender_id=sender_id,
                       sender_name=sender_name, notice_type=UserNotice.POST_N,
                       content=content, object_id=object_id)
                   for record in follower_records]

        if notices:
            UserNotice.objects.bulk_create(notices)

        return True


class CommentNoticeOwnerTask(Task):
    name = "post.comment.notcie.owner"

    def run(self, sender_id, sender_name, receiver_id, object_id, content, **kwargs):
        """
        发送评论事件给post owner
        """
        UserNotice.objects.create(
            receiver=receiver_id,
            sender=sender_id,
            sender_name=sender_name,
            notice_type=UserNotice.COMMENT_N,
            content=content, object_id=object_id)

        return True


class EsIndexUpdateTask(Task):
    name = "es.index.update"

    def run(self, app_name, model_name, pk, **kwargs):
        try:
            model_class = apps.get_model(app_name, model_name)
            instance = model_class.objects.get(pk=pk)
            search_index = connections['default'].get_unified_index().get_index(model_class)
            search_index.update_object(instance)
        except Exception as exc:
            self.retry([app_name, model_name, pk], kwargs, exc=exc)


class EsIndexDeleteTask(Task):
    name = "es.index.delete"
 
    def run(self, app_name, model_name, pk, **kwargs):
        try:
            model_class = apps.get_model(app_name, model_name)
            instance = model_class.objects.get(pk=pk)
            search_index = connections['default'].get_unified_index().get_index(model_class)
            search_index.remove_object(instance)
        except Exception as exc:
            self.retry([app_name, model_name, pk], kwargs, exc=exc)


# http://docs.celeryproject.org/en/latest/whatsnew-4.0.html#the-task-base-class-no-longer-automatically-register-tasks
PostNoticeFollowerTask = app.register_task(PostNoticeFollowerTask())
CommentNoticeOwnerTask = app.register_task(CommentNoticeOwnerTask())
EsIndexUpdateTask = app.register_task(EsIndexUpdateTask())
EsIndexDeleteTask = app.register_task(EsIndexDeleteTask())
