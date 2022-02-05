import pprint
from django.core.management.base import BaseCommand
from Core.libs.pictures import sync_pictures


class Command(BaseCommand):
    help = "Synchronizes the picture objects in the database and the picture and thumbnail files on disk."

    def handle(self, *args, **options):
        # TODO: Check if PICTURES_SUBDIR and THUMBNAILS_SUBDIR are accessible (writable)
        stats = sync_pictures(hot_run=False, verbosity=options['verbosity'])

        # pp = pprint.PrettyPrinter(indent=4, sort_dicts=False)
        # pp.pprint(stats)

        print("")
        print(f"Pictures    pictures/*")
        print(f"{stats['pic_objects_without_pic_file']:6}")
        print(f"{stats['pic_objects_with_pic_file']:6}     {stats['pic_files_with_pic_object']:6}")
        print(f"           {stats['pic_files_without_pic_object']:6}")
        print("")
        print(f"pictures/*  thumbs/*")
        print(f"{stats['pic_files_without_thumb_file']:6}")
        print(f"{stats['pic_files_with_thumb_file']:6}     {stats['thumb_files_with_pic_file']:6}")
        print(f"           {stats['thumb_files_without_pic_file']:6}")
