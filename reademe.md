# Chin Lab Lithium-Cesium Codebase

This is the primary repository for the Chinlab Lithium-Cesium codebase, created in July 2024 by merging a bunch of smaller repositories because it was getting too annoying to keep everything synced. 

## Installation

To use this code base, you will need to have git and MATLAB installed on your machine. Then you'll want to clone this repository into the `Documents/MATLAB` directory on your machine. 

You then need to add two additional `.m` files in your MATLAB directory, which are not stored in git because they're machine specific. These are: `localpath.m` and `startup.m`. I'm including templates for these files in the `example_files` subdirectory, but they'll need to be filled in with the correct paths for your machine. `startup.m` is run when you open MATLAB, and lets you add extra folders to your MATLAB path (in this case, `lics-codebase` and its subfolders). `localpath.m` tells the image loading functions where to look for the images stored on your machine. We'll get to that next.

In order to automatically download and process images from the experiment, you'll need to download the Box desktop client, and have the `CHIN_LICS` folder shared with you. The NAS automatically uploads to a subfolder of that Box folder, and so you can get data automatically through it. Then you'll need to configure your `localpath.m` to point to the right location for the Box sync on your machine. 

I then recommend cloning repositories for specific projects into a common folder on your machine, such as `Documents/CodeProjects` or something like this. You can also clone the Daily repository, which has all the daily analysis scripts we use as we take data. 

## Handling updates

This repository is going to be updated frequently, as we add new features and fix bugs. To keep your local copy up to date, you'll need to pull from Github. If a change is pushed to Github and you don't have any local changes, then great, just pull the changes from Github. If you DO have local changes, then you'll need to stash them, pull the changes from Github, and then unstash your changes to apply them on top of the updated code. If there's a conflict, you'll need to resolve it manually. For this reason, I recommend pulling from Github frequently, so that you don't have to deal with a ton of changes at once. 

## API Documentation

