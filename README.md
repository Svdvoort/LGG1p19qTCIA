# LGG1p19qTCIA
Code used to process 1p19q data from TCIA and upload to XNAT

Original database:
https://wiki.cancerimagingarchive.net/display/Public/LGG-1p19qDeletion#faf546a6676c45ccb6ef408562f39790

# How-To

## Set-up
This code has been made and run under Python 2.7.12. 
A virtual environment has been used to ensure that no 'contimination' of packages occured. 
The package list is availble in requirements.txt
Running 'pip install -r requirements.txt' sets up all the required packages.

## Get Data
Currently it is not yet possible to get the data automatically.
Go to the [TCIA database](https://wiki.cancerimagingarchive.net/display/Public/LGG-1p19qDeletion#faf546a6676c45ccb6ef408562f39790). 

The current software works with Version 1, Updated on 2017/09/30 of the database.

Create a folder to store all your data, this is hereafter referred to as the 'Data folder'

On the TCIA website download the Images, this will give you a .jlnp file with the NBIA download manager. It asks to 'Select Directory For Downloaded Files', here put the data folder you created earlier.
Download the Segmentations (.zip) and the 1p19q Status and Histologica Type (.xlsx) and put them both in the data folder. You do not need to extract the .zip. 

From here on the scripts can do the work automatically to clean up the database.

## Configuration

Configuration for the files is specified in config.yaml
