# adstex
Find all citation keys in your LaTeX documents and search NASA ADS to generate corresponding bibtex entries.

# Usage: 

    adstex file1.tex [file2.tex [...]] -o ref.bib

## Package Requirements
- ads >= 0.11.1
- bibtexparser >= 0.6.1

# Notes
You need to setup `ADS_API_TOKEN` in your environment.
Register an account at https://ui.adsabs.harvard.edu/
and obtain your token at https://ui.adsabs.harvard.edu/#user/settings/token


The MIT License (MIT)
Copyright (c) 2015 Yao-Yuan Mao (yymao)

