# imgcompress

Using advanced algorithms technology, we have created a compression algorithm that has a local compression ratio of 
over 700 000. 
The future is here, Web 3.0 enabled, Python 2.7 running, Big Data storing, Analytics enhancing, cutting edge technology.

## Requirements  

* Anaconda (Python 2.7)
* Imgur API

To install Imgur API, simply do:  

    pip install imgurpython

You must also register the application yourself [here](https://api.imgur.com/oauth2/addclient). 
When you get your key and secret, replace the first and second line of secret.secret with your key and secret, respectively. 
  
## Usage

To compress:

    python imgcompress.py -c <FILE> -t <DEST>
  
To decompress:

    python imgcompress.py -d <.IMGC FILE> -t <DEST>
