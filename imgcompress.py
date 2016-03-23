#!/usr/bin/python
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
import numpy as np
# import numpy as p
# if p is np:
#   print 'we solved it!'
import urllib
from PIL import Image
import argparse
import os
import requests

WIDTH = 720*3

# Imgur compresses images over 5 MB
# But 1 MB for anonymous QQ
MAX_FILE_SIZE = 1*1000**2

# Size of imgur's encoding
ENC_LEN = 7

# Requests URL
TOKEN_URL = 'https://api.imgur.com/oauth2/token'

# Initialize the client
try:
  try:
    sec = open('SECRET','r')
  except IOError:
    sec = open('secret.secret','r')
  newline_filter = lambda c: False if c=='\n' or c=='\r' else True
  client_id = filter(newline_filter,sec.readline())
  client_secret = filter(newline_filter,sec.readline())
  sec.close()
  client = ImgurClient(client_id,client_secret)
except:
  pass

def login(client):
  '''Uses pin login to log a client in'''
  try:
    with open('.imgcompress.user_session.sav','r') as f:
      access_token = filter(newline_filter,f.readline())
      refresh_token = filter(newline_filter,f.readline())
    client.set_user_auth(access_token,refresh_token)
    try:
      client.auth.refresh()
    except ImgurClientError:
      raise IOError
    with open('.imgcompress.user_session.sav','w') as f:
      f.write(client.auth.get_current_access_token() + '\n' + client.auth.refresh_token)
  except IOError:
    print 'Please go to https://api.imgur.com/oauth2/authorize?client_id=' + client_id + \
        '&response_type=pin&state=none and sign in with your imgur account!'
    pin = raw_input('Pin: ')
    data = {'client_id':client_id,'client_secret':client_secret,'grant_type':'pin','pin':pin}
    response = requests.post(TOKEN_URL,data=data)
    try:
      access_token = response.json()['access_token']
      refresh_token = response.json()['refresh_token']
      client.set_user_auth(access_token,refresh_token)
      with open('.imgcompress.user_session.sav','w') as f:
        f.write(access_token + '\n' + refresh_token)
    except:
      print 'Log in failed! Continuing as anonymous user (Compression ratio may be affected.)'
      return False
  global MAX_FILE_SIZE
  MAX_FILE_SIZE = 5*1000**2
  return True

def topng_helper(binary_array,width,save_path,mode):
  '''Helps turn binaries into nice pngs'''

  # find file size
  size_array = np.array([binary_array.shape[0]%256,binary_array.shape[0]/256%256,\
      binary_array.shape[0]/256/256%256,binary_array.shape[0]/256/256/256%256],'uint8')

  # Add file size to binary
  binary_array = np.concatenate((size_array,binary_array),axis=0)

  # Find the height of image and add padding
  data_size = binary_array.shape[0]
  height = data_size/width
  pad = width-data_size%width
  
  if pad%width != 0:
    height += 1
  else:
    pad = 0

  diff = 0
  height += diff
  pad += diff * WIDTH

  if mode is 'RGB':
    pass
  elif mode is not None:
    print 'Unsupported mode'
    return None

  if binary_array.shape[0] < pad:
    padding = np.concatenate([binary_array]*(pad/binary_array.shape[0]+1),axis=0)[:pad]
  else:
    padding = binary_array[:pad]
  binary_array = np.concatenate((binary_array,padding),axis=0)

  assert(width*height==binary_array.shape[0])

  # Make the matrix of pixels
  dat = binary_array.reshape(height,width/3,3)

  image = Image.fromarray(dat,mode=mode)
  image.save(save_path)
  return save_path

def topng(path,width=WIDTH,save_path='.tmp.png',mode='RGB'):
  '''Turns a binary into a nice png'''

  dt = 'uint8'
  
  # Get data from binary file
  binary_array = np.fromfile(path,dtype=dt)
  binary_array.dtype = 'uint8'

  size = binary_array.shape[0]

  comp_size = 0
  ret_path = []

  while comp_size < size:
    spath = '.' + str(comp_size/MAX_FILE_SIZE) + save_path
    comp_size += MAX_FILE_SIZE
    ret_path += [topng_helper(binary_array[:MAX_FILE_SIZE],width,spath,mode)]
    if comp_size < size:
      binary_array = binary_array[MAX_FILE_SIZE:]

  print 'Compression is done. Your compression ratio today was:',size/(7.0 * (comp_size+MAX_FILE_SIZE-1)/MAX_FILE_SIZE)
  return ret_path

def frompng(png,save_path='BINARY'):
  '''Takes a png file and takes out the binary shit'''
  try:
    img = Image.open(png)
  except AttributeError as e:
    print 'Did not find a valid Imgur image!'
    raise e

  binary_array = np.array(img,dtype='uint8').reshape(-1,)
  size = 0
  for i in range(4):
    size += binary_array[i]*256**i

  # print binary_array[0],binary_array[1],binary_array[2],binary_array[3]
  # print size

  binary_array = binary_array[4:4+size]
  
  with open(save_path,'a') as f:
    f.write(binary_array.tostring())

  print 'Decompression is done. You\'re wasting space on your disk now.'

  return save_path

def download(enc,loc):
  '''Takes in an imgur encoding (enc) and puts it the path specified by a string (loc)'''
  try:
    url = client.get_image(enc).link
  except ImgurClientError as e:
    print e.error_message
    print e.status_code
    return
  urllib.URLopener().retrieve(url,loc)
  return loc

def decompress(path,decomp_path):
  with open(path,'r') as f:
    for line in f:
      while line != '':
        link = line[:7]
        png = download(link,'.temp.png')
        frompng(png,decomp_path)
        os.remove('.temp.png')
        line = line[7:]

def compress(path,comp_path=None):
  if comp_path is None:
    comp_path = path + '.imgc'
  with open(comp_path,'w') as comp_fd:
    tmp_files = topng(path)
    for tmp_file in tmp_files:
      cb = client.upload_from_path(tmp_file,anon=False)
      os.remove(tmp_file)
      comp_fd.write(str(cb[u'id']))

def main():
  parser = argparse.ArgumentParser( \
      prog='imgcompress.py', \
      description='''This is the highest average compression ratio compression algorithm available.
        And it's FREE.
        
        Make sure you have your Imgur API secret saved in 'secret.secret'. For more info:
            https://api.imgur.com/oauth2/addclient''')

  parser.add_argument('-c','--compress',required=False,help='follow with file name to compress')
  parser.add_argument('-d','--decompress',required=False,help='follow with file name to decompress')
  parser.add_argument('-t','--dest',required=True,help='specify where you want to store the file')
  parser.add_argument('-a','--auth',help='specify where you want to store the file',action='store_true',default=False)
  
  args = parser.parse_args()

  # Make empty file/empty out existing file
  open(args.dest,'w').close()

  if args.compress is None and args.decompress is None:
    parser.print_help()
    return

  if args.compress is not None:
    if args.noauth:
      loggedin = login(client)

    path = args.compress
    compress(path,args.dest)
    return

  if args.decompress is not None:
    path = args.decompress
    decompress(path,args.dest)

if __name__ == '__main__':
  main()
