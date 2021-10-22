import os
import subprocess


def get_book_meta(i: str):
    book_meta = {
        'Title': 'Unknown',
        'Author(s)': 'Unknown',
        'Publisher': 'Unknown',
        'Book Producer': 'Unknown',
        'Languages': 'Unknown',
        'Comments': 'Unknown',
        'Published': 'Unknown',
        'Identifiers': 'Unknown',
    }
    ebook_meta = os.getenv('SHELL_CALIBRE_EBOOK_META', '')
    if not os.path.exists(i) or ebook_meta == '':
        return book_meta
    result, _ = run_command([ebook_meta, i, '--get-cover', os.path.dirname(i) + os.sep + 'cover.png'])
    if result.find('\r\n') < 0:
        return book_meta

    for s in result.split('\r\n'):
        print(s)
        if s.find(':') < 0:
            continue
        for key in book_meta.keys():
            if s.split(':')[0].rstrip() == key:
                book_meta[key] = ''.join(s.split(':')[1:]).strip()

    if book_meta['Published'] != 'Unknown':
        book_meta['Published'] = book_meta['Published'][:10]
    return book_meta


def convert_book_to_mobi(i: str, o='') -> (bool, str):
    if os.path.splitext(i)[1] == '.mobi':
        return True, i
    if o == '':
        o = os.path.splitext(i)[0] + '.mobi'
    ebook_convert = os.getenv('SHELL_CALIBRE_EBOOK_CONVERT', '')
    if not os.path.exists(i) or ebook_convert == '':
        return False, ''
    if os.path.exists(o):
        return True, o

    run_command([ebook_convert, i, o])
    return os.path.exists(o), o


def run_command(command):
    proc = subprocess.Popen(
        command,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout_value, stderr_value = proc.communicate()
    return stdout_value.decode('utf-8'), stderr_value
