from datetime import datetime
from pathlib import Path
from shutil import disk_usage
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


def fmt_bytes(size, decimal_places=2):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if size < 1024.0 or unit == 'PiB':
            break
        size /= 1024.0

    return f"{size:.{decimal_places}f} {unit:3}"


def get_data_from_pic_stem(pic_stem):
    try:
        dt = datetime.strptime(pic_stem[4:19], "%Y%m%d_%H%M%S")
    except ValueError:
        dt = datetime(2000, 1, 1)

    try:
        importance = int(pic_stem[20:21])
    except ValueError:
        importance = 0

    # cross_check = get_pic_stem_from_data(dt, importance)
    # if pic_stem != cross_check:
    #     # print(f"Bad pic_stem: {pic_stem} != {cross_check}")
    #     pass

    return dt, importance


def get_score(dt, importance, now):
    """
    This function computes the score that indicates the significance of a picture.
    The significance determines the order in which pictures are deleted when disk
    space gets scarce.

    Some notes:

      - Older pictures should be deleted before newer pictures.
      - Less important pictures should be deleted before more important pictures.

    For example, a picture that is unimportant but only a day old could have
    the same significance (priority for deletion) as another picture that is
    very important but now several years old.

    That is, if we put the age and the importance of a picture into a coordinate
    system, the picture with the coordinate p1 = (age: 1 day, importance: 1)
    should have the same score as a picture at coordinate p2 = (age: 8 years,
    importance: 8).

    Note that we can interpolate between p1 and p2 and that the line through
    p1 and p2 can be considered a 2-dimensional hyperplane. The distance of any
    point to that hyperplane can be taken as the score of that point.
    """
    age = (now - dt).total_seconds() / 3600.0   # age in hours
    vec = (age, importance)
    nrm = (-(8 - 1), (365*8 - 1)*24.0)

    return vec[0]*nrm[0] + vec[1]*nrm[1]


def gather_pictures(clean_dir, now):
    pics = []

    for pic_path in Path(clean_dir).iterdir():
        pics.append(
            (
                pic_path,
                pic_path.stat().st_size,
                get_score(*get_data_from_pic_stem(pic_path.stem), now),
            )
        )

    # Sort the pictures by score.
    pics.sort(key=lambda pic: -pic[2])
    return pics


def cleanup_pictures(hot_run, out=None):
    GiB = pow(1024, 3)
    MIN_PICS_TOTAL =  1*GiB
    MAX_PICS_TOTAL = 20*GiB
    MIN_DISK_FREE  =  2*GiB

    disk_total, disk_used, disk_free = disk_usage("/")
    btd_disk = max(MIN_DISK_FREE - disk_free, 0)

    print(f"{fmt_bytes(disk_total):>10} disk space total", file=out)
    print(f"{fmt_bytes(disk_used):>10} disk space used", file=out)
    print(f"{fmt_bytes(disk_free):>10} disk space free", file=out)
    print(f"{fmt_bytes(MIN_DISK_FREE):>10} disk space to be kept free (MIN_DISK_FREE)", file=out)
    print(f"{fmt_bytes(btd_disk):>10} to delete (by disk space limits)", file=out)

    pics_dir = Path(settings.MEDIA_ROOT, Picture.PICTURES_SUBDIR)
    pics = gather_pictures(pics_dir, datetime.now())
    pics_total_bytes = sum(pic[1] for pic in pics)
    btd_pics = max(pics_total_bytes - MAX_PICS_TOTAL, 0)

    print(f"\n{len(pics)} pictures", file=out)
    print(f"{fmt_bytes(pics_total_bytes):>10} picture space taken", file=out)
    print(f"{fmt_bytes(MAX_PICS_TOTAL):>10} picture space limit (MAX_PICS_TOTAL)", file=out)
    print(f"{fmt_bytes(btd_pics):>10} to delete (by picture space limits)", file=out)

    delete_at_most = max(pics_total_bytes - MIN_PICS_TOTAL, 0)
    pic_bytes_to_delete = min(max(btd_disk, btd_pics), delete_at_most)

    print(f"\ncombined", file=out)
    print(f"{fmt_bytes(MIN_PICS_TOTAL):>10} minimum picture space to keep (MIN_PICS_TOTAL)", file=out)
    print(f"{fmt_bytes(pic_bytes_to_delete):>10} to delete (by combined limits)", file=out)

    while pics and pic_bytes_to_delete > 0:
        pic = pics.pop()

        if hot_run:
            pic[0].unlink(missing_ok=True)
            print(f"  deleted {pic[0]},{pic[1]:>8} bytes, score {pic[2]}", file=out)

            num_del, details = Picture.objects.filter(filename=pic[0].name).delete()
            if num_del != 1:
                print("  WARNING: Could not delete the related `Picture` object!", file=out)
        else:
            print(f"  would delete {pic[0]},{pic[1]:>8} bytes, score {pic[2]}", file=out)

        pic_bytes_to_delete -= pic[1]
        pics_total_bytes -= pic[1]

    print(f"\n{len(pics)} pictures left", file=out)
    print(f"{fmt_bytes(pics_total_bytes):>10} picture space taken", file=out)
