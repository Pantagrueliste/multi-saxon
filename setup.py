from setuptools import setup, find_packages

setup(
    name="multi_saxon",
    version="0.2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "saxonche",
        "tqdm",
        "toml",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "multi-saxon=multi_saxon.cli.main:cli",
        ],
    },
    python_requires=">=3.7",
    author="Clément Godbarge",
    author_email="your.email@example.com",
    description="Parallel XML TEI to text transformation tool using Saxon",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Pantagrueliste/multi-saxon",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)