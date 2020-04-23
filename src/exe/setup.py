from setuptools import find_packages
from cx_Freeze import setup, Executable


options = {
    'build_exe': {
        'includes': [
            'cx_Logging', 'idna',
        ],
        'packages': [
            'asyncio', 'flask', 'jinja2', 'dash', 'plotly', 'waitress'
        ],
        'excludes': ['tkinter']
    }
}

executables = [
    Executable('server.py',
               base='console',
               targetName='FunViz')
]

setup(
    name='FunViz',
    packages=find_packages(),
    version='0.4.0',
    description='Fundamentals Visualizer',
    executables=executables,
    options=options
)