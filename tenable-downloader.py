#!/usr/bin/env python3
import configparser
from getpass import getpass
import os
import ssl
import urllib.request
from urllib.error import HTTPError
import json
import shutil
import hashlib


# Begin: code from https://github.com/andrewspearson/tenable_light
config = configparser.ConfigParser()
config.read('tenable.ini')


def request(method, host, endpoint, url=None, headers=None, data=None, proxy=None, verify=True):
    # url should only be used by the Downloads class
    if url is None:
        request_ = urllib.request.Request('https://' + host + endpoint)
    else:
        request_ = urllib.request.Request(url)
    request_.method = method
    request_.add_header('accept', 'application/json')
    request_.add_header('content-type', 'application/json')
    context = ''
    if headers:
        for key, value in headers.items():
            request_.add_header(key, value)
    if data:
        request_.data = json.dumps(data).encode()
    if proxy:
        request_.set_proxy(proxy, 'https')
    if verify is False:
        # https://www.python.org/dev/peps/pep-0476
        context = ssl._create_unverified_context()
    try:
        response = urllib.request.urlopen(request_, context=context)
        return response
    except HTTPError as error:
        print('\nERROR: HTTP ' + str(error.code))
        print(error.reason)


def auth_error(msg='ERROR: Invalid authentication data'):
    print(msg)
    quit()


class Downloads:
    def __init__(self, bearer_token=None, proxy=None, verify=True):
        # Set connection data in order of preference
        self.host = 'www.tenable.com'
        self.bearer_token = bearer_token
        self.proxy = proxy
        self.verify = verify
        if self.bearer_token:
            pass
        elif config.has_option('downloads', 'bearer_token'):
            self.bearer_token = config.get('downloads', 'bearer_token')
            if config.has_option('downloads', 'proxy'):
                self.proxy = config.get('downloads', 'proxy')
            else:
                self.proxy = None
            if config.has_option('downloads', 'verify'):
                self.verify = config.getboolean('downloads', 'verify')
            else:
                self.verify = True
        else:
            auth_error()

        # Create authentication headers
        self.headers = {
            "Host": "www.tenable.com",
            "User-agent": "Mozilla/5.0",
            "Authorization": "Bearer " + self.bearer_token
        }

    def request(self, url):
        # url is used for Downloads in order to easily work with the files_index_url, and file_url values
        response = request('GET', None, None, url, self.headers, None, self.proxy, self.verify)
        return response
# End: code from https://github.com/andrewspearson/tenable_light


def menu(data):
    os.system('clear')
    if type(data) is dict:
        menu_ = dict((index, key) for index, key in enumerate(data))
        for index, key in menu_.items():
            print(str(index) + '. ' + key)
        selection = prompt(range(len(data)))
        data = data[menu_[selection]]
        return data
    if type(data) is list:
        if 'file_url' in data[0]:
            for index, key in enumerate(data):
                print(str(index) + '. ' + str(key['file']))
            selection = prompt(range(len(data)))
            file_ = data[selection]
            return file_
        else:
            for index, key in enumerate(data):
                print(str(index) + '. ' + str(key['title']))
            selection = prompt(range(len(data)))
            page_ = data[selection]
            return page_
    else:
        print('ERROR: Unknown data')


def prompt(selections):
    error_msg = 'Invalid entry'
    while True:
        try:
            selection = int(input('Enter number: '))
        except ValueError:
            print(error_msg)
            continue
        if selection not in selections:
            print(error_msg)
            continue
        else:
            break
    return selection


def file_verify(file, hash_func, digest):
    with open(file, 'rb') as file:
        if hash_func == 'sha256':
            hash_obj = hashlib.sha256()
        elif hash_func == 'md5':
            hash_obj = hashlib.md5()
        else:
            print('ERROR: Invalid hash function')
        for chunk in iter(lambda: file.read(128*hash_obj.block_size), b''):
            hash_obj.update(chunk)
        return hash_obj.hexdigest() == digest


# Get bearer token and create a Downloads client
if config.has_option('downloads', 'bearer_token'):
    downloads = Downloads()
else:
    auth = getpass(prompt='Enter Tenable downloads bearer token ID: ')
    downloads = Downloads(auth)

# Get download pages
pages = json.load(downloads.request('https://www.tenable.com/downloads/api/v2/pages'))
page = menu(pages)

# Get download files
files = json.load(downloads.request(page['files_index_url']))
while 'file_url' not in files:
    files = menu(files)

# Download file
print('\nDownloading ' + files['file'] + '...')
download = downloads.request(files['file_url'])
file_name = files['file']
with download as response, open(file_name, 'wb') as file:
    shutil.copyfileobj(response, file)

# Verify download
hash_func = ''
print('Verifying file hash...')
if 'sha256' in files:
    hash_func = 'sha256'
elif 'md5' in files:
    print('SHA256 hash not available')
    hash_func = 'md5'
if hash_func:
    if file_verify(file_name, hash_func, files[hash_func]):
        print(hash_func.upper() + ' hash verified')
    else:
        print('ERROR: ' + hash_func.upper() + ' hash verification failed')
        os.remove(file_name)
        print('Deleted file due to failed hash verification')
else:
    print('No hashes available\nVerification skipped')
