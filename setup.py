import textwrap
from pathlib import Path

from setuptools import find_packages, setup

__version__ = "0.31.2"

# read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="flask-rest-jsonapi-next",
    version=__version__,
    description=textwrap.dedent(
        """
        Flask extension to create REST web api according to JSONAPI 1.0 specification
        with Flask, Marshmallow and data provider of your choice (SQLAlchemy, MongoDB,
        ...)
        """
    ),
    long_description=long_description,
    long_description_content_type = "text/markdown",
    url="https://github.com/tadams42/flask-rest-jsonapi-next",
    author="Tomislav Adamic",
    author_email="tomislav.adamic@gmail.com",
    license="MIT",
    classifiers=[
        "Framework :: Flask",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="web api rest jsonapi flask sqlalchemy marshmallow",
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    platforms="any",
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=[
        "six",
        "Flask",
        "marshmallow",
        "marshmallow_jsonapi",
        "sqlalchemy",
    ],
    setup_requires=[
        "pytest-runner",
    ],
    tests_require=[
        "pytest",
    ],
    extras_require={
        "dev": [
            "pytest",
            "coveralls",
            "coverage",
            "ipython",
            "black",
            "isort",
            "bump2version",
        ],
        "docs": [
            "sphinx",
            "sphinx_rtd_theme",
        ],
    },
)
