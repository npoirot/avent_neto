#!/usr/bin/env python
import os
import stat
import http.client
from urllib.parse import urlparse
try:
    from BeautifulSoup import BeautifulSoup
except:
    from bs4 import BeautifulSoup

# https://avent.netophonix.com/2020/mono/1
# https://www.les2minutesdupeuple.ml/web/mp3/0001.mp3
website = "avent.netophonix.com"
year = 2020
min_nb = 1
max_nb = 25
prefix = "03x"
webpath = "/" + str(year) + "/mono/"

# Connect to main website and for each id, get filename and link location
for i in range(min_nb, max_nb + 1):
    conn = http.client.HTTPSConnection(website)
    print("Getting file nb " + str(i))
    conn.request("GET", webpath + str(i))
    r = conn.getresponse()
    if r.status != 200 or r.reason != "OK":
        print("An error occured getting file nb: " + str(i))
        continue

    webpage = r.read()
    conn.close()
    parsed_data = BeautifulSoup(webpage, 'html.parser')
    file_link = parsed_data.body.find('a', attrs={'class':'download-link'}).get('href')

    # Get rid of title prefix and suffix "*******- **********,******"
    # Where '*' is any character          prefix   ^^^^^^^^^^ suffix
    title = parsed_data.title.text
    if title.find('- ') != -1:
        title = title[title.find('- ') + 2:]
    if title.rfind(',') != -1:
        title = title[:title.rfind(',')]
    if title.endswith('.mp3'):
        title = title[:-4]
    filename = prefix + "{0:0=2d}".format(i) + "-" + title + ".mp3"
    filename = filename.replace(' /', ',').replace('/', ',')

    # Connect to website hosting the downloadable file
    conn = http.client.HTTPSConnection(urlparse(file_link).netloc)
    conn.request("GET", urlparse(file_link).path)
    r = conn.getresponse()
    if r.status != 200 or r.reason != "OK":
        print("An error occured getting " + file_link)
        conn.close()
        continue

    if (os.path.isfile(filename)):
        override = input("'" + filename + "' already exists. Do you want to replace it ? [y/N]")
        if override.lower() != 'y':
            continue
        else:
            os.unlink(filename)

    # Write the returned file on the disk
    print("Writing " + filename)
    if os.name == 'nt':
        fd = os.open(filename, os.O_CREAT|os.O_WRONLY|os.O_BINARY)
    else:
        fd = os.open(filename, os.O_CREAT|os.O_WRONLY)
    os.write(fd, r.read())
    os.close(fd)
    os.chmod(filename, stat.S_IRUSR|stat.S_IWUSR|
                       stat.S_IRGRP|
                       stat.S_IROTH)
    conn.close()

input("Download(s) complete, press 'Enter' to exit.")
