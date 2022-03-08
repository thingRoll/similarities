# -*- coding: utf-8 -*-
"""ResNet50_similar_search.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cASnOmR8wUtK4rRoiQJ0NrEiGy1unuMr
"""

# !pip install gdown
# !gdown --id 1IQ90jtnITrrcBWsFjF8jkFXF7LAxDqLF

# Commented out IPython magic to ensure Python compatibility.
# %%time
# import zipfile
# zip_ref = zipfile.ZipFile("archive.zip", 'r')
# zip_ref.extractall("./scenery")
# zip_ref.close()

import matplotlib.pyplot as plt
def show_images(images, figsize=(20,10), columns = 5):
  plt.figure(figsize=figsize)
  for i, image in enumerate(images):
      plt.subplot(len(images) / columns + 1, columns, i + 1)
      plt.imshow(image)

import os
IMAGES_PATH="./scenery"
IMAGES_PATH = '../examples/data/'
file_names=os.listdir(IMAGES_PATH)
print(f"number of images: {len(file_names)}")

from keras.applications.resnet50 import ResNet50
from keras.applications.resnet50 import preprocess_input
import os
from os import listdir
from os.path import splitext
import numpy as np
from PIL import Image
import pickle as pk
from tqdm import tqdm
def read_img_file(f):
    img = Image.open(f)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    return img

def resize_img_to_array(img, img_shape):
    img_array = np.array(
        img.resize(
            img_shape, 
            Image.ANTIALIAS
        )
    )    
    return img_array

def get_features(img):
    img_width, img_height = 224, 224
    np_img = resize_img_to_array(img, img_shape=(img_width, img_height))
    expanded_img_array = np.expand_dims(np_img, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    X_conv = model.predict(preprocessed_img)
    image_features=X_conv[0]
    image_features /=  np.linalg.norm(image_features)
    return image_features
    
model = ResNet50(weights='imagenet', include_top=False,input_shape=(224, 224, 3),pooling='max')

def generate_resnet_features():
    all_image_features=[]
    image_filenames=listdir(IMAGES_PATH)
    image_ids=set(map(lambda el: splitext(el)[0],image_filenames))
    try:
       all_image_features=pk.load(open("resnet_image_features.pkl", "rb"))
    except (OSError, IOError) as e:
       print("file_not_found")

    def exists_in_all_image_features(image_id):
        for image in all_image_features:
            if image['image_id'] == image_id:
                # print("skipping "+ str(image_id))
                return True
        return False

    def exists_in_image_folder(image_id):
        if image_id in image_ids:
                return True
        return False   

    def sync_resnet_image_features():
        for_deletion=[]
        for i in range(len(all_image_features)):
            if not exists_in_image_folder(all_image_features[i]['image_id']):
                print("deleting "+ str(all_image_features[i]['image_id']))
                for_deletion.append(i)
        for i in reversed(for_deletion):
            del all_image_features[i]

    sync_resnet_image_features()
    for image_filename in tqdm(image_filenames):
        image_id=splitext(image_filename)[0]
        if exists_in_all_image_features(image_id):
            continue
        img_arr = read_img_file(IMAGES_PATH+"/"+image_filename)
        image_features=get_features(img_arr)
        # print(image_filename)
        # print(image_features)
        all_image_features.append({'image_id':image_id,'features':image_features})
    pk.dump(all_image_features, open("resnet_image_features.pkl","wb"))

generate_resnet_features()

import numpy as np
from PIL import Image
query_image_pillow=Image.open(f'{IMAGES_PATH}/00000061_(6).jpg').convert('RGB')
query_image_features=get_features(query_image_pillow)
show_images([np.array(query_image_pillow)])
print(query_image_features.shape)

from sklearn.neighbors import NearestNeighbors
from os import listdir
import pickle as pk

image_features=pk.load( open("resnet_image_features.pkl", "rb"))
features=[]
for image in image_features:
    features.append(np.array(image['features']))
features=np.array(features)
features=np.squeeze(features)

path="./scenery"
knn = NearestNeighbors(n_neighbors=20,algorithm='brute',metric='euclidean')
knn.fit(features)
file_names=listdir(path)

indices = knn.kneighbors([query_image_features], return_distance=False)
found_images=[]
for x in indices[0]:
    found_images.append(np.array(Image.open(path+"/"+file_names[x])))
show_images(np.array(found_images))

# !pip install hnswlib

import hnswlib
dim=2048
index = hnswlib.Index(space='l2', dim=dim)
index.init_index(max_elements=10000, ef_construction=100, M=16)
index.add_items(features)

# Commented out IPython magic to ensure Python compatibility.
# %%time
labels, distances = index.knn_query([query_image_features], k = 20)

images_np_hnsw=[]
labels=labels[0]
print(labels)
for idx in labels:
  images_np_hnsw.append(np.array(Image.open(f'{IMAGES_PATH}/{file_names[idx]}')))
show_images(np.array(images_np_hnsw))

width, height = query_image_pillow.size
query_image_resized=query_image_pillow.resize((width//19, height//19))
query_image_resized_features=get_features(query_image_resized)
show_images([np.array(query_image_resized)])
labels, distances = index.knn_query([query_image_resized_features], k = 20)
images_np_hnsw_2=[]
labels=labels[0]
print(labels)
for idx in labels:
  images_np_hnsw_2.append(np.array(Image.open(f'{IMAGES_PATH}/{file_names[idx]}')))
show_images(np.array(images_np_hnsw_2))

query_image_rotated = query_image_pillow.rotate(180)
query_image_rotated_features=get_features(query_image_rotated)
show_images([np.array(query_image_rotated)])
labels, distances = index.knn_query([query_image_rotated_features], k = 20)
images_np_hnsw_3=[]
labels=labels[0]
print(labels)
for idx in labels:
  images_np_hnsw_3.append(np.array(Image.open(f'{IMAGES_PATH}/{file_names[idx]}')))
show_images(np.array(images_np_hnsw_3))

crop_rectangle = (400, 200, 600, 400)
query_image_cropped = query_image_pillow.crop(crop_rectangle)
query_image_cropped_features=get_features(query_image_cropped)
show_images([np.array(query_image_cropped)])
labels, distances = index.knn_query([query_image_cropped_features], k = 20)
images_np_hnsw_4=[]
labels=labels[0]
print(labels)
for idx in labels:
  images_np_hnsw_4.append(np.array(Image.open(f'{IMAGES_PATH}/{file_names[idx]}')))
show_images(np.array(images_np_hnsw_4))

# !pip install git+https://github.com/qwertyforce/Embeddings2Image.git@patch-1

import os
from tqdm import tqdm
from e2i import EmbeddingsProjector
import numpy as np
import h5py
import pickle as pk
data_path = 'data.hdf5'
output_path = 'output_plot'
full_file_names=list(map(lambda el: IMAGES_PATH+"/"+el,file_names))
with h5py.File(data_path, 'w') as hf:
    hf.create_dataset('urls', data=np.asarray(full_file_names).astype("S"))
    hf.create_dataset('vectors', data=features)
    hf.close()

image = EmbeddingsProjector()
image.path2data = data_path
image.load_data()
image.each_img_size = 100
image.output_img_size =  10000
image.calculate_projection()
image.output_img_name = output_path
image.output_img_type = 'scatter'
image.create_image()
print(image.image_list)
print('done!')