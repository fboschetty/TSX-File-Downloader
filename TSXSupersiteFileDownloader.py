#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 12:15:46 2022

@author: FelixBoschetty
"""

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

# Function to find files on webpage
def find_files(url):
    soup = BeautifulSoup(requests.get(url).text)

    hrefs = []

    for a in soup.find_all('a'):
        hrefs.append(a['href'])

    return hrefs

# Extract files 

URL = "https://download.geoservice.dlr.de/supersites/files/LatinAmerica/" # URL including which supersite

links = find_files(URL)

# Filter By Orbit and Beam ID

Orbit = 'O013'    # Choose Orbit here
BeamID = 'SL084'  # Choose BeamID here

to_download = []
for fileID in links:
    if (Orbit in fileID) & (BeamID in fileID):
        to_download.append(URL+fileID)

# Download files

user=''  # TSXSupersite username
key=''   # TSXSupersite password

for url in to_download:
    response = requests.get(url, auth=(user, key), stream=True)
    total_size_in_bytes= int(response.headers.get('content-length', 0))
    block_size = 1024 #1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open('test.dat', 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")

    
