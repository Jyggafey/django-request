# -*- coding: utf-8 -*-
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import six, timezone
from request.models import Request

DURATION_OPTIONS = {
    'hours': lambda amount: timezone.now() - timedelta(hours=amount),
    'days': lambda amount: timezone.now() - timedelta(days=amount),
    'weeks': lambda amount: timezone.now() - timedelta(weeks=amount),
    'months': lambda amount: timezone.now() + relativedelta(months=-amount),
    'years': lambda amount: timezone.now() + relativedelta(years=-amount),
}

input = raw_input if six.PY2 else input  # @ReservedAssignment


class Command(BaseCommand):
    help = "Purge old requests."

    def add_arguments(self, parser):
        parser.add_argument(
            'amount',
            type=int,
        )
        parser.add_argument('duration')
        parser.add_argument(
            '--noinput',
            action='store_false',
            dest='interactive',
            default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'
        )

    def handle(self, *args, **options):
        amount = options['amount']
        duration = options['duration']

        # Check we have the correct values
        if duration[-1] != 's':  # If its not plural, make it plural
            duration_plural = '{0}s'.format(duration)
        else:
            duration_plural = duration

        if duration_plural not in DURATION_OPTIONS:
            raise CommandError('Amount must be {0}'.format(', '.join(DURATION_OPTIONS)))

        qs = Request.objects.filter(time__lte=DURATION_OPTIONS[duration_plural](amount))
        count = qs.count()

        if count == 0:
            self.stdout.write('There are no requests to delete.')
            return

        if options.get('interactive'):
            confirm = input("""
You have requested a database reset.
This will IRREVERSIBLY DESTROY any
requests created before %d %s ago.
That is a total of %d requests.
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: """ % (amount, duration, count))
        else:
            confirm = 'yes'

        if confirm == 'yes':
            qs.delete()
        else:
            self.stdout.write('Purge cancelled')
