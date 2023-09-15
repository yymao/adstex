"""
adstex: Automated generation of NASA ADS bibtex entries
from citation keys (identifiers, author+year) in your TeX source files.

Project website: https://github.com/yymao/adstex

The MIT License (MIT)
Copyright (c) 2015-2023 Yao-Yuan Mao (yymao)
http://opensource.org/licenses/MIT
"""
from __future__ import absolute_import, print_function

import os
import re
import warnings
from argparse import ArgumentParser
from builtins import input
from collections import defaultdict
from datetime import date
from shutil import copyfile
from joblib import Parallel, delayed

import ads
import bibtexparser
import packaging.version
import requests

try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

__version__ = "0.5.0"

_this_year = date.today().year % 100
_this_cent = date.today().year // 100

_re_comment = re.compile(r"(?<!\\)%.*(?=[\r\n])")
_re_bib = re.compile(r"\\(?:no)?bibliography\*?(?:(?!\n{2,})\s)*{((?:(?!\n{2,})[^{}])+)}")
_re_cite = re.compile(
    r"\\(?:bibentry|[cC]ite[a-zA]{0,7})\*?(?:(?!\n{2,})\s)*(?:(?<!\\)[\[<](?:(?!\n{2,}).)*?(?<!\\)[\]>](?:(?!\n{2,})\s)*)*{((?:(?!\n{2,})[^{}])+)}",
    re.S,
)
_re_fayear = re.compile(r"([A-Za-z-]+)(?:(?=[\W_])[^\s\d,]+)?((?:\d{2})?\d{2})")
_re_id = {}
_re_id["doi"] = re.compile(r"\b10\.\d{4,}(?:\.\d+)*\/(?:(?!['\"&<>])\S)+\b")
_re_id["bibcode"] = re.compile(r"\b\d{4}\D\S{13}[A-Z.:]\b")
_re_id["arxiv"] = re.compile(r"\b(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Za-z-]+)?\/\d{7})\b")

_name_prefix = (
    "van",
    "di",
    "de",
    "den",
    "der",
    "van de",
    "van den",
    "van der",
    "von der",
)
_name_prefix = sorted(_name_prefix, key=len, reverse=True)

# global configs
_database = "astronomy"
_disable_ssl_verification = False


def fixedAdsSearchQuery(*args, **kwargs):
    q = ads.SearchQuery(*args, **kwargs)
    q.session.headers.pop("Content-Type", None)
    if _disable_ssl_verification:
        q.session.verify = False
    return q


def fixedAdsExportQuery(*args, **kwargs):
    q = ads.ExportQuery(*args, **kwargs)
    if _disable_ssl_verification:
        q.session.verify = False
    return q


def get_bparser():
    try:
        mybparser = bibtexparser.bparser.BibTexParser(common_strings=True)
        mybparser.bib_database.strings["june"] = "June"
    except TypeError:
        mybparser = bibtexparser.bparser.BibTexParser()
    return mybparser


def _match_name_prefix(name):
    for prefix in _name_prefix:
        p = prefix.replace(" ", "")
        if name.lower().startswith(p):
            return " ".join((prefix, name[len(p) :]))


def _y2toy4(y2):
    y2 = int(y2)
    k = int(y2 > _this_year)
    return str((_this_cent - k) * 100 + y2)


def _is_like_string(s):
    try:
        s + ""
    except TypeError:
        return False
    return True


def _headerize(msg, extraline=True):
    return "{2}{0}\n{1}\n{0}".format("-" * 60, msg, "\n" if extraline else "")


def search_keys(files, find_bib=False):
    if _is_like_string(files):
        files = [files]
    bib = None
    keys = set()
    for f in files:
        with open(f) as fp:
            text = fp.read()
        text = _re_comment.sub("", text)
        if find_bib and not bib:
            m = _re_bib.search(text)
            if m:
                dirpath = os.path.dirname(f)
                bib = []
                for b in m.groups()[0].split(","):
                    b = b.strip()
                    if not b.lower().endswith(".bib"):
                        b += ".bib"
                    bib.append(os.path.join(dirpath, b))
        for m in _re_cite.finditer(text):
            for k in m.groups()[0].split(","):
                keys.add(k.strip())
    return keys, bib


def format_author(authors, max_char):
    s = authors[0]
    for author in authors[1:]:
        if len(s) + len(author) + 2 < max_char - 7:
            s = u"{}; {}".format(s, author)
        else:
            break
    else:
        return s
    return s + u" et al."


def format_ads_entry(i, entry, max_char=78):
    title = entry.title[0][: max_char - 4] if entry.title else "<no title>"
    return u"[{}] {} (cited {} times)\n    {}\n    {}".format(
        i,
        entry.bibcode,
        entry.citation_count,
        format_author(entry.author, max_char - 4),
        title,
    )


def id2bibcode(id_this, possible_id_types=("bibcode", "doi", "arxiv")):
    if _is_like_string(possible_id_types):
        possible_id_types = [possible_id_types]
    for id_type in possible_id_types:
        m = _re_id[id_type].search(id_this)
        if m:
            s = fixedAdsSearchQuery(q="identifier:\"{}\"".format(m.group()), fl=["bibcode"])
            try:
                return next(s).bibcode
            except (StopIteration, ads.exceptions.APIResponseError):
                pass


def authoryear2bibcode(author, year, key):
    q = 'author:"^{}" year:{} database:{}'.format(author, year, _database)
    entries = list(
        fixedAdsSearchQuery(
            q=q,
            fl=["id", "author", "bibcode", "title", "citation_count"],
            sort="citation_count desc",
            rows=20,
            max_pages=0,
        )
    )
    if entries:
        total = len(entries)
        print(
            _headerize(
                "Choose one entry from below for <{}> (most cited at the end)".format(
                    key
                )
            )
        )
        print(
            u"\n\n".join(
                format_ads_entry(total - i, e) for i, e in enumerate(reversed(entries))
            )
        )
        print(
            _headerize(
                "Choose one entry from above for <{}>".format(key),
                extraline=False,
            )
        )
        choices = list(range(0, len(entries) + 1))
        c = -1
        while c not in choices:
            c = input(
                "ENTER choice (if no matches, ENTER 0 to skip or ENTER an identifier): "
            )
            bibcode = id2bibcode(c)
            if bibcode:
                return bibcode
            try:
                c = int(c)
            except (TypeError, ValueError):
                pass
        if not c:
            return
        return entries[c - 1].bibcode
    elif " " not in author:
        new_author = _match_name_prefix(author)
        if new_author:
            return authoryear2bibcode(new_author, year, key)


def find_bibcode_interactive(key):
    m = _re_fayear.match(key)
    if m:
        fa, y = m.groups()
        if len(y) == 2:
            y = _y2toy4(y)
        bibcode = authoryear2bibcode(fa, y, key)
        if bibcode:
            return bibcode

    print(_headerize("ENTER an identifier (bibcode, arxiv, doi) for <{}>".format(key)))
    c = True
    while c:
        c = input("Identifier (or press ENTER to skip): ")
        bibcode = id2bibcode(c)
        if bibcode:
            return bibcode


def extract_bibcode(entry):
    m = _re_id["bibcode"].search(unquote(entry.get("adsurl", "")))
    if m:
        return m.group()


def entry2bibcode(entry):
    for field_name, possible_id_types in (
        ("adsurl", "bibcode"),
        ("doi", "doi"),
        ("eprint", "arxiv"),
        ("url", ("bibcode", "doi", "arxiv")),
        ("pages", "arxiv"),
    ):
        if field_name in entry:
            id_this = id2bibcode(unquote(entry[field_name]), possible_id_types)
            if id_this:
                return id_this


def update_bib(b1, b2):
    b1._entries_dict.clear()
    b2._entries_dict.clear()
    b1.entries_dict.update(b2.entries_dict)
    b1.entries = list(b1.entries_dict.values())
    return b1


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "files", metavar="TEX", nargs="+", help="tex files to search citation keys"
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="BIB",
        help="main bibtex file; new entries will be added to this file, existing entries may be updated",
    )
    parser.add_argument(
        "-r",
        "--other",
        nargs="+",
        metavar="BIB",
        help="other bibtex files that contain existing references (read-only)",
    )
    parser.add_argument(
        "--no-update",
        dest="update",
        action="store_false",
        help="for existing entries, do not check ADS for updates",
    )
    parser.add_argument(
        "--force-regenerate",
        action="store_true",
        help="for all existing entries, regenerate the bibtex with the latest version from ADS if found",
    )
    parser.add_argument(
        "--merge-other",
        action="store_true",
        help="merge the entries from other bibtex files",
    )  # thanks to syrte for adding this option
    parser.add_argument(
        "--include-physics",
        action="store_true",
        help="include physics database when searching ADS",
    )
    parser.add_argument(
        "--no-backup",
        dest="backup",
        action="store_false",
        help="back up output file if being overwritten",
    )
    parser.add_argument(
        "--disable-ssl-verification",
        action="store_true",
        help="disable SSL verification (it will render your API key vulnerable)",
    )
    parser.add_argument(
        "--parallel",
        "-P",
        action="store_true",
        help="enable parallel ADS update queries",
    )  # thanks to dwijn for adding this option
    parser.add_argument(
        "--threads",
        default=8,
        type=int,
        help="specify the number of threads used when --parallel is set (default: 8)",
    )  # thanks to dwijn for adding this option
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )
    args = parser.parse_args()

    if args.include_physics:
        global _database
        _database = '("astronomy" OR "physics")'

    if args.disable_ssl_verification:
        ans = input("You have chosen to disable SSL verification. This will render your API key vulnerable. Do you want to continue? [y/N] ")
        if ans in ("y", "Y", "yes", "Yes", "YES"):
            global _disable_ssl_verification
            _disable_ssl_verification = True
            warnings.filterwarnings("ignore", "Unverified HTTPS request is being made", Warning)
        else:
            print("OK, abort!")
            return

    if len(args.files) == 1 and args.files[0].lower().endswith(".bib"):  # bib update mode
        if args.output or args.other:
            parser.error(
                "Input file is a bib file, not tex file. This will enter bib update mode. Do not specify `--output` and `--other` together in this mode."
            )
        if not args.update:
            parser.error(
                "Input file is a bib file, not tex file. This will enter bib update mode. Must not specify --no-update"
            )
        if not os.path.isfile(args.files[0]):
            parser.error("Cannot locate input bib file {}".format(args.files[0]))
        keys = None
        args.output = args.files[0]

    elif args.output:  # bib output is specified
        keys, _ = search_keys(args.files, find_bib=False)

    else:  # bib output is missing, auto-identify
        keys, bib = search_keys(args.files, find_bib=True)
        if not bib:
            parser.error(
                "Cannot identify bibtex file from the tex source. Use -o to specify a bibtex file as output."
            )
        args.output = bib.pop(0)
        if args.other:
            args.other.extend(bib)
        else:
            args.other = bib

        msg = "Auto-identifying bibtex files...\n"
        msg += "Main bibtex source (output file): {}\n".format(args.output)
        if args.other:
            msg += "Additional bibtex sources: {}\n".format(", ".join(args.other))
        print(_headerize(msg))

    if os.path.isfile(args.output):
        with open(args.output) as fp:
            bib = bibtexparser.load(fp, parser=get_bparser())
    else:
        bib = bibtexparser.loads(" ", parser=get_bparser())

    bib_other = bibtexparser.loads(" ", parser=get_bparser())
    if args.other:
        for f in args.other:
            with open(f) as fp:
                bib_other = update_bib(
                    bib_other, bibtexparser.load(fp, parser=get_bparser())
                )

    if keys is None:  # bib update mode
        keys = list(bib.entries_dict)

    interactive = set()
    not_found = set()
    to_retrieve = set()
    all_entries = defaultdict(list)

    def update(key):
        key_exists = key in bib.entries_dict
        key_exists_in_others = key in bib_other.entries_dict

        if args.update:
            if key_exists:
                bibcode = extract_bibcode(bib.entries_dict[key])
                bibcode_new = entry2bibcode(bib.entries_dict[key])
            elif key_exists_in_others and args.merge_other:
                bibcode = extract_bibcode(bib_other.entries_dict[key])
                bibcode_new = entry2bibcode(bib_other.entries_dict[key])
            else:
                bibcode_new = None

            if bibcode_new:
                all_entries[bibcode_new].append(key)
                if bibcode_new != bibcode or args.force_regenerate:
                    to_retrieve.add(bibcode_new)
                    print(
                        "{}:{} UPDATE => {}".format(
                            key,
                            "" if key_exists else " FOUND IN SECONDARY BIB SOURCES,",
                            bibcode_new,
                        )
                    )
                    return

        if key_exists:
            print("{}: EXISTING".format(key))
            return

        if key_exists_in_others and args.merge_other:
            bib.entries_dict[key] = bib_other.entries_dict[key]
            bib.entries = list(bib.entries_dict.values())
            print("{}: FOUND IN OTHER BIB SOURCE, MERGED".format(key))
            return

        if key_exists_in_others:
            print("{}: FOUND IN OTHER BIB SOURCE, IGNORED".format(key))
            return

        bibcode = id2bibcode(key)
        if bibcode:
            to_retrieve.add(bibcode)
            all_entries[bibcode].append(key)
            print("{}: NEW ENTRY => {}".format(key, bibcode))
            return

        # if all above failed
        interactive.add(key)

    if args.parallel:
        Parallel(n_jobs=args.threads, prefer="threads")(delayed(update)(key) for key in keys)
    else:
        [update(key) for key in keys]

    if interactive:
        print(_headerize("Resolving keys that do not contain identifiers..."))
        for key in interactive:
            bibcode = find_bibcode_interactive(key)
            if bibcode:
                to_retrieve.add(bibcode)
                all_entries[bibcode].append(key)
                print("{}: NEW ENTRY => {}".format(key, bibcode))
            else:
                not_found.add(key)
                print("{}: NOT FOUND".format(key))

    if not_found:
        print(_headerize("Please check the following keys"))
        for key in not_found:
            print(key)

    repeated_keys = [t for t in all_entries.items() if len(t[1]) > 1]
    if repeated_keys:
        print(_headerize("The following keys refer to the same entry"))
        for b, k in repeated_keys:
            print(
                "{1} has been referred as the following keys; please keep only one:\n{0}\n".format(
                    " ".join(k), b
                )
            )

    if to_retrieve:
        print(_headerize("Building new bibtex file, please wait..."))
        bib_new = bibtexparser.loads(
            fixedAdsExportQuery(list(to_retrieve), "bibtex").execute(), parser=get_bparser()
        )
        for entry in bib_new.entries:
            entry["ID"] = all_entries[entry["ID"]][0]
        bib = update_bib(bib, bib_new)
        bib_dump_str = bibtexparser.dumps(bib).encode("utf8")
        if args.backup and os.path.isfile(args.output):
            copyfile(args.output, args.output + ".bak")
        with open(args.output, "wb") as fp:
            fp.write(bib_dump_str)

    print(_headerize("Done!"))

    # check version
    try:
        latest_version = packaging.version.parse(
            requests.get(
                "https://pypi.python.org/pypi/adstex/json", timeout=0.1,
            ).json()["info"]["version"]
        )
    except (requests.RequestException, KeyError, ValueError):
        pass
    else:
        if latest_version > packaging.version.parse(__version__):
            msg = "A newer version of adstex (v{}) is now available!\n".format(
                latest_version
            )
            msg += "Please consider updating it by running:\n\n"
            msg += "pip install adstex=={}".format(latest_version)
            print(_headerize(msg))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(_headerize("Abort! adstex interupted by a keyboard signal!"))
