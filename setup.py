import io
import esipysi
from setuptools import setup, find_packages

try:
    with open("README.md", "r") as fh:
        long_description = fh.read()
except:
    long_description = ""

setup(
    name = "EsiPysi",
    version = esipysi.__version__,
    author = "Flying Kiwi",
    author_email = "github@flyingkiwibird.com",
    description = ("A client for ESI, the API for Eve Online"),
    license = "MIT",
    keywords = "Esi Eve Python Api",
    url = "https://github.com/FlyingKiwiBird/EsiPysi",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=[
        "aiohttp",
        "aiodns",
        "requests",
        "redis"
    ],
    long_description_content_type='text/markdown',
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
