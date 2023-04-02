# Import the requests and json modules
import requests
import json
from PIL import Image
from io import BytesIO
import urllib.request
import secrets
import string
import os

# Create a directory
try:
  os.makedirs('/content/train')
  os.makedirs('/content/train/images')
  os.makedirs('/content/train/labels')
  os.makedirs('/content/valid/images')
  os.makedirs('/content/valid/labels')
  
except:
  print('Problem')


# Define the URL of the JSON file
url = "https://raw.githubusercontent.com/RobertIsham1621/CP40-index/main/CP40-740.json"

# Send a GET request to the URL and get the response
response = requests.get(url)

# Parse the response as JSON
data = response.json()
import numpy as np

# Define a function to convert bounding box coordinates to region relative coordinates
def bbox_to_region(bbox, image_width, image_height, grid_size):
    # Convert (x, y, w, h) format to (cx, cy, w, h) format
    cx = bbox[0] + bbox[2] / 2
    cy = bbox[1] + bbox[3] / 2
    w = bbox[2]
    h = bbox[3]
    
    # Normalize the coordinates by dividing them by the image width and height
    cx /= image_width
    cy /= image_height
    w /= image_width
    h /= image_height
    
    # Assign each box to a grid cell based on its center coordinates
    grid_x = int(cx * grid_size)
    grid_y = int(cy * grid_size)
    
    # Subtract the top-left coordinates of the grid cell from the normalized center coordinates of the box
    cx -= grid_x / grid_size
    cy -= grid_y / grid_size
    
    # Return the region relative coordinates as a numpy array
    return np.array([cx, cy, w, h])

# Print the data or store it in a variable
count=0
imgs_loaded=set()
classdict=dict()
classind=0
which=1
for img in data['_via_img_metadata']:
  imgurl=img[0:-2]
  try:
    file =[] 
    for r in  data['_via_img_metadata'][img]['regions']:
      if 'field_type' in r['region_attributes']:
        if r['region_attributes']['field_type'] in\
        ['letter','latin phrase']:
          if not file:
            print(imgurl)
            file=BytesIO(urllib.request.urlopen(imgurl).read())
          if which == 1:
            which =2
          elif which == 2:
            which =1 
          with Image.open(file) as im:
            # Set the box tuple (left, upper, right, lower)
            x1=r['shape_attributes']['x']
            x2=r['shape_attributes']['x']+r['shape_attributes']['width']
            w=r['shape_attributes']['width']
            y1=r['shape_attributes']['y']
            y2=r['shape_attributes']['y']+r['shape_attributes']['height']   
            h=r['shape_attributes']['height']
            box = (x1, y1, x2, y2)

            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(8))
            # Crop the image
            # Save the cropped image
    # Crop the image
            im_cropped = im.crop(box)
            if which == 1:
              im_cropped.save("train/images/"+password + '.jpg')
            else:
              im_cropped.save("valid/images/"+password + '.jpg')
            label=r['region_attributes']['text']
            if label in classdict:
              classnum=classdict[label]
            else:
              classdict[label]=classind
              classnum=classdict[label]
              classind +=1
            reg=[classnum,0.5, 0.5, 1,1]
            if which == 1:
              mylabelfile="train/labels/"+password + '.txt'
            else:
              mylabelfile ="valid/labels/"+password + '.txt'
            with open(mylabelfile,'a') as f:
              f.writelines(str(reg[0]) +" "+ str(reg[1])+" "+str(reg[2])+" "+str(reg[3]) +" "+str(reg[4]) +"\n")

      if 'fully_indexed' in r['region_attributes']:
        if 'yes' in r['region_attributes']['fully_indexed']:
          if not file:
            file=BytesIO(urllib.request.urlopen(imgurl).read())
          if which == 1:
            which =2
          elif which == 2:
            which =1 
          if r['region_attributes']['fully_indexed']['yes']:
            x1=r['shape_attributes']['x']
            x2=r['shape_attributes']['x']+r['shape_attributes']['width']
            w=r['shape_attributes']['width']
            y1=r['shape_attributes']['y']
            y2=r['shape_attributes']['y']+r['shape_attributes']['height']   
            h=r['shape_attributes']['height']
            imgurl=img[0:-2]
            file = BytesIO(urllib.request.urlopen(imgurl).read())
            with Image.open(file) as im:
              # Set the box tuple (left, upper, right, lower)
              box = (x1, y1, x2, y2)

              alphabet = string.ascii_letters + string.digits
              password = ''.join(secrets.choice(alphabet) for i in range(8))
              # Crop the image
              # Save the cropped image
      # Crop the image
              im_cropped = im.crop(box)
              if which == 1:
                im_cropped.save("train/images/"+password + '.jpg')
              else:
                im_cropped.save("valid/images/"+password + '.jpg')
              for r2 in  data['_via_img_metadata'][img]['regions']:
                xr1=r2['shape_attributes']['x']
                xr2=r2['shape_attributes']['x']+r2['shape_attributes']['width']
                w2=r2['shape_attributes']['width']
                yr1=r2['shape_attributes']['y']
                yr2=r2['shape_attributes']['y']+r2['shape_attributes']['height'] 
                h2=r2['shape_attributes']['height'] 
                if xr1>x1 and xr2<x2 and yr1>y1 and yr2<y2:
                  if 'field_type' in r2['region_attributes']:
                    if r2['region_attributes']['field_type'] in\
                    ['letter','county','latin phrase']:
                          
                      label=r2['region_attributes']['text']
                      if label in classdict:
                        classnum=classdict[label]
                      else:
                        classdict[label]=classind
                        classnum=classdict[label]
                        classind +=1
                      reg=[classnum,((xr1+xr2)/2-x1)/w, ((yr1+yr2)/2-y1)/h, w2/w,h2/h]
                      if which == 1:
                        mylabelfile="train/labels/"+password + '.txt'
                      else:
                        mylabelfile ="valid/labels/"+password + '.txt'
                      with open(mylabelfile,'a') as f:
                        f.writelines(str(reg[0]) +" "+ str(reg[1])+" "+str(reg[2])+" "+str(reg[3]) +" "+str(reg[4]) +"\n")
  except:
    print('prolem')
with open('data.yaml', 'w') as file:
    file.write('train: ../train/images \n')
    file.write('val: ../valid/images \n')
    file.write('test: ../test/images \n')
    file.write('nc: ' + str(len(classdict.keys()))+ '\n')
    file.write('names: '+ str(list(classdict.keys())) + '\n')

    
%pip install ultralytics
import ultralytics
ultralytics.checks()

!yolo train model=yolov8s.pt data=data.yaml epochs=200 
!yolo mode=predict  model=runs/detect/train/weights/best.pt source=real_test.jpeg save_txt=True conf=0.2  save=True



