from pathlib import Path
from django.conf import settings
from Core.models import Picture


def sync_pictures(hot_run, verbosity=1):
    """Synchronizes the picture objects in the database and the picture and thumbnail files on disk."""

    stats = {
        'pic_objects_with_pic_file': 0,
        'pic_objects_without_pic_file': 0,

        'pic_files_with_pic_object': 0,     # same as `pic_objects_with_pic_file`
        'pic_files_without_pic_object': 0,

        'pic_files_with_thumb_file': 0,
        'pic_files_without_thumb_file': 0,

        'thumb_files_with_pic_file': 0,     # same as `pic_files_with_thumb_file`
        'thumb_files_without_pic_file': 0,
    }

    # Examine the `Picture` objects in the database.
    for pic_obj in Picture.objects.all():
        pic_path = Path(settings.MEDIA_ROOT, Picture.PICTURES_SUBDIR, pic_obj.filename)

        if pic_path.is_file():
            stats['pic_objects_with_pic_file'] += 1
        else:
            # There is no image file on disk for this picture.
            # So there is nothing we can do but to delete the database object.
            stats['pic_objects_without_pic_file'] += 1
            if verbosity > 1:
                print("missing file", pic_path, "--> deleting related db object")
            if hot_run:
                pic_obj.delete()

    # Examine the files in `pictures/*`.
    pics_dir = Path(settings.MEDIA_ROOT, Picture.PICTURES_SUBDIR)
    for pic_path in pics_dir.iterdir():
        if Picture.objects.filter(filename=pic_path.name).exists():
            stats['pic_files_with_pic_object'] += 1
        else:
            # There is an image file that is not known to the database.
            # Well, let's pick it up!
            stats['pic_files_without_pic_object'] += 1
            if verbosity > 1:
                print("picking up file", pic_path)
            # if is_suitable:
            #     pickup()
            # else:
            #     del_file()

        # A thumbnail is expected to have the same suffix as the image – or 'jpg'.
        thumb_path = Path(settings.MEDIA_ROOT, Picture.THUMBNAILS_SUBDIR, pic_path.name)
        if thumb_path.is_file() or thumb_path.with_suffix('.jpg').is_file():
            stats['pic_files_with_thumb_file'] += 1
        else:
            # There is an image file that has no corresponding thumb file.
            # It's okay to ignore this, as thumbnails are lazily recreated as required.
            stats['pic_files_without_thumb_file'] += 1

    # Examine the files in `thumbnails/*`.
    thumbs_dir = Path(settings.MEDIA_ROOT, Picture.THUMBNAILS_SUBDIR)
    for thumb_path in thumbs_dir.iterdir():
        pic_path = Path(settings.MEDIA_ROOT, Picture.PICTURES_SUBDIR, thumb_path.name)
        if any(pic_path.with_suffix(sfx).is_file() for sfx in Picture.VALID_SUFFIXES):
            stats['thumb_files_with_pic_file'] += 1
        else:
            # There is no image file on disk for this thumbnail.
            # So there is nothing we can do but to delete the thumbnail file.
            stats['thumb_files_without_pic_file'] += 1
            if verbosity > 1:
                print("missing file", pic_path, "--> deleting related thumbnail file")
            if hot_run:
                thumb_path.delete()

    return stats
