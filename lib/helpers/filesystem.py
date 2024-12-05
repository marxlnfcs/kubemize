import os
import shutil
import typing
import uuid
from pathlib import Path

from wcmatch import glob

from lib.helpers.object import flatten_array


def create_random_id(length=8):
    return uuid.uuid4().hex[:length]


def file_exists(path: str, cwd: str = None) -> bool:
    return os.path.isfile(resolve_path(path, cwd=cwd))


def dir_exists(path: str) -> bool:
    return os.path.isdir(resolve_path(path))


def read_file(path: str) -> str:
    return read_file_as_binary(path).decode('utf-8')


def read_file_as_binary(path: str) -> bytes:
    with open(resolve_path(path), 'rb') as f:
        return f.read()


def write_file(path: str, content: str or bytes, cwd: str = None) -> None:
    create_parent_of_file(path, cwd=cwd)
    mode = 'wb' if isinstance(content, bytes) else 'w'
    with open(resolve_path(path, cwd=cwd), mode) as f:
        f.write(content)


def join_path(base: str, *paths: str) -> str:
    return to_unix_path(os.path.join(base, *paths))


def resolve_path(*paths: str) -> str:
    return to_unix_path(os.path.abspath(join_path(*paths)))


def to_unix_path(path: str) -> str:
    return os.path.abspath(path).replace('\\', '/')


def is_absolute_path(path: str) -> bool:
    return os.path.isabs(path)


def get_base_name(path: str) -> str:
    return os.path.basename(path)


def delete_dir(path: str) -> None:
    if dir_exists(path):
        shutil.rmtree(path)


def delete_file(path: str, cwd: str = None) -> None:
    if file_exists(path, cwd=cwd):
        os.remove(path)


def get_dir_content(path: str) -> list:
    if dir_exists(path):
        return os.listdir(resolve_path(path))
    return []


def resolve_path(path: str, cwd: str = None) -> str:
    return to_unix_path(os.path.join(cwd, path) if cwd and not is_absolute_path(path) else path)

def resolve_paths(paths: str or list, cwd: str = None) -> list:
    items = []
    patterns = []
    cwd = cwd if cwd else os.getcwd()
    for pattern in ([paths] if isinstance(paths, str) else paths):
        patterns.append(pattern.strip().lstrip("./") if not pattern.startswith('../') else pattern)
    for item in glob.glob(patterns, root_dir=cwd, flags=glob.BRACE | glob.GLOBSTAR | glob.NEGATE | glob.IGNORECASE | glob.DOTGLOB | glob.MATCHBASE | glob.GLOBTILDE):
        items.append(resolve_path(item, cwd))
    return items

def resolve_files(paths: str or list, cwd: str = None) -> list:
    files = []
    for item in resolve_paths(paths, cwd):
        if os.path.isfile(item):
            files.append(item)
    return files

def resolve_dirs(paths: str or list, cwd: str = None) -> list:
    dirs = []
    for item in resolve_paths(paths, cwd):
        if os.path.isdir(item):
            dirs.append(item)
    return dirs

def path_contains_filename(path: str, *filenames: str or typing.List[str]) -> bool:
    for name in flatten_array(*filenames):
        if Path(path).name.strip().lower() == name.strip().lower():
            return True
    return False

def create_dir(path: str, cwd: str = None) -> str:
    path = resolve_path(path, cwd)
    if not dir_exists(path):
        os.makedirs(path, exist_ok=True)
    return path

def create_parent_of_file(path: str, cwd: str = None) -> None:
    full_path = resolve_path(path, cwd)
    dir_path = os.path.dirname(full_path)

    if not dir_exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

def get_extension(path: str, cwd: str = None) -> str or None:
    return os.path.splitext(resolve_path(path, cwd=cwd))[1] or None

def get_dirname(path: str, cwd: str = None) -> str:
    return os.path.dirname(resolve_path(path, cwd=cwd))

def get_basename(path: str, cwd: str = None) -> str:
    return os.path.basename(resolve_path(path, cwd=cwd))

def randomize_file_name(path: str, cwd: str = None) -> str:
    parts = resolve_path(to_unix_path(path), cwd=cwd).split('/')
    base_name = get_base_name(path)

    bn_parts = base_name.split('.')
    random_id = create_random_id(8)

    if len(bn_parts) > 1:
        new_name = f"{bn_parts[0]}-{random_id}.{'.'.join(bn_parts[1:])}"
    else:
        new_name = f"{bn_parts[0]}-{random_id}" if bn_parts[0] else random_id

    parts[-1] = new_name
    return join_path(*parts)
