"""
Find all citation keys in your LaTeX documents and search NASA ADS
to generate corresponding bibtex entries.

Project website: https://github.com/yymao/adstex

The MIT License (MIT)
Copyright (c) 2015-2018 Yao-Yuan Mao (yymao)
http://opensource.org/licenses/MIT
"""
from __future__ import print_function
import os
import re
from argparse import ArgumentParser
from datetime import date
try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote
from collections import defaultdict
from builtins import input
import ads
import bibtexparser

__version__ = "0.2.2"

_this_year = date.today().year % 100
_this_cent = date.today().year // 100

_re_cite = re.compile(r'\\[cC]ite[a-z]{0,7}\*?(?:\[.*?\])*{([\w\s/&.:,-]+)}')
_re_fayear = re.compile(r'([A-Za-z-]+)(?:(?=[\W_])[^\s\d,]+)?((?:\d{2})?\d{2})')
_re_id = {}
_re_id['doi'] = re.compile(r'10\.\d{4,}(?:\.\d+)*\/(?:(?![\'"&<>])\S)+')
_re_id['bibcode'] = re.compile(r'\d{4}\D\S{13}[A-Z.:]$')
_re_id['arxiv'] = re.compile(r'(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Za-z-]+)?\/\d{7})')

_name_prefix = ('van', 'di', 'de', 'den', 'der', 'van de', 'van den', 'van der', 'von der')
_name_prefix = sorted(_name_prefix, key=len, reverse=True)

_database = "astronomy"


def fixedAdsSearchQuery(*args, **kwargs):
    q = ads.SearchQuery(*args, **kwargs)
    q.session
    if "Content-Type" in q._session.headers:
        del q._session.headers["Content-Type"]
    return q


def get_bparser():
    try:
        mybparser = bibtexparser.bparser.BibTexParser(common_strings=True)
        mybparser.bib_database.strings['june'] = 'June'
    except TypeError:
        mybparser = bibtexparser.bparser.BibTexParser()
    return mybparser


def _match_name_prefix(name):
    for prefix in _name_prefix:
        p = prefix.replace(' ', '')
        if name.lower().startswith(p):
            return ' '.join((prefix, name[len(p):]))


def _y2toy4(y2):
    y2 = int(y2)
    k = int(y2 > _this_year)
    return str((_this_cent - k) * 100 + y2)


def _is_like_string(s):
    try:
        s + ''
    except TypeError:
        return False
    return True


def _headerize(msg, extraline=True):
    return '{2}{0}\n{1}\n{0}'.format('-'*60, msg, '\n' if extraline else '')


def search_keys(files):
    if _is_like_string(files):
        files = [files]
    keys = set()
    for f in files:
        with open(f) as fp:
            text = fp.read()
        for m in _re_cite.finditer(text):
            for k in m.groups()[0].split(','):
                keys.add(k.strip())
    return keys


def format_author(authors, max_char):
    s = authors[0]
    for author in authors[1:]:
        if len(s) + len(author) + 2 < max_char-7:
            s = u'{}; {}'.format(s, author)
        else:
            break
    else:
        return s
    return s + u' et al.'


def format_ads_entry(i, entry, max_char=78):
    title = entry.title[0][:max_char-4] if entry.title else '<no title>'
    return u'[{}] {} (cited {} times)\n    {}\n    {}'.format(i, entry.bibcode,
            entry.citation_count, format_author(entry.author, max_char-4),
            title)


def id2bibcode(id_this):
    for id_type in ('bibcode', 'arxiv', 'doi'):
        m = _re_id[id_type].match(id_this)
        if m:
            s = fixedAdsSearchQuery(q=':'.join((id_type, m.group())), fl=['bibcode'])
            try:
                return s.next().bibcode
            except StopIteration:
                return


def authoryear2bibcode(author, year, key):
    q = 'author:"^{}" year:{} database:{}'.format(author, year, _database)
    entries = list(fixedAdsSearchQuery(q=q, fl=['id', 'author', 'bibcode', 'title', 'citation_count'],
                                       sort='citation_count desc', rows=20, max_pages=0))
    if entries:
        total = len(entries)
        print(_headerize('Choose one entry from below for "{}" (most cited at the end)'.format(key)))
        print(u'\n\n'.join(format_ads_entry(total-i, e) for i, e in enumerate(reversed(entries))))
        print(_headerize('Choose one entry from above for "{}"'.format(key, extraline=False)))
        choices = list(range(0, len(entries)+1))
        c = -1
        while c not in choices:
            c = input('ENTER choice (if no matches, ENTER 0 to skip or ENTER an identifier): ')
            bibcode = id2bibcode(c)
            if bibcode:
                return bibcode
            try:
                c = int(c)
            except (TypeError, ValueError):
                pass
        if not c:
            return
        return entries[c-1].bibcode
    elif ' ' not in author:
        new_author = _match_name_prefix(author)
        if new_author:
            return authoryear2bibcode(new_author, year, key)


def find_bibcode(key):
    bibcode = id2bibcode(key)
    if bibcode:
        return bibcode

    m = _re_fayear.match(key)
    if m:
        fa, y = m.groups()
        if len(y) == 2:
            y = _y2toy4(y)
        bibcode = authoryear2bibcode(fa, y, key)
        if bibcode:
            return bibcode

    print(_headerize('ENTER an identifier (bibcode, arxiv, doi) for "{}"'.format(key)))
    c = True
    while c:
        c = input('Identifier (or press ENTER to skip): ')
        bibcode = id2bibcode(c)
        if bibcode:
            return bibcode


def extract_bibcode(entry):
    return unquote(entry.get('adsurl', '').rpartition('/')[-1])


def entry2bibcode(entry):
    if 'adsurl' in entry:
        s = fixedAdsSearchQuery(bibcode=extract_bibcode(entry), fl=['bibcode'])
        try:
            return s.next().bibcode
        except StopIteration:
            pass

    if 'doi' in entry:
        s = fixedAdsSearchQuery(doi=entry['doi'], fl=['bibcode'])
        try:
            return s.next().bibcode
        except StopIteration:
            pass

    if 'eprint' in entry:
        s = fixedAdsSearchQuery(arxiv=entry['eprint'], fl=['bibcode'])
        try:
            return s.next().bibcode
        except StopIteration:
            pass


def update_bib(b1, b2):
    b1._entries_dict.clear()
    b2._entries_dict.clear()
    b1.entries_dict.update(b2.entries_dict)
    b1.entries = list(b1.entries_dict.values())
    return b1


def main():
    parser = ArgumentParser()
    parser.add_argument('files', metavar='TEX', nargs='+', help='tex files to search citation keys')
    parser.add_argument('-o', '--output', metavar='BIB', required=True, help='main bibtex file; new entries will be added to this file, existing entries may be updated')
    parser.add_argument('-r', '--other', nargs='+', metavar='BIB', help='other bibtex files that contain existing references (read-only)')
    parser.add_argument('--no-update', dest='update', action='store_false', help='for existing entries, do not check ADS for updates')
    parser.add_argument('--force-update', dest='force_update', action='store_true', help='for all existing entries, overwrite with the latest version from ADS')
    parser.add_argument('--include-physics', dest='include_physics', action='store_true', help='include physics database when searching ADS')
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    args = parser.parse_args()

    if args.include_physics:
        _database = '("astronomy" OR "physics")'

    keys = search_keys(args.files)

    if os.path.isfile(args.output):
        with open(args.output) as fp:
            bib = bibtexparser.load(fp, parser=get_bparser())
    else:
        bib = bibtexparser.loads(' ', parser=get_bparser())

    bib_other = bibtexparser.loads(' ', parser=get_bparser())
    if args.other:
        for f in args.other:
            with open(f) as fp:
                bib_other = update_bib(bib_other, bibtexparser.load(fp, parser=get_bparser()))

    not_found = set()
    to_retrieve = set()
    all_entries = defaultdict(list)
    try:
        for key in keys:
            if key in bib.entries_dict:
                if args.update:
                    bibcode = extract_bibcode(bib.entries_dict[key])
                    bibcode_new = entry2bibcode(bib.entries_dict[key])
                    if bibcode_new:
                        all_entries[bibcode_new].append(key)
                        if bibcode_new != bibcode or args.force_update:
                            to_retrieve.add(bibcode_new)
                            print('{}: UPDATE => {}'.format(key, bibcode_new))
                            continue
                print('{}: EXISTING'.format(key))
                continue

            if key in bib_other.entries_dict:
                print('{}: FOUND IN OTHER REFS, IGNORED'.format(key))
                continue

            bibcode = find_bibcode(key)
            if bibcode:
                to_retrieve.add(bibcode)
                all_entries[bibcode].append(key)
                print('{}: NEW ENTRY => {}'.format(key, bibcode))
            else:
                not_found.add(key)
                print('{}: NOT FOUND'.format(key))
    except KeyboardInterrupt:
        print()

    if not_found:
        print(_headerize('Please check the following keys'))
        for key in not_found:
            print(key)

    repeated_keys = [t for t in all_entries.items() if len(t[1]) > 1]
    if repeated_keys:
        print(_headerize('The following keys refer to the same entry'))
        for b, k in repeated_keys:
            print('{1} has been referred as the following keys; please keep only one:\n{0}\n'.format(' '.join(k), b))

    if to_retrieve:
        print(_headerize('Building new bibtex file, please wait...'))
        bib_new = bibtexparser.loads(ads.ExportQuery(list(to_retrieve), 'bibtex').execute(), parser=get_bparser())
        for entry in bib_new.entries:
            entry['ID'] = all_entries[entry['ID']][0]
        bib = update_bib(bib, bib_new)
        bib_dump_str = bibtexparser.dumps(bib).encode('utf8')
        with open(args.output, 'wb') as fp:
            fp.write(bib_dump_str)

    print(_headerize('Done!'))


if __name__ == "__main__":
    main()
