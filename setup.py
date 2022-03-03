import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    required = f.read().splitlines()

setuptools.setup(
    name = "autotor",
    version = "1.0.0",
    author = "Salvador Belenguer",
    description = "AutoTor is a simple package to make requests through Tor. "
        "It allows automation, easy Tor circuit renewal and customisation of "
        "the requests.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/salvaba94/AutoTor",
    python_requires = ">=3.7",
    install_requires = required,
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where = "src"),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ]
)