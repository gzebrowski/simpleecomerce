from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser, UserManager


class ProfileUserManager(UserManager):
    @classmethod
    def normalize_email(cls, email):
        return email.lower()

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not email and username:
            email = username
        email = self.__class__.normalize_email(email)
        username = email
        return super(ProfileUserManager, self).create_user(username, email=email, password=password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return super(ProfileUserManager, self).create_superuser(email, email=email, password=password, **extra_fields)


class UserProfile(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = ProfileUserManager()

UserProfile._meta.get_field('email')._unique = True
UserProfile._meta.get_field('username')._unique = False
