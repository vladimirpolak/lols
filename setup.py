from setuptools import setup

def read_version(fname="lols/version.py") -> str:
    exec(compile(open(fname, encoding="utf-8").read(), fname, "exec"))
    return locals()["__version__"]

setup(
    name='lols',
    version=read_version(),
    author='Vladimír Polák',
    author_email='vladimirpolak2@gmail.com',
    description='Bulk hosting sites scraper/downloader',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    readme="README.md",
    packages=['lols', 'lols.http', 'lols.scrapers'],
    url='https://github.com/vladimirpolak/lols',
    license='MIT',
    install_requires=[
        'requests',
        'retry',
        'w3lib',
    ],
    entry_points={
        'console_scripts': [
            'lols = lols:main'
        ]
    }
)
