#!/usr/bin/env python
import email.utils
import logging
import os
import pathlib
import subprocess
import sys
import yaml

maintainer = os.environ['MAINTAINER']
major = int(os.environ['MAJOR'])
version = os.environ['VERSION']
revision = int(os.environ['REVISION'])
changelog = 'upstream release' if revision == 1 else 'improve packaging'
with open(f'jdk{major}/package.yml') as f:
    d = yaml.safe_load(f)
    priority = d['priority']
    jinfo_ignore = frozenset(d.get('jinfo-ignore') or [])
    packages = d['packages']
    del d

arch = 'amd64'
package_name_prefix = f'oracle-java-{major}'
jvm_name = f'oracle-java-{major}-{arch}'
jvm_prefix = pathlib.Path('usr/lib/jvm')
jvm = jvm_prefix / jvm_name
jinfo_path = pathlib.Path(f'debian/{package_name_prefix}-jre-headless/{jvm_prefix}/.{jvm_name}.jinfo')
cacerts = 'jre/lib/security/cacerts' if major == 8 else 'lib/security/cacerts'
src = pathlib.Path('debian/tmp')

def find(cmd):
    text = subprocess.check_output(cmd, cwd=src, shell=True, text=True).strip('\0')
    if not text:
        return []
    return text.split('\0')

def prepare():
    global executables
    global empty_directories

    ## rename cacerts
    (src/cacerts).rename(src/f'{cacerts}.oracle')

    ## find all executables
    executables = set(find(r'find . -type f -perm /111 -printf "%P\0" | sort -z'))

    ## find all empty directories
    empty_directories = set(find(r'find . -type d -empty -printf "%P\0" | sort -z'))

    ## generate debian/control
    with open('debian/control', 'w') as control:
        control.write(f'''\
Source: {package_name_prefix}
Section: java
Priority: optional
Maintainer: {maintainer}
Build-Depends: debhelper (>= 9)
''')
        for package_name in packages:
            with open(f'debian/{package_name}.control') as package_control:
                data = package_control.read().replace('%prefix%', package_name_prefix)
            control.write(f'''\

Package: {package_name_prefix}-{package_name}
{data}''')

    ## generate debian/changelog
    pathlib.Path('debian/changelog').write_text(f'''\
{package_name_prefix} ({version}-{revision}) unstable; urgency=low

  * {changelog}

 -- {maintainer}  {email.utils.formatdate()}
''')

    ## generate jinfo header
    jinfo_path.parent.mkdir(mode=0o755, parents=True)
    jinfo_path.write_text(f'''\
name={package_name_prefix}
priority={priority}

''')

def move(src, dst):
    assert not dst.exists()
    dst.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    src.rename(dst)

def process(package_name, meta):
    dst = pathlib.Path(f'debian/{package_name_prefix}-{package_name}/{jvm}')

    for path in meta.get('files') or []:
        src_path = src/path
        if path.endswith('/'):
            assert src_path.is_dir()
        else:
            assert src_path.is_file() or src_path.is_symlink()
        move(src_path, dst/path)

    purge = set()
    for path in empty_directories:
        if (dst/path).is_dir():
            purge.add(path)
    empty_directories.difference_update(purge)

    substvars(package_name=package_name, meta=meta)

    if package_name == 'cacerts':
        path = pathlib.Path(f'debian/{package_name_prefix}-cacerts.postinst')
        path.write_text(f'''\
#!/bin/sh
set -e

case "$1" in
	configure)
		update-ca-certificates
		update-alternatives --install /{jvm}/{cacerts} {package_name_prefix}-cacerts /{jvm}/{cacerts}.system 20
	;;
esac
''')
        path.chmod(0o755)

        path = pathlib.Path(f'debian/{package_name_prefix}-cacerts.prerm')
        path.write_text(f'''\
#/bin/sh
set -e

case "$1" in
    remove|deconfigure)
        update-alternatives --remove {package_name_prefix}-cacerts /{jvm}/{cacerts}.system
        rm /{jvm}/{cacerts}.system
    ;;
esac
''')
        path.chmod(0o755)

        path = pathlib.Path('debian/{package_name_prefix}-cacerts/etc/ca-certificates/update.d')
        path.mkdir(mode=0o755, parents=True)
        path /= f'{package_name_prefix}-cacerts'
        path.write_text(f'''\
#!/bin/sh
exec trust extract --overwrite --format=java-cacerts --filter=ca-anchors --purpose server-auth /{jvm}/{cacerts}.system
''')
        path.chmod(0o755)
    else:
        pkg_exe = set()
        for path in executables:
            dst_path = dst/path
            if not dst_path.exists():
                continue
            pkg_exe.add(path)
            name = pathlib.Path(path).name

            path = f'man/man1/{name}.1'
            src_path = src/path
            if src_path.exists():
                move(src_path, dst/path)
        pkg_exe -= jinfo_ignore
        executables.difference_update(pkg_exe)
        if pkg_exe:
            jinfo(package_name=package_name, exe=pkg_exe)
            pkg_exe_list = '\n'.join(pkg_exe)

            path = pathlib.Path(f'debian/{package_name_prefix}-{package_name}.postinst')
            with open(path, 'w') as postinst:
                postinst.write(f'''\
#!/bin/sh
set -e

jvm=/{jvm}
priority={priority}
executables='
{pkg_exe_list}
'

case "$1" in
    configure)
        for relpath in ${{executables}}; do
            name=$(basename "${{relpath}}")
            path=${{jvm}}/${{relpath}}
            link=/usr/bin/${{name}}
            slave_name=${{name}}.1.gz
            slave_path=${{jvm}}/man/man1/${{slave_name}}
            slave_link=/usr/share/man/man1/${{slave_name}}
            if [ -e "${{slave_path}}" ]; then
                update-alternatives --install "${{link}}" "${{name}}" "${{path}}" "${{priority}}" --slave "${{slave_link}}" "${{slave_name}}" "${{slave_path}}"
            else
                update-alternatives --install "${{link}}" "${{name}}" "${{path}}" "${{priority}}"
            fi
        done
''')
                if package_name == 'jre-headless':
                    postinst.write(f'''
        update-alternatives --install "${{jvm}}/{cacerts}" {package_name_prefix}-cacerts "${{jvm}}/{cacerts}.oracle" 10
''')
                postinst.write('''
    ;;
esac
''')
            path.chmod(0o755)

            path = pathlib.Path(f'debian/{package_name_prefix}-{package_name}.prerm')
            with open(path, 'w') as prerm:
                prerm.write(f'''\
#!/bin/sh
set -e

jvm=/{jvm}
executables='
{pkg_exe_list}
'

case "$1" in
    remove|deconfigure)
        for relpath in ${{executables}}; do
            name=$(basename "${{relpath}}")
            update-alternatives --remove "${{name}}" "${{jvm}}/${{relpath}}"
        done
''')
                if package_name == 'jre-headless':
                    prerm.write(f'''\
        update-alternatives --remove {package_name_prefix}-cacerts "${{jvm}}/{cacerts}.oracle"
''')
                prerm.write(f'''\
    ;;
esac
''')
            path.chmod(0o755)

jinfo_names = set()

def jinfo(package_name, exe):
    if package_name.endswith('-headless'):
        abbr = f'{package_name[:-9]}hl'
        if abbr == 'jrehl':
            abbr = 'hl'
    else:
        abbr = package_name

    for path in exe:
        name = pathlib.Path(path).name
        if name in jinfo_names:
            logging.warning(f'jinfo: duplicate entry, skipped {path}')
            continue
        jinfo_names.add(name)
        with open(jinfo_path, 'a') as jinfo:
            jinfo.write(f'{abbr} {name} /{jvm}/{path}\n')

def substvars(package_name, meta):
    depends = meta.get('depends') or []
    recommends = meta.get('recommends') or []
    suggests = meta.get('suggests') or []
    provides = meta.get('provides') or []

    with open(f'debian/{package_name_prefix}-{package_name}.substvars', 'a') as substvars:
        substvars.write(f'''\
{package_name}:Depends={', '.join(depends)}
{package_name}:Recommends={', '.join(recommends)}
{package_name}:Suggests={', '.join(suggests)}
{package_name}:Provides={', '.join(provides)}
'''.replace('%prefix%', package_name_prefix))

def check_missing():
    file_left = find(r'find . ! -type d -printf "%P\0" | sort -z')
    for path in file_left:
        logging.error(f'missing: {path}')
    for path in empty_directories:
        logging.error(f'missing: {path}')
    if file_left or empty_directories:
        sys.exit(1)

def main():
    logging.basicConfig(
        stream=sys.stderr,
        level='INFO',
        format='[%(levelname)s] %(message)s',
    )
    prepare()
    logging.info('processing packages...')
    for package_name, meta in packages.items():
        if meta is None:
            meta = {}
        process(package_name=package_name, meta=meta)
    check_missing()

if __name__ == '__main__':
    main()
