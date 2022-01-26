from datetime import datetime
from PIL import Image, ImageDraw


def fmt_bytes(size, decimal_places=2):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if size < 1024.0 or unit == 'PiB':
            break
        size /= 1024.0

    return f"{size:.{decimal_places}f} {unit}"


def get_pic_stem_from_data(dt, importance):
    return f'pic_{dt.strftime("%Y%m%d_%H%M%S")}_{importance}'


def get_data_from_pic_stem(pic_stem):
    try:
        dt = datetime.strptime(pic_stem[4:19], "%Y%m%d_%H%M%S")
    except ValueError:
        dt = datetime(2000, 1, 1)

    try:
        importance = int(pic_stem[20:21])
    except ValueError:
        importance = 0

    cross_check = get_pic_stem_from_data(dt, importance)
    if pic_stem != cross_check:
        # print(f"Bad pic_stem: {pic_stem} != {cross_check}")
        pass

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


def create_simple_image(text=None, text_color=(0, 50, 80), size=(400, 300), background_color=(255, 220, 200)):
    img = Image.new("RGB", size, background_color)
    if text:
        d = ImageDraw.Draw(img)
        d.text((10, 10), text, fill=text_color)
    return img
