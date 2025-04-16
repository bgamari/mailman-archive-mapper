#!/usr/bin/env python3

import sys
import os
from dateutil.parser import parse, ParserError
from glob import glob
from bs4 import BeautifulSoup
from hyperkitty.lib.utils import get_message_id_hash
import argparse

def warn(msg):
    print(msg, file=sys.stderr)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-base-url", default="/mailman/private/", help="URL prefix for Mailman 2 archive URLs (default: /mailman/private/)")
    parser.add_argument("--new-base-url", default="/mailman3/hyperkitty/", help="URL prefix for Mailman 3 archive URLs (default: /mailman3/hyperkitty/)")
    parser.add_argument("--list", action="append", help="Name of list to map. Can be repeated for multiple lists. Default is to process all lists.")
    parser.add_argument("old_archive_path")
    parser.add_argument("domain_name")
    args = parser.parse_args()

    archive_root = args.old_archive_path

    if args.list is None:
        lists = [os.path.basename(l).removesuffix('.mbox') for l in glob(os.path.join(args.old_archive_path, "*.mbox"))]
    else:
        lists = args.list

    for listname in lists:
        mbox_file = os.path.join(archive_root, listname + ".mbox", listname + ".mbox")
        hyperkitty_url = args.new_base_url.rstrip('/') + "/list/%s@%s/message/%s/"

        date = None
        message_id = None
        processed = True
        link_map = dict()
        from_line = None
        with open(mbox_file, "rb") as fin:
            for lineb in fin:
                try:
                    line = lineb.decode("utf-8")
                except UnicodeDecodeError:
                    continue
                if line.startswith('From '):
                    if not processed:
                        warn("Failed to process mail: " + from_line)
                    from_line = line
                    date = None
                    message_id = None
                    processed = False

                if not processed:
                    if date is None and line.startswith('Date:'):
                        date = line[5:].strip()
                    if message_id is None and line.lower().startswith('message-id:'):
                        message_id = line[11:].strip().lstrip('<').rstrip('>')
                    if date is not None and message_id is not None:
                        try:
                            parsed_date = parse(date)
                            if parsed_date in link_map:
                                warn("Duplicate mails for: " + date)
                            else:
                                link_map[parsed_date] = message_id
                            processed = True
                        except ParserError:
                            warn(f"Failed to parse date: {date}")
                            processed = False

        for html_file in glob(os.path.join(archive_root, listname, '*', '[0-9]*.html')):
            with open(html_file) as fin:
                try:
                    soup = BeautifulSoup(fin, features="lxml")
                except UnicodeDecodeError:
                    warn("Unicode error reading %s" % html_file)
                    continue

                try:
                    date = soup.find_all("i")[0].get_text()
                    d = parse(date)
                except IndexError:
                    warn(f"Failed to find date in {html_file}")
                    continue
                except ParserError:
                    warn(f"Failed to parse date: {date}")
                    continue

                msg_id = link_map.get(d, None)
                if msg_id is not None:
                    msg_id_hash = get_message_id_hash(msg_id)
                    print(args.old_base_url + html_file.removeprefix(archive_root).lstrip('/') + " " + hyperkitty_url % (listname, args.domain_name, msg_id_hash))


if __name__ == '__main__':
    main()
