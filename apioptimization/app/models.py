from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class AppComment(models.Model):
    id = models.BigAutoField(primary_key=True)
    text = models.TextField()
    created_at = models.DateTimeField()
    author = models.ForeignKey('AppUser', models.DO_NOTHING)
    post = models.ForeignKey('AppPost', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'app_comment'


class AppPost(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    author = models.ForeignKey('AppUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'app_post'


class AppUserGroups(models.Model):
    user = models.ForeignKey('AppUser', models.DO_NOTHING, db_column='user_id')
    group = models.ForeignKey(Group, models.DO_NOTHING, db_column='group_id')

    class Meta:
        managed = False
        db_table = 'app_user_groups'


class AppUserUserPermissions(models.Model):
    user = models.ForeignKey('AppUser', models.DO_NOTHING, db_column='user_id')
    permission = models.ForeignKey(Permission, models.DO_NOTHING, db_column='permission_id')

    class Meta:
        managed = False
        db_table = 'app_user_user_permissions'


class AppUser(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        through=AppUserGroups,
        blank=True,
        related_name='app_user_set',
        related_query_name='app_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        through=AppUserUserPermissions,
        blank=True,
        related_name='app_user_set',
        related_query_name='app_user',
    )

    class Meta:
        managed = False
        db_table = 'app_user'