# multi-saxon
[![DOI](https://zenodo.org/badge/680835550.svg)](https://zenodo.org/badge/latestdoi/680835550)

``multi-saxon`` is a tool designed to rapidly transform vast amounts of XML TEI files to text. By harnessing the capabilities of Saxonica's [SaxonC-HE](https://pypi.org/project/saxonche/) processor (XSLT 2.0+) and leveraging multiprocessing, multi-saxon offers high speed XML transformations `lxml` can only acheive with XSLT 1.0.

## Features

- **Fast Transformations**: Utilize the multiprocessing capabilities of your machine for simultaneous XML transformations.
- **Saxon Integration**: Seamlessly process XML files using the renowned Saxon processor.
- **CSV Output**: Generate comprehensive CSV reports containing relevant metadata about the processed XML TEI files.

## Limitations
- ``multi-saxon`` is optimized for TEI P5 files.
- Limited customization

## Upcoming Features
- A separate config.toml file to increase metadata customization. 

## Installation

1. Ensure you have Python 3.x installed on your machine. If not, [download and install Python](https://www.python.org/downloads/).

2. Clone this repository:
   ```bash
   git clone https://github.com/Pantagrueliste/multi-saxon.git
   ```
