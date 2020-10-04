#!/usr/bin/env python
import os
import yaml
import sys

def set_env(name, value):
    delimiter = '_GitHubActionsFileCommandDelimeter_'
    with open(os.environ['GITHUB_ENV'], 'a') as f:
        f.write(f'{name}<<{delimiter}\n{value}\n{delimiter}\n')

def main():
    major = int(os.environ['MAJOR'])
    for name, value in yaml.safe_load(open(f'jdk{major}/source.yml')).items():
        assert isinstance(value, str)
        set_env(name.upper(), value)
        if name == 'url':
            set_env('FILENAME', value.rsplit('/', 1)[-1])

if __name__ == '__main__':
    main()
