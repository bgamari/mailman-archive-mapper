# Mailman archive mapper

This script creates a map from Mailman 2 archive URLs to Mailman 3 archive
URLs.  This can be used to preserve links to message archives by generating
redirects from old to new URLs.

## Mailman 2 to 3 migration

Mailman 3 provides tools to import lists from Mailman 2, and also to import the
list archives from Mailman 2 lists, but it does not provide a way to preserve
the old URLs.  It's fairly common for mailing list messages to be referenced by
URLs to the list archives, so loss of these URLs can be a real problem when
migrating to Mailman 3.

## How does it work?

Mailman 2 assigns messages a numeric identifier as they are inserted into the
archives, and this is used as the filename for the message archive.  This is
assigned based on the order in which they are added to the archive, so in
theory you can derive the number given a copy of the mailbox containing the
messages.  In practice, occasional errors when inserting messages mean that
this isn't approach reliable.

Instaed, this script works by extracting the time and date of the message from
the archive HTML, and matching this up with the `Date` header of messages in
the `.mbox` file.

Mailman 3 archive URLs are based a hash of the `Message-ID` header, so can be
generated given a copy of the message.

This script outputs a map of old to new URLs, which can be used by a web server
to redirect requests.

Obviously this approach doesn't work if you have multiple messages with the
same timestamp (to the nearest second).

## Usage

The script takes as input the folder containing your Mailman 2 archives, and
the domain name used by your mailing lists (needed to generate the Mailman 3
list names).

```
mailman-archive-mapper /var/lib/mailman/archives/private/ example.com > url-map.txt
```

The script assumes that your old archives URLs start with `/mailman/private/`
and your new URLs start with `/mailman3/hyperkitty/` but you can change these
defaults with the `--old-base-url` and `--new-base-url` options.

By default, the script will process all lists in the specified directory, but
you can restrict it to specified lists using the `--list` option (can be
repeated for multiple lists).

The output file contains space-separated pairs of old and new URLs, one per
line.  This can be used directly with Apache's `RewriteMap` directive, but if
you've got a large archive, it's best to convert it to DBM format for more
efficient lookups.  This can be done using Apache's `httxt2dbm` utility:

```
httxt2dbm -i url-map.txt -o /etc/apache2/mailman-archives.map
```

This can then be used in an Apache config as follows (you will need
`mod_rewrite` enabled).

```
RewriteEngine On

RewriteMap mailman2-archives-map dbm:/etc/apache2/mailman-archives.map
RewriteRule ^(/mailman/private/.*)$ ${mailman2-archives-map:$1} [L,R]
```

## Limitations

As noted above, the script can't cope if you've got multiple messages with the
same timestamp.  It would be fairly straightforward to assign these correctly
based on order, but it doesn't currently do this.

The script ignores any messages in the archive that aren't valid UTF-8.

The script assumes that the date is contained in the first `<i>` tag in the
HTML file.
