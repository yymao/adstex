# adstex
[![PyPI version](https://img.shields.io/pypi/v/adstex.svg)](https://pypi.python.org/pypi/adstex)

Find all citation keys in your LaTeX documents and search NASA ADS to generate corresponding bibtex entries.

## Installation

    pip install adstex

or, if you want to use the latest version.

    pip install git+git://github.com/yymao/adstex.git

## Usage

    adstex file1.tex [file2.tex [...]] -o references.bib

### Obtain an ADS API token
Follow the steps below to obtain an ADS API token:

1. Visit the [ADS beta website](https://ui.adsabs.harvard.edu/) to [register an account](https://ui.adsabs.harvard.edu/#user/account/register) if you don't have one.

2. [Visit this page](https://ui.adsabs.harvard.edu/#user/settings/token), log in with your ADS beta account and you will see a token string. Copy that token string.

3. Set your token string to an environment variable named `ADS_API_TOKEN`. You can do that by running:
     ``` bash
     # If you use bash --
     export ADS_API_TOKEN="your token string here"
     ```
     ``` csh
     # If you use csh --
     setenv ADS_API_TOKEN "your token string here"
     ```
    You can put this line into your `~/.bashrc` or `~/.cshrc` file.
