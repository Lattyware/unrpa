import setuptools  # type: ignore

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="unrpa",
    version="2.0.1",
    author="Gareth Latty",
    author_email="gareth@lattyware.co.uk",
    description="Extract files from the RPA archive format (from the Ren'Py Visual Novel Engine).",
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
)
