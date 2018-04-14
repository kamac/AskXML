from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='askxml',
    version='1.0.0',
    description='Run SQL statements on XML documents',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kamac/AskXML',
    author='Maciej Kozik',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Markup :: XML',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='xml sql statements query',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
)