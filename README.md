# Clustering Mask

This repository contains the clustering mask python app that takes an excel exported QGIS file and returns a clustered excel file that can be imported into QGIS.
## Table of Contents

- [Requirements](#requirements)
- [Usage](#usage)

## Requirements

- Python3
- Add Python3 to your windows PATH: [here](https://www.geeksforgeeks.org/how-to-add-python-to-windows-path/)

Note: both of these are usually there, so before doing anything, first check if `python3` is already part of the powershell command. Open a Powershell instance and check if you see the version of the python installed by running the following command:
```powershell
python3 --version
```
## Usage

1. Check the `.env` file and properly set the `THRESHOLD` and `COL`:
    - set `THRESHOLD` to the proper threshold.
    - set `COL` to the number of columns in each row of the raster.
2. Run the program with the following command, replace the file path:
```powershell
python3 main.py path/to/the/file
```
3. Result will be in the `output` folder with the same name of the input file.
