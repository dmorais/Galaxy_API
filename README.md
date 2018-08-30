## bioblend_GenAP

This is a set of scripts to that utilize bioblend to interact with the 
Galaxy API.

## Dependencies
Python 2.7 
Bioblend 0.7.3 or higher

### **Installation**
After cloning edit these files:
* util/config.py  (add server and port to the dictionary)
* api_key.txt.template (copy it as api_key.txt add your server, port
and your Galaxy API key)


## Scripts
#### 1. **create_library.py**


Before using this script create a yml file  following the template 
*yml_file/library.yml*.

This script creates a Galaxy Library from one of three different sources:
 local  file, url or from remote server (symlink). 
 * **Local** will upload files from your machine to the Galaxy Library
 * **Url** will fetch the files from a remote server and upload to the Galaxy
  Library
 *  **Server** will take file aready in the Galaxy server and symlink them
 to the Galaxy Library.

```
    python create_library.py api_key.txt yml_file.yml

```

#### 2. **transferDataSetIhec.py**








## Author
#### **David Morais**
