from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
import numpy as np
import numpy as p
if p is np:
  print 'we solved it!'
import urllib
from PIL import Image

WIDTH = 720

sec = open('secret.secret','r')
newline_filter = lambda c: False if c=='\n' or c=='\r' else True
client_id = filter(newline_filter,sec.readline())
client_secret = filter(newline_filter,sec.readline())
sec.close()

client = ImgurClient(client_id,client_secret)

def topng(path,width=WIDTH,save_path='tmp.png',mode=None):
  '''Turns a binary into a nice png'''
  
  # Get data from binary file
  binary_array = np.fromfile(path,dtype='uint8')

  # find file size
  size_array = np.array([binary_array.shape[0]%255,binary_array.shape[0]/255%255,\
      binary_array.shape[0]/255/255%255,binary_array.shape[0]/255/255/255%255],'uint8')

  # Add file size to binary
  binary_array = np.concatenate((size_array,binary_array),axis=0)

  # print binary_array.dtype

  # Find the height of image and add padding
  data_size = binary_array.shape[0]
  height = data_size/width
  pad = width-data_size%width
  
  if pad%width != 0:
    height += 1
  else:
    pad = 0

  if mode is 'RGB':
    pass
  elif mode is not None:
    print 'Unsupported mode'
    return None

  padding = np.array([0]*pad,'uint8')
  binary_array = np.concatenate((binary_array,padding),axis=0)

  assert(width*height==binary_array.shape[0])

  # print pad
  # print height,width
  # print len(binary_array)

  # Make the matrix of pixels
  dat = binary_array.reshape(height,width/3,3)
  # dat.dtype = 'uint8'

  print dat
  print len(dat)
  print dat.shape
  print dat.dtype
  
  image = Image.fromarray(dat,mode=mode)
  # image = image.convert('RGB')
  image.save(save_path)

  return save_path

def frompng(png,save_path='BINARY'):
  '''Takes a png file and takes out the binary shit'''
  img = Image.open(png)
  binary_array = np.array(img,dtype='uint8').reshape(-1,)

def decompress(enc,loc):
  '''Takes in an imgur encoding (enc) and puts it the path specified by a string (loc)'''
  try:
    url = client.get_image(enc).link
  except ImgurClientError as e:
    print e.error_message
    print e.status_code
    return
  urllib.URLopener().retrieve(url,loc)
