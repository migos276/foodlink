from django.contrib.auth.management.commands.createsuperuser import Command as BaseCreateSuperUserCommand
from django.core.management import CommandError

class Command(BaseCreateSuperUserCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--tel', dest='tel', default=None, help='Telephone number for the superuser')

    def handle(self, *args, **options):
        tel = options.get('tel')

        # If tel is not provided, prompt the user interactively
        if tel is None:
            tel = input('Telephone number (tel): ')
            if not tel:
                raise CommandError('Error: Telephone number (tel) is required.')

        options['tel'] = tel
        super().handle(*args, **options)

    def create_superuser(self, *args, **options):
        # This method is deprecated here but ensures tel is passed with create_superuser
        # The actual create_superuser call will be handled by the CustomUserManager
        return super().create_superuser(*args, **options)
