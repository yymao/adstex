# adstex
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/adstex.svg)](https://anaconda.org/conda-forge/adstex)
[![PyPI version](https://img.shields.io/pypi/v/adstex.svg)](https://pypi.python.org/pypi/adstex)

Tired of copying and pasting bibtex entries?
Here's a new way to manage your bibtex entries — do not manage them!

`adstex` automatically identifies all citation keys (e.g., identifiers, author+year)
in your TeX source files and use
NASA's [Astrophysics Data System](https://ui.adsabs.harvard.edu/) (ADS)
to generate corresponding bibtex entries!

`adstex` was featured in an ADS blog post "[User-Developed Tools for ADS](http://adsabs.github.io/blog/3rd-party-tools)"!

## Features

- Write your papers without worrying about the bibtex entries.
  Simply put down arXiv IDs, ADS bibcodes, DOIs, or first author & year citation keys
  in your `\cite` commands,
  and then use `adstex` to automatically generate the bibtex file for you.

- `adstex` recognizes all variants of the `\cite` commands,
  and works with various styles of citation keys.
  For example, `adstex` would work with all the following:
  ```tex
  \citet{1705.03888}
  \citep[e.g.,][]{Mao:2015, White2018}
  \citealt{10.1093/mnras/stx3111, 2017arXiv170909665M}
  ```

- `adstex` works along with your existing bibtex files.
  It simply skips (or updates) those citation keys that already have corresponding bibtex entries.

- `adstex` will also update existing bibtex entries for you!
  Citing an arXiv preprint which is now published in a journal?
  No problem, `adstex` will detect this and automatically update the bibtex entry.
  (_This is amazing, yes, I know!_)

- `adstex` also detect citation keys that actually refer to the same paper
  (e.g., you use an author:year citation key but another collaborator uses an
  arxiv ID as key for the same paper),
  and will prompt you to fix these issues.


## Installation and Setup

### Install `adstex`

You can install `adstex` from conda-forge

```bash
conda install adstex --channel conda-forge
```

Or from PyPI

```bash
pip install adstex
```

### Set up an ADS API token

`adstex` requires an API token to use ADS. Here's how to obtain one:

1. Visit [NASA/ADS](https://ui.adsabs.harvard.edu/) to [sign up for an account](https://ui.adsabs.harvard.edu/user/account/register) if you don't have one.

2. Visit the [API Token page](https://ui.adsabs.harvard.edu/user/settings/token), log in with your ADS account and you will see an API token string. Copy that token string.

3. Set your token string to an environment variable named `ADS_API_TOKEN`. You can do that by running:
    ```bash
    # If you use bash or bash-like shells --
    export ADS_API_TOKEN="your token string here"
    ```
    ```csh
    # If you use csh or csh-like shells --
    setenv ADS_API_TOKEN "your token string here"
    ```
    You can put this line into your `~/.bashrc` or `~/.cshrc` file.


## Usage

Once you finish the paper (_sorry, can't help with that!_), simply run `adstex`
with the following command (_Internet connection is needed for `adstex` to work._):

```bash
# Note: if you are using version 0.2.x, please add the -o option. See below.

adstex your_tex_source.tex
```

`adstex` will automatically build the bibtex files, and write to the bibtex
source that you specified in your tex source file.

- If you want to have more control on the output file (or if you are using adstex v0.2.x), use the `-o` option:
  ```bash
  adstex your_tex_source.tex -o your_bib_source.bib
  ```
  Once `adstex` is done, it will write all bibtex entries in the file
  that you specified with the `-o` option.

- You can also provide multiple TeX source files at once:
  ```bash
  adstex your_tex_source1.tex [your_tex_source2.tex [...]] -o your_bib_source.bib
  ```

- For citation keys that are arXiv IDs, ADS bibcodes, or DOIs,
  `adstex` will automatically find the corresponding bibtex entries.

- For first author + year citation keys, `adstex` will search on NASA ADS and
  provide you a list of candidate papers to select from.
  If you don't see the paper you are looking for, you can
  directly enter an ADS bibcode or arXiv ID when prompted.

- You can also find a complete option list by running:
  ```bash
  adstex --help
  ```
  However, you may find the following FAQs more informative.


## FAQs

1. **Can `adstex` recognize citation keys with multiple authors or compound surnames?**

   Not always; `adstex` uses [regular expression](https://en.wikipedia.org/wiki/Regular_expression), not AI.

   For citation keys with multiple authors, if you use a separator to separate
   the surnames, (e.g., `\cite{Press:Schechter:1974}`), the `adstex` will be able to
   identify the first author and year to conduct a search on the ADS.

   For compound surnames, your best bets are
   joining the words without the spaces (e.g., `\cite{deSitter:1913}`), and
   keeping the hyphens (e.g., `\cite{Boylan-Kolchin:1913}`).

   Note that in the event that `adstex` cannot find the correct paper from a
   first author + year citation key, it will prompt you to enter an identifier
   (ADS bibcode, arXiv ID, or DOI) for that key.


2. **I have some other bibtex files, how to ask `adstex` to skip citation keys that already have existing entries in those files?**

   Use the `-r` option to provide additional existing bibtex files.
   `adstex` will read in these files without modifying them
   (only the file specified by `-o` will be modified). Here's an example command:

   ```bash
   adstex main.tex -o main.bib -r software.bib classic.bib
   ```

3. **How do I use `adstex` as a reference manager? Or can I use `adstex` with other reference managers (e.g., JabRef, Mendeley, Zotero)?**

    `adstex` is not a reference manager, and will not be one.
    The philosophy behind `adstex` is to *not* manage the references,
    because NASA's ADS is already doing that for us (and is doing an excellent job)!
    So `adstex` simply generates the bibtex file using the ADS on the fly.

    If you are already using a reference manager, you may want to continue to use it to generate bibtex files. You can then use `adstex` to fetch just the new entries (see FAQ #2).
    You can also use `adstex` to update all existing entries with the latest version from the ADS by running:
    ```bash
    adstex your_bibtex_file.bib
    ```

4. **Does this work with the ADS astronomy database only?**

   For citation keys that are arXiv IDs, ADS bibcodes, or DOIs,
   `adstex` would work with any entry as long as it is in the ADS.

   For first author + year citation keys, by default `adstex` would only
   search the astronomy database on NASA ADS.
   However, you can use `--include-physics` to include the ADS physics database.

   `adstex` only works with the ADS, and hence the name of this program :)

5. **`adstex` seems to run very slowly. Is there any way to speed it up?**

   By default, `adstex` check if existing entries have any updates
   (e.g., arXiv preprint becoming a journal paper), and this process may slow
   down the execution.
   You can use `--no-update` to turn this feature off,
   so that `adstex` will only look for new entries.

   In addition, you can turn on parallel execution by adding the `--parallel`
   option. You can further specify the number of threads it uses with
   `--parallel=x` (default is 8).

6. **I have different citation keys that point to the same paper in my tex file,
   can `adstex` merge and remove the repetitions?**

   `adstex` will warn you (near the end of its execution) if it detects multiple
   keys that point to the same paper. It will list all those citation keys, but
   it will *not* merge them automatically. `adstex` never edits the tex source files;
   hence, you need to update the citation keys in the tex source files manually.

7. **Is there a way to use `adstex` with Overleaf?**

   If you or your institution has an Overleaf subscription, you can use Overleaf's
   git or Dropbox integration to fetch the source files to your local machine,
   run `adstex` locally, and then push back to Overleaf via git
   (in the case of Dropbox, no pushing needed).

   If you don't have access to Overleaf's premium features, you can still just
   download the tex source file and bib file, run `adstex` locally, and then upload
   the updated bib file back to Overleaf (tex source file will not be changed by `adstex`).

8. **I got a `SSLCertVerificationError`! How to fix it?**

   This error usually happens when the ADS SSL certification has been updated,
   but your local SSL certification has not yet. The error should go away once the
   local certification is updated too.

   With `adstex` 0.4.0+, you can use the `--disable-ssl-verification` option to
   temporarily disable the verification of SSL certification. This option can be
   handy if you don't have control of your local SSL certification installation.
   Note that with this option, your ADS API key may be vulnerable to a
   man-in-the-middle attack. You can generate new ADS API key on
   [ADS website](https://ui.adsabs.harvard.edu/user/settings/token) if you think
   your API key may have been compromise.

9. **`adstex` saves me so much time. How do I acknowledge it?**

   First of all, thank you :)

   `adstex` won't exist without NASA's ADS, so please do acknowledge them by
   adding the following to your acknowledgements section:
   ```tex
   This research has made use of NASA's Astrophysics Data System.
   ```
   (_Note: `adstex` is not affiliated with nor endorsed by NASA's ADS._)

   Then, if you would like to also acknowledge `adstex`, you can add
   the following to your acknowledgements section:
   ```tex
   This research has made use of adstex (\url{https://github.com/yymao/adstex}).
   ```
