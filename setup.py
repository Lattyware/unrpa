import setuptools  # type: ignore
from unrpa import meta

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name=meta.name,
    version=meta.version,
    author="Gareth Latty",
    author_email="gareth@lattyware.co.uk",
    description=meta.description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lattyware/unrpa",
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    keywords="renpy rpa archive extract",
    classifiers=[
        "Topic :: System :: Archiving",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    entry_points={"console_scripts": ["unrpa = unrpa.__main__:main"]},
    extras_require={"ZiX": "uncompyle6>=3.5.0"},
)
