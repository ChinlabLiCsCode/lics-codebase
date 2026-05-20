# Chin Lab Lithium-Cesium Codebase

This is the primary repository for the Chinlab Lithium-Cesium codebase, created in July 2024 by merging a bunch of smaller repositories because it was getting too annoying to keep everything synced. The usage of git began in 2023 with an effort by Henry and Michael to organize the code base and make it more accessible. As such, older code probably can't be found here.

As of 2026, we are switching from the old labview/MATLAB control system and data  analysis paradigm to a new Python-based system, using the labscript-suite as our experiment control software. In May 2026, I merged the user-level labscript-suite code into this repo, and brought in the core labscript-suite code in as git submodules. The labscript-suite code is stored in the `labscript-suite` subdirectory. To update the submodules, you can run `git submodule update --remote` from the command line in the root directory of this repository. 

## Installation

To use this code base, you will need to have git, MATLAB, and Python with conda installed on your machine. You can clone this repository to your local machine using git. Clone it using 

`git clone --recurse-submodules git@github.com:ChinlabLiCsCode/lics-codebase.git`

This will automatically install and populate the labscript submodules, which are maintained somewhat separately in order to preserve the ability to bring changes back and forth from the official labscript-suite distribution.

### MATLAB

To run old MATLAB code, you then need to add two additional `.m` files in your MATLAB directory, which are not stored in git because they're machine specific. These are: `localpath.m` and `startup.m`. I'm including templates for these files in the `example_files` subdirectory, but they'll need to be filled in with the correct paths for your machine. `startup.m` is run when you open MATLAB, and lets you add extra folders to your MATLAB path (in this case, `lics-codebase` and its subfolders). `localpath.m` tells the image loading functions where to look for the images stored on your machine. We'll get to that next.

In order to automatically download and process images from the experiment, you'll need to download the Box desktop client, and have the `CHIN_LICS` folder shared with you. The NAS automatically uploads to a subfolder of that Box folder, and so you can get data automatically through it. Then you'll need to configure your `localpath.m` to point to the right location for the Box sync on your machine. 

I then recommend cloning repositories for specific projects into a common folder on your machine, such as `Documents/CodeProjects` or something like this. You can also clone the Daily repository, which has all the daily analysis scripts we use as we take data. 

### Python / labscript-suite
To use the new python and labscript-suite code, you'll need to set up a conda environment with the required configurations. From [the labscript suite](https://labscriptsuite.org/en/latest/installation/setting-up-an-environment/#anaconda-python), you want to first set up a bare conda environment with Python 3. They use 3.11 but let's use the newest version that works, which is 3.13 as of this writing. I tried 3.14 and it had conflicts. Run:

`conda create -n labscript python=3.13`

The [next steps in the guide](https://labscriptsuite.org/en/latest/installation/developer-anaconda/) are to clone the seven core labscript-suite repos. This should already have been taken care of when you used `--recurse-submodules` in cloning the repo, but if it wasn't you can run `git submodule update --init --recursive` to pull in the submodules from Github.

Continuing to follow the guide, `cd` into the labscript-suite subfolder and run: 

```
conda activate labscript
conda config --env --append channels labscript-suite
conda install setuptools-conda "pyqt<6" pip desktop-app
setuptools-conda install-requirements labscript runmanager blacs lyse runviewer labscript-devices labscript-utils
pip install --no-build-isolation --no-deps -e labscript -e runmanager -e blacs -e lyse -e runviewer -e labscript-devices -e labscript-utils
```

At this point I had an error on Windows and had to run this: `conda install -c conda-forge pyzmq --force-reinstall`. Continuing on:

```
labscript-profile-create -n lics-labscript-apparatus -c
desktop-app install blacs lyse runmanager runviewer
conda remove conda # optional but highly recommended
```

The `labscript-profile-create` will set up a template user library in ~/labscript-suite, which is actually outside where you store the codebase on your machine. That's fine. Go into the labconfig/your_computer.ini file, and change the relevant paths to point to the locations you actually want them to point to:

```
apparatus_name = lics-labscript-apparatus   # should be this without needing to modify
shared_drive = ___  # point to the real shared drive on the experiment computer, or to the shared Box folder if on a separate analyzing computer.
experiment_shot_storage = %(shared_drive)s/Experiments/%(apparatus_name)s
userlib = ___/lics-codebase   # root for user code: point to lics-codebase.
pythonlib = %(userlib)s   # for helper python functions. redundant in our case.
labscriptlib = ___/lics-codebase/lics-labscript-apparatus   # for apparatus and sequence files
analysislib = ___/lics-codebase/lics-labscript-analysis   # for standard analysis code
app_saved_configs = %(labscript_suite)s/app_saved_configs/%(apparatus_name)s # don't change this one
user_devices = ___/lics-codebase/lics-labscript-devices   # for our custom devices
```

Setting these should take care of it. 


## Handling updates

This repository is going to be updated frequently, as we add new features and fix bugs. To keep your local copy up to date, you'll need to pull from Github. If a change is pushed to Github and you don't have any local changes, then great, just pull the changes from Github. If you DO have local changes, then you'll need to stash them, pull the changes from Github, and then unstash your changes to apply them on top of the updated code. If there's a conflict, you'll need to resolve it manually. For this reason, I recommend pulling from Github frequently, so that you don't have to deal with a ton of changes at once.

### Syncing labscript submodules with upstream

The seven labscript-suite submodules (`blacs`, `labscript`, `labscript-devices`, `labscript-utils`, `lyse`, `runmanager`, `runviewer`) are forks of the official [labscript-suite](https://github.com/labscript-suite) repos hosted under ChinlabLiCsCode. To pull in new upstream changes:

**One-time setup** — add an `upstream` remote inside each submodule (only needed once per machine):

```powershell
foreach ($repo in @("blacs","labscript","labscript-devices","labscript-utils","lyse","runmanager","runviewer")) {
  git -C "labscript-suite\$repo" remote add upstream "https://github.com/labscript-suite/$repo.git"
}
```

**Fetching and merging upstream changes** — run this whenever you want to sync:

```powershell
# Fetch all upstreams
foreach ($repo in @("blacs","labscript","labscript-devices","labscript-utils","lyse","runmanager","runviewer")) {
  git -C "labscript-suite\$repo" fetch upstream
}

# Check how far ahead/behind each fork is
foreach ($repo in @("blacs","labscript","labscript-devices","labscript-utils","lyse","runmanager","runviewer")) {
  $ahead  = git -C "labscript-suite\$repo" rev-list --count "upstream/master..HEAD"
  $behind = git -C "labscript-suite\$repo" rev-list --count "HEAD..upstream/master"
  Write-Host "$repo : ahead=$ahead behind=$behind"
}

# Merge and push each submodule
foreach ($repo in @("blacs","labscript","labscript-devices","labscript-utils","lyse","runmanager","runviewer")) {
  git -C "labscript-suite\$repo" checkout master
  git -C "labscript-suite\$repo" merge upstream/master --no-edit
  git -C "labscript-suite\$repo" push origin master
}
```

If a repo has local custom commits (ahead > 0), the merge may produce conflicts that need to be resolved manually before pushing.

**Update the submodule pointers** in the parent repo after all submodules are updated, then commit:

```powershell
git submodule update --remote --no-fetch
git add labscript-suite/blacs labscript-suite/labscript labscript-suite/labscript-devices labscript-suite/labscript-utils labscript-suite/lyse labscript-suite/runmanager labscript-suite/runviewer
git commit -m "Update labscript submodules to latest upstream"
git push
```

## API Documentation

