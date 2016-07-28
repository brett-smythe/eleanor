"""Setuptools for eleanor service"""
from setuptools import setup, find_packages

reqs = []

with open('requirements.txt') as inf:
    for line in inf:
        line = line.strip()
        reqs.append(line)


setup(
    name='eleanor',
    version='0.4',
    description='API for accumulated social data',
    author='Brett Smythe',
    author_email='smythebrett@gmail.com',
    maintainer='Brett Smythe',
    maintainer_email='smythebrett@gmail.com',
    packages=find_packages(),
    install_reqs=reqs,
    entry_points={
        'console_scripts': [
            'eleanor=eleanor.main:main'
        ]
    }
)
