from django.core.management.base import BaseCommand
from Core.libs.pictures import cleanup_pictures


class Command(BaseCommand):
    help = "Deletes low-value pictures that exceed the allotted disk space."

    def add_arguments(self, parser):
        parser.add_argument("--hot-run", action="store_true", help="Actually delete files!")

    def handle(self, *args, **options):
        out = None  # self.stdout causes excessive newlines
        cleanup_pictures(hot_run=options['hot_run'], out=out)
        print("")
