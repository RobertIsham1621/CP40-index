# Import the requests and json modules
import requests
import json
from PIL import Image
from io import BytesIO
import urllib.request

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
for img in data['_via_img_metadata']:
  for r in  data['_via_img_metadata'][img]['regions']:
    if r['region_attributes']['text']=='¶':
      print(r['shape_attributes'])
      print(r['region_attributes'])
      bbox=[r['shape_attributes']['x'],
            r['shape_attributes']['y'],
            r['shape_attributes']['width'],
            r['shape_attributes']['height']]
      count +=1
      imgurl=img[0:-2]
      file = BytesIO(urllib.request.urlopen(imgurl).read())

      # Open the image with PIL
      im = Image.open(file)
      width, height = im.size
      grid_size=20
      reg=[0,bbox[0]/width, bbox[1]/height, bbox[2]/width,bbox[3]/height]
      print(str(reg))
      mylabelfile="train/labels/" +imgurl[-12:-4] +".txt"
      with open(mylabelfile,'a') as f:
        f.writelines(str(reg[0]) +" "+ str(reg[1])+" "+str(reg[2])+" "+str(reg[3]) +" "+str(reg[4]) +"\n")
      if not imgurl in imgs_loaded:
        imgs_loaded.add(imgurl)
        response = requests.get(imgurl)


        # Check if the response is successful
        if response.status_code == 200:
            # Define the directory and file name to save the image
            directory = "train/images/"
            file_name = imgurl[-12:]
            
            # Open a file in write-binary mode and write the response content
            with open(directory + file_name, "wb") as file:
                file.write(response.content)

print(str(count))

%pip install ultralytics
import ultralytics
ultralytics.checks()
!yolo train model=yolov8s.pt data=data.yaml epochs=200 imgsz=2048

