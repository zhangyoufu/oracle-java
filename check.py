#!/usr/bin/env python3
import logging
import re
import requests
import sys
import urllib.parse

def parse_page(page):
    return result

def main():
    logging.basicConfig(
        stream=sys.stderr,
        level='INFO',
        format='[%(levelname)s] %(message)s',
    )

    major = sys.argv[1]
    url = sys.argv[2]

    # fetch download page
    rsp = requests.get(url)
    logging.info(f'download page: {url} {rsp.status_code} {rsp.reason}')
    if rsp.status_code != 200:
        return
    if 'oraclelicense=' not in rsp.text:
        return
    page = rsp.text

    # parse checksum page url
    m = re.search(r'<a target="" href="([^"]+)">checksum </a>', page)
    assert m, page
    url = m.group(1)
    if url.startswith('//'):
        url = 'https:' + url

    # fetch checksum page
    rsp = requests.get(url)
    logging.info(f'checksum page: {url} {rsp.status_code} {rsp.reason}')
    if rsp.status_code != 200:
        return
    checksum_page = rsp.text

    # find download link
    for m in re.finditer(r"data-file='(//[^']+)'", page):
        url = 'https:' + m.group(1)
        filename = url.rsplit('/', 1)[1]
        assert re.fullmatch(r'[-_.0-9a-z]+', filename), filename
        if 'linux-x64' in filename and 'demos' not in filename and filename.endswith('.tar.gz'):
            break
    else:
        logging.error('link not found\n')

    # parse download link
    url = url.replace('/otn/', '/otn-pub/')
    m = re.match(r'https://download\.oracle\.com/otn-pub/java/jdk/([^/]+)/([0-9a-f]{32})/', url)
    assert m, url
    version = urllib.parse.unquote(m.group(1), errors='strict')
    bundle = m.group(2)
    if major == '8':
        m = re.fullmatch(r'8u(\d+)-b\d+', version)
        assert m, version
        minor = m.group(1)
        url = f'https://javadl.oracle.com/webapps/download/GetFile/1.8.0_{version[2:]}/{bundle}/linux-i586/jdk-8u{minor}-linux-x64.tar.gz'

    # find checksum
    m = re.search(fr'<tr><td>{re.escape(filename)}</td><td>(.*?)</td></tr>', checksum_page)
    assert m, checksum_page
    checksum_list = m.group(1)
    m = re.search(r'sha256: ([0-9a-f]{64})', checksum_list)
    assert m, checksum_list
    sha256 = m.group(1)

    # write source.yml
    with open(f'jdk{major}/source.yml', 'w') as f:
        f.write(f'''\
version: {version}
url: {url}
sha256: {sha256}
''')

if __name__ == '__main__':
    main()
