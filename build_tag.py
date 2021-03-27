import platform, sys

py = {'CPython': 'cp', 'PyPy': 'pp'}[platform.python_implementation()]
print(f'{py}{sys.version_info.major}{sys.version_info.minor}')
