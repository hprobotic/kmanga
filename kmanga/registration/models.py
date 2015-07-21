from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class UserProfile(models.Model):
    FREE = 'F'
    PAY = 'P'
    MODE_CHOICES = (
        (FREE, 'Non-pay user'),
        (PAY, 'Pay user'),
    )
    GERMAN = 'DE'
    ENGLISH = 'EN'
    SPANISH = 'ES'
    FRENCH = 'FR'
    ITALIAN = 'IT'
    RUSSIAN = 'RU'
    LANGUAGE_CHOICES = (
        (ENGLISH, 'English'),
        (SPANISH, 'Spanish'),
        (GERMAN, 'German'),
        (FRENCH, 'French'),
        (ITALIAN, 'Italian'),
        (RUSSIAN, 'Russian'),
    )
    ISSUES_PER_DAY = {
        FREE: 10,
        PAY: 50,
    }

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                primary_key=True)
    mode = models.CharField(max_length=1, choices=MODE_CHOICES,
                            default=FREE)
    language = models.CharField(max_length=2,
                                choices=LANGUAGE_CHOICES)
    issues_per_day = models.IntegerField(default=ISSUES_PER_DAY[FREE])
    email_kindle = models.EmailField()

    def __str__(self):
        return self.user.username
