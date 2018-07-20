import os
import setuptools

os.system('cd readme; mdoc -i README.mdoc -o ../README.md -v vars.json')

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mdoc",
    version="0.0.8",
    author="Eric Shapiro",
    author_email="eshapiro42@gmail.com",
    description="Modular documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data = True,
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
