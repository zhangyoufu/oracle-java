#!/usr/bin/env python
import os
import yaml
import sys

def escape_message(s):
    return s.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')

def escape_property(s):
    return s.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A').replace(':', '%3A').replace(',', '%2C')

def issue(command, message, **properties):
    if properties:
        escaped_properties = ','.join(
            f'{k}={escape_property(v)}'
            for k, v in properties.items()
        )
        print(f'::{command} {escaped_properties}::{escape_message(message)}')
    else:
        print(f'::{command}::{escape_message(message)}')

def set_env(name, value):
    issue('set-env', value, name=name)

def main():
    major = int(os.environ['MAJOR'])
    for name, value in yaml.safe_load(open(f'jdk{major}/source.yml')).items():
        assert isinstance(value, str)
        set_env(name.upper(), value)
        if name == 'url':
            set_env('FILENAME', value.rsplit('/', 1)[-1])

if __name__ == '__main__':
    main()
