# multi-saxon
[![DOI](https://zenodo.org/badge/680835550.svg)](https://zenodo.org/badge/latestdoi/680835550)

``multi-saxon`` swiftly converts large amounts of XML TEI files into text. Harnessing the power of Saxonica's [SaxonC-HE](https://pypi.org/project/saxonche/) processor (XSLT 2.0+), it parallelizes file processing. This approach enables users to circumvent some of the limitations of ``lxml``, which operates exclusively within the XSLT 1.0.


## Features

- **Fast Transformations**: Utilize the multiprocessing capabilities of your machine for simultaneous XML transformations.
- **Saxon Integration**: Seamlessly process XML files using the renowned Saxon processor.
- **CSV Output**: Generate comprehensive CSV reports containing relevant metadata about the processed XML TEI files.

## Limitations
- ``multi-saxon`` is optimized for TEI P5 files.
- Limited customization (for now).

## Upcoming Features
- A separate config.toml file to increase metadata customization.

## Installation

1. Ensure you have Python 3.x installed on your machine. If not, [download and install Python](https://www.python.org/downloads/).

2. Clone this repository:
   ```bash
   git clone https://github.com/Pantagrueliste/multi-saxon.git
   ```
