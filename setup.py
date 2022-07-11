"""Python setup.py for mock_github package"""
import io
import os
from setuptools import find_packages, setup


def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("mock_github", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """

    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="mock_github",
    version=read("mock_github", "VERSION"),
    description="Awesome mock_github created by blink1073",
    url="https://github.com/blink1073/mock_github/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="blink1073",
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": ["mock_github = mock_github.__main__:main"]
    },
    extras_require={"test": read_requirements("requirements-test.txt")},
)
