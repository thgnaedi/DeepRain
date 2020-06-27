## Envs

The .yml files can be used to create anaconda environments with all neccessary packages for this Project.
To use the environments you need anaconda and run the command: ```conda env create --file envname.yml```

### collectData.yml
Environment for downloading/extracting DWD Data and to convert them into images.

### wradlib.yml
Environment for converting DWD binarys to Images
* if wradlib installation is not working via conda, try steps shown [in wradlib doc](https://docs.wradlib.org/en/stable/installation.html) for me Step "Bleeding edge code" worked
