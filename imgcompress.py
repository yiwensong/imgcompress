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
client_id = sec.readline()[0:14]
client_secret = sec.readline()[0:39]
sec.close()

client = ImgurClient(client_id,client_secret)

def topng(path,width=WIDTH,save_path='tmp.png'):
  '''Turns a binary into a nice png'''
  # Get data from binary file
  binary_array = np.fromfile(path,dtype='uint8')

  # find file size
  size_array = np.array([binary_array.shape[0]%255,binary_array.shape[0]/255%255,\
      binary_array.shape[0]/255/255%255,binary_array.shape[0]/255/255/255%255])

  # Add file size to binary
  binary_array = np.concatenate((size_array,binary_array),axis=0)

  # Find the height of image and add padding
  data_size = binary_array.shape[0]
  height = data_size/width
  pad = data_size%width
  if pad != 0:
    height += 1
  binary_array = np.concatenate((binary_array,np.array([0]*pad)),axis=0)

  # Make the matrix of pixels
  dat = binary_array.reshape(height,width)
  
  image = Image.fromarray(dat)
  image.save(save_path)

  return save_path

def decompress(enc,loc):
  '''Takes in an imgur encoding (enc) and puts it the path specified by a string (loc)'''
  try:
    url = client.get_image(enc).link
  except ImgurClientError as e:
    print e.error_message
    print e.status_code
    return
  urllib.URLopener().retrieve(url,loc)
