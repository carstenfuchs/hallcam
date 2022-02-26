from django.core.management.base import BaseCommand
from Core.libs.pictures import sync_pictures


def print_table(tab):
    num_columns = len(tab[0])
    col_widths = [2]*num_columns

    # Determine the columns widths.
    for row in tab:
        for col_nr, field in enumerate(row):
            col_widths[col_nr] = max(col_widths[col_nr], len(str(field)))

    for row in tab:
        for col_nr, field in enumerate(row):
            print(f"{field:{col_widths[col_nr]}} ", end='')
        print('')


class Command(BaseCommand):
    help = "Synchronizes the picture objects in the database and the picture and thumbnail files on disk."

    def add_arguments(self, parser):
        parser.add_argument("--hot-run", action="store_true", help="Actually update the database and delete files!")

    def handle(self, *args, **options):
        stats = sync_pictures(hot_run=options['hot_run'], verbosity=options['verbosity'])
        tab = [
            ["Pictures", "pictures/*", "|", "pictures/*", "thumbs/*"],
            ["--------", "----------", "|", "----------", "--------"],
            [
                stats["pic_objects_without_pic_file"],
                "",
                "|",
                stats["pic_files_without_thumb_file"],
                "",
            ],
            [
                stats["pic_objects_with_pic_file"],
                stats["pic_files_with_pic_object"],
                "|",
                stats["pic_files_with_thumb_file"],
                stats["thumb_files_with_pic_file"],
            ],
            [
                "",
                stats["pic_files_without_pic_object"],
                "|",
                "",
                stats["thumb_files_without_pic_file"],
            ],
            ["--------", "----------", "|", "----------", "--------"],
            [
                sum([stats["pic_objects_without_pic_file"], stats["pic_objects_with_pic_file"]]),
                sum([stats["pic_files_with_pic_object"], stats["pic_files_without_pic_object"]]),
                "|",
                sum([stats["pic_files_without_thumb_file"], stats["pic_files_with_thumb_file"]]),
                sum([stats["thumb_files_with_pic_file"], stats["thumb_files_without_pic_file"]]),
            ],
        ]

        print("")
        print_table(tab)
        print("")
