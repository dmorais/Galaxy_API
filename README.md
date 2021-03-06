## bioblend_GenAP

This is a set of scripts to that utilize bioblend to interact with the 
Galaxy API.



## Dependencies
Python 2.7 

Bioblend 0.11.0 

### **Installation**
After cloning edit these files:
* util/config.py.template  ( copy it to util/config.py and add server 
and port to the dictionary)

on your .bashrc add the line
````
export  API_KEY=
````
Where the API_KEY is the Admin Galaxy API key created from the GUI

## IMPORTANT

before using any script you must source the python env

```
source /cvmfs/soft.galaxy/v2/server/.venv/bin/activate
```

## Scripts
#### 1. **create_library.py**

## Set up on Galaxy
This Galaxy option must be set to a dir inside galaxy server.
````
library_import_dir = /srv/galaxy/galaxy-data-library/
````
Before using this script create a yaml file  following the template 
*yml_file/library.yml*.

This script creates a Galaxy Library from one of three different sources:
 local  file, url or from remote server (symlink). 
 * **Local** will upload files from your machine to the Galaxy Library
 * **Url** will fetch the files from a remote server and upload to the Galaxy
  Library
 *  **Server** will take file aready in the Galaxy server and symlink them
 to the Galaxy Library.
 
 The script will know which option (local, url, server) to use based on
 the yaml file.

```
    python create_library.py yaml_file.yml
```


#### 2. **pickle_library_dataset.py**

This script creates a pickled version of the Galaxy library, where the 
file name is the key and the Galaxy file id is the value. This speed up
the lookup for file IDs.

This script must be run after the Library creation and at every new library
release.

```

python pickle_library_dataset.py -l library_name [optional -d path to the pickled file will be created]
```

The script help
```
usage: pickle_library_dataset.py [-h] -l LIBRARY [-d DUMP]

A tool to create binary dictionary of a Galaxy library where the keys are file
namesand the values are file ids

optional arguments:
  -h, --help            show this help message and exit
  -l LIBRARY, --library LIBRARY
                        Name of the library holding the files.
  -d DUMP, --dump DUMP  A path to the directory where de library will be
                        dumped. Default lib_dump

```


#### 3. **transferDataSetIhec.py**

## Set up on Galaxy
This Galaxy option must be set to True. The Galaxy authetication must be
 handled by a proxy. If not the option -email of the script will be required
 and the script will not create random accounts.
```` 
use_remote_user = True
````
This script creates a user on Galaxy (if it does not exists), handles its
authentication, and adds to the user's history all datasets passed
to it (inside of a file). The datasets must be inside of the Galaxy Library.
**Use the create_libary.py to create the library before**

The script can also delete users from Galaxy.

````


    # Create a random user and add datasets from IHEC library to a new history
    python transferDataSetIhec.py -l IHEC -s dataset-list.txt 
    
    
    #Connect to a specific user account and add datasets from IHEC library to a new history  
    python transferDataSetIhec.py -l IHEC -s dataset-list.txt -e user@genap.com 
    
    #Connect to a specific user account and add datasets from IHEC library to a existing history 
    python transferDataSetIhec.py -l IHEC -s dataset-list.txt -e user@genap.com -his 87hg7gg6g6gf
    


    NOTE: pass the --dump argument if the pickled library is not at its default location (lib_dump)
````

**The dataset-list.txt file** is a file containing the path of each dataset
that will be imported in the user's history. This path must reflect the 
path inside of the Galaxy Library.

if for example a Library called IHEC contain this path
````
IHEC/consortia/species/file1.bigwig

IHEC/consortia/species/file2.bed
````
The dataset-list.txt should be
````
/consortia/species/file1.bigwig

/consortia/species/file2.bed
````

The script help

```
A tool to create user on Galaxy and transfer IHEC datasets to the user history

optional arguments:
  -h, --help            show this help message and exit
  
  -s SAMPLES, --samples SAMPLES
                        File with the sample's Libary path
                        
  -d DELETE, --delete DELETE
                        Id of the user to be deleted
                        
  -e EMAIL, --email EMAIL
                        User email on Galaxy (if user is already registered)
                        
  -his HISTORY_ID, --history_id HISTORY_ID
                        A Galaxy history id. If provided the files will be
                        uploaded to this history.
                        
  -l LIBRARY, --library LIBRARY
                        Name of the library holding the files.
  
  --dump DUMP           A path to the directory where de library dictonary was
                        dumped. Default lib_dump

```





## Author
#### **David Morais**
