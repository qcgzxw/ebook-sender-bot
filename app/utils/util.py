import os
import re
import subprocess

from app.config.configs import is_windows


def get_book_meta(i: str):
    """Get ebook information"""
    book_meta = {
        'Title': 'Unknown',
        'Author(s)': 'Unknown',
        'Publisher': 'Unknown',
        'Book Producer': 'Unknown',
        'Tags': 'Unknown',
        'Languages': 'Unknown',
        'Comments': 'Unknown',
        'Published': 'Unknown',
        'Rights': 'Unknown',
        'Identifiers': 'Unknown',
    }
    supported_formats_for_reading_meta = ['azw', 'azw1', 'azw3', 'azw4', 'cb7', 'cbr', 'cbz', 'chm', 'docx', 'epub',
                                          'fb2', 'fbz', 'html', 'htmlz', 'imp', 'lit', 'lrf', 'lrx', 'mobi', 'odt',
                                          'oebzip', 'opf', 'pdb', 'pdf', 'pml', 'pmlz', 'pobi', 'prc', 'rar', 'rb',
                                          'rtf', 'snb', 'tpz', 'txt', 'txtz', 'updb']
    if i.split('.')[-1].lower() not in supported_formats_for_reading_meta:
        return book_meta
    ebook_meta = 'ebook-meta.exe' if is_windows() else 'ebook-meta'
    if not os.path.exists(i) or ebook_meta == '':
        return book_meta
    result, _ = __run_command([ebook_meta, i, '--get-cover', os.path.dirname(i) + os.sep + 'cover.png'])
    if len(result.splitlines()) <= 2:
        return book_meta

    for line in result.splitlines():
        if line.find(':') < 0:
            continue
        for key in book_meta.keys():
            # line="Title               : Lawrence Block Eight Million Ways to Die"
            # first_part = "Title               "
            # second_part = " Lawrence Block Eight Million Ways to Die"
            first_part = line.split(':')[0]
            second_part = line[len(first_part) + 1:]
            if first_part.strip() == key:
                book_meta[key] = replace_all(remove_html_tags(second_part.strip()), {
                    "/": " ",
                    "\\": " ",
                    ":": "：",
                    "*": "X",
                    "?": "？",
                    "<": "《",
                    ">": "》",
                    "|": " ",
                })

    # line="Published           : 2010-01-15T06:28:29.127000+00:00"
    if book_meta['Published'] != 'Unknown':
        book_meta['Published'] = book_meta['Published'][:10]
    if os.path.exists(os.path.dirname(i) + os.sep + 'cover.png'):
        book_meta['cover_path'] = os.path.dirname(i) + os.sep + 'cover.png'
    return book_meta


def convert_book(i: str, file_ext='mobi', o='') -> (bool, str):
    """Convert ebook to mobi format"""
    supported_formats_for_converting = (
        'azw', 'azw1', 'azw3', 'azw4', 'epub', 'mobi', 'kfx', 'fb2', 'html', 'lit', 'lrf', 'pdb')
    if i.split('.')[-1].lower() not in supported_formats_for_converting \
            or os.path.splitext(i)[1].lower() == "." + file_ext:
        return True, i
    if o == '':
        o = os.path.splitext(i)[0] + "." + file_ext
    ebook_convert = 'ebook-convert.exe' if is_windows() else 'ebook-convert'
    if not os.path.exists(i) or ebook_convert == '':
        return False, ''
    if os.path.exists(o):
        return True, o

    __run_command([ebook_convert, i, o])
    return os.path.exists(o), o


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def replace_all(text: str, dic: dict):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


def __run_command(command):
    """Run system command"""
    # Why does subprocess.Popen() with shell true work differently on linux vs windows.
    # https://stackoverflow.com/questions/1253122/why-does-subprocess-popen-with-shell-true-work-differently-on-linux-vs-windows
    proc = subprocess.Popen(
        command,
        shell=is_windows(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout_value, stderr_value = proc.communicate()
    return stdout_value.decode('utf-8'), stderr_value
