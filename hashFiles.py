#!/usr/bin/env python3
import glob
import hashlib
import pathlib
import re
import sys

dgst = hashlib.sha256()
for line in sys.stdin:
    # ignore comment line
    if line.startswith('#'):
        continue

    pattern = line.rstrip('\n')

    # ignore empty line
    if not pattern:
        continue

    for _path in sorted(glob.glob(pattern, recursive=True)):
        dgst.update(_path.encode())
        path = pathlib.Path(_path)
        if path.is_symlink():
            dgst.update(os.readlink(path).encode())
        elif path.is_file():
            data = path.read_bytes()
            if _path.startswith('.github/workflows/'):
                # ignore parts of workflow yaml
                data = re.sub(br'(?ms)^# DONT-CHECKSUM-BEGIN\n.*?^# DONT-CHECKSUM-END\n', b'', data)
            dgst.update(data)
        elif path.is_dir():
            pass
        else:
            raise NotImplementedError('cannot hash special file type')

print(dgst.hexdigest())
