# tenable-downloader
tenable-downloader.py is a menu driven tool for downloading Tenable software.
## Requirements
* Python3
* [Tenable Downloads API Bearer token](https://www.tenable.com/downloads/api-docs)
## Installation
tenable-downloader.py is a dependency free, standalone Python program.
### git
```
$ git clone https://github.com/andrewspearson/tenable-downloader.git
```
### curl
```
$ curl https://raw.githubusercontent.com/andrewspearson/tenable-downloader/main/tenable-downloader.py -O
```

**NOTE:** macOS users running Python 3.6+ will need to [install certificates](https://bugs.python.org/issue28150).

TLDR, run this command:
```
$ /Applications/Python {version}/Install Certificates.command
```
This seems to only be an issue on macOS.
## Usage
tenable-downloader.py may read the bearer token either interactively or through an INI file. If the ```tenable.ini``` file is present and contains a ```bearer_token```, then you will not be prompted to enter a bearer token. If the ```tenable.ini``` file is not present or the ```bearer_token``` is not defined, then you will be prompted to enter a bearer token.

tenable-downloader.py reading bearer token interactively:

tenable-downloader.py reading bearer token through a ```tenable.ini``` file:
