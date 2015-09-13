"""
Find all citation keys in your LaTeX documents and search NASA ADS 
to generate corresponding bibtex entries. 

Project website: https://github.com/yymao/adstex

The MIT License (MIT)
Copyright (c) 2015 Yao-Yuan Mao (yymao)
http://opensource.org/licenses/MIT
"""

from setuptools import setup

setup(
    name='adstex',
    version='0.1.0',
    description='Find all citation keys in your LaTeX documents and search NASA ADS to generate corresponding bibtex entries.',
    url='https://github.com/yymao/adstex',
    author='Yao-Yuan Mao',
    author_email='yymao@alumni.stanford.edu',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Scientific/Engineering :: Astronomy',
    ],
    use_2to3=True,
    keywords='bibtex ads',
    packages=['adstex'],
    install_requires=['ads>=0.11.1','bibtexparser>=0.6.1'],
    entry_points={
        'console_scripts': [
            'adstex=adstex:main',
        ],
    },
)
