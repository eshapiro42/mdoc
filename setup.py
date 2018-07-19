import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mdoc",
    version="0.0.6",
    author="Eric Shapiro",
    author_email="eshapiro42@gmail.com",
    description="Modular documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eshapiro42/mdoc",
    packages=setuptools.find_packages(),
    install_requires=['pathlib'],
    entry_points = {'console_scripts': ['mdoc = mdoc:console']},
    classifiers=(
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)
