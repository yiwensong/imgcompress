from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
import numpy as np
# import numpy as p
# if p is np:
#   print 'we solved it!'
import urllib
from PIL import Image
import argparse

WIDTH = 720*3
# ONETRUEGOD = np.array(Image.open('onetruegod.png'),dtype='uint8')
# OTG_HEIGHT = ONETRUEGOD.shape[0]

REP = 1

sec = open('secret.secret','r')
newline_filter = lambda c: False if c=='\n' or c=='\r' else True
client_id = filter(newline_filter,sec.readline())
client_secret = filter(newline_filter,sec.readline())
sec.close()
client = ImgurClient(client_id,client_secret)

def add_zeros(array,rep=REP):
  if rep<=1:
    return array
  new_arr = np.array([0]*array.shape[0]*rep,dtype='uint8')
  for i in range(array.shape[0]):
    new_arr[i*rep+1] = array[i]
  return new_arr

def rm_zeros(array,rep=REP):
  return np.array([array[i] for i in range(0,array.shape[0],rep)],dtype='uint8')

def topng(path,width=WIDTH,save_path='tmp.png',mode='RGB'):
  '''Turns a binary into a nice png'''

  dt = 'uint8'
  
  # Get data from binary file
  binary_array = np.fromfile(path,dtype=dt)
  # print binary_array.shape

  binary_array.dtype = 'uint8'
  # print binary_array.shape

  # Used to sparse out data for onetruegod
  binary_array = add_zeros(binary_array)

  # find file size
  size_array = np.array([binary_array.shape[0]%256,binary_array.shape[0]/256%256,\
      binary_array.shape[0]/256/256%256,binary_array.shape[0]/256/256/256%256],'uint8')

  sz = 0
  for i in range(4):
    sz += size_array[i] * (2**(4*i))

  # Add file size to binary
  binary_array = np.concatenate((size_array,binary_array),axis=0)

  # print binary_array.dtype

  # Find the height of image and add padding
  data_size = binary_array.shape[0]
  height = data_size/width
  pad = width-data_size%width

  print size_array, data_size, sz
  
  if pad%width != 0:
    height += 1
  else:
    pad = 0

  # diff = OTG_HEIGHT - (height % OTG_HEIGHT)
  diff = 0
  height += diff
  pad += diff * WIDTH

  if mode is 'RGB':
    pass
  elif mode is not None:
    print 'Unsupported mode'
    return None

  padding = binary_array[:pad]
  binary_array = np.concatenate((binary_array,padding),axis=0)

  # print 'pad',pad
  # print height,width,height*width
  # print len(binary_array)

  assert(width*height==binary_array.shape[0])

  # Make the matrix of pixels
  dat = binary_array.reshape(height,width/3,3)
  # dat.dtype = 'uint8'

  # print dat
  # print len(dat)
  # print dat.shape
  # print dat.dtype
  
  # gods_needed = height/OTG_HEIGHT
  # if gods_needed > 0:
  #   god = np.concatenate([ONETRUEGOD]*gods_needed,axis=0)

  image = Image.fromarray(dat,mode=mode)
  # image = image.convert('RGB')
  image.save(save_path)

  return save_path

def frompng(png,save_path='BINARY'):
  '''Takes a png file and takes out the binary shit'''
  img = Image.open(png)
  binary_array = np.array(img,dtype='uint8').reshape(-1,)

  size = 0
  for i in range(4):
    size += binary_array[i]*256**i

  print binary_array[0],binary_array[1],binary_array[2],binary_array[3]
  print size

  binary_array = binary_array[4:4+size]

  binary_array.tofile(save_path)

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
  f = open(path,'r')
  link = f.read()[:7]
  png = download(link,'tmp')
  frompng(png,decomp_path)
  # TODO: cleanup the tmp file

def compress(path,comp_path=None):
  if comp_path is None:
    comp_path = path + '.imgc'
  comp_fd = open(comp_path,'w')
  tmp_file = topng(path)
  # TODO: Cleanup tmp_file
  cb = client.upload_from_path(tmp_file)
  comp_fd.write(str(cb[u'id']))
  comp_fd.close()

def main():
  parser = argparse.ArgumentParser( \
      prog='imgcompress.py', \
      description='''This is the highest average compression ratio compression algorithm available.
        And it's FREE.''')

  parser.add_argument('-c','--compress',required=False,help='follow with file name to compress')
  parser.add_argument('-d','--decompress',required=False,help='follow with file name to decompress')
  parser.add_argument('-t','--dest',required=True,help='specify where you want to store the file')
  
  args = parser.parse_args()

  if args.compress is None and args.decompress is None:
    parser.print_help()
    return

  if args.compress is not None:
    path = args.compress
    compress(path,args.dest)
    return

  if args.decompress is not None:
    path = args.decompress
    decompress(path,args.dest)


if __name__ == '__main__':
  main()
