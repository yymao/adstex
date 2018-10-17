# adstex
[![PyPI version](https://img.shields.io/pypi/v/adstex.svg)](https://pypi.python.org/pypi/adstex)

Find all citation keys in your LaTeX documents and search NASA ADS to generate corresponding bibtex entries.

## Installation

    pip install adstex

Or, if you want to use the version in the master branch (not recommended):

    pip install https://github.com/yymao/adstex/archive/master.zip

## Usage

_Note: You need to first obtain an ADS API token. See instructions at the bottom of this README._

```bash
adstex file1.tex [file2.tex [...]] -o references_output.bib [-r references_readonly.bib]
```

In your tex files, you can cite paper using arXiv IDs, ADS bibcodes, DOIs, and first author + year, with any `natbib` commands. Here's some examples:

```tex
\citep{1705.03888}
\citet{Mao2017}
\citep[e.g.,]{Mao:2015, White:2018}
\citealt{10.1093/mnras/stx3111, 2017arXiv170909665M}
```

For first author + year citations, `adstex` will prompt you to select the paper you are looking for. You can also directly enter an ADS bibcode if you don't see the correct paper when prompted.

To see a complete option list, run:
```bash
adstex --help
```

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
