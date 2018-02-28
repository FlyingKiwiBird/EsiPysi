import io
import esipysi
from setuptools import setup

with io.open("requirements.txt") as reader:
    install_requirements = [line.strip("\n") for line in reader]

with io.open('readme.md') as reader:
    readme = reader.read()



setup(
    name = "EsiPysi",
    version = esipysi.__version__,
    author = "Flying Kiwi",
    author_email = "github@flyingkiwibird.com",
    description = ("A client for ESI, the API for Eve Online"),
    license = "MIT",
    keywords = "Esi Eve Python Api",
    url = "https://github.com/FlyingKiwiBird/EsiPysi",
    packages=['esipysi'],
    install_requires=install_requirements,
    long_description=readme,
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
