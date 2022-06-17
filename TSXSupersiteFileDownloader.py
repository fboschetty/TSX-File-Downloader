#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 12:15:46 2022

@author: FelixBoschetty
"""

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
from os import path
from typing import List
from datetime import datetime
import numpy as np


@dataclass
class Config():
    """Class to load in config params from a config.json"""
    
    # Load config.json
    f = open("./config.json")
    config = json.load(f)
    f.close()
    
    # Directory to download files
    down_dir: str = config["dir"]
    
    # Supersite 
    url: str = config["url"]              # url for TSX supersites 
    supersite: str = config["supersite"]  # specific supersite
    
    # Filters
    orbit: str = config["orbit"]          # TSX orbit number  
    beam_id: str = config["beam_id"]      # TSX beam ID
    start: str = config["start"]          # first date considered
    end: str = config["end"]              # last date considered
    
    # Access
    user: str = config["user"]            # TSX supersite username
    password: str = config["password"]    # TSX supersite password
    
    

class HTMLscraper:
    """Class to scrape list of files from webpage"""
    
    def find_files(url: str, supersite: str):
        
        URL = path.join(url, supersite, "")
        
        soup = BeautifulSoup(requests.get(URL).text, features="html.parser")

        hrefs = []

        for a in soup.find_all('a'):
            hrefs.append(a['href'])
        return hrefs


class FilterDownloads(ABC):
   """Abstract Class for filtering downloads"""
   
   @abstractmethod
   def Filtered(to_download: List[str]) -> List[str]:
       """Abstract Method that takes a list of filenames and returns a filtered list"""
       pass


class FilterTSX(FilterDownloads):
    """Filters out non-TSX URLS"""
    def Filtered(to_download: List[str]) -> List[str]:
        return [file for file in to_download if "TSX" in file]

class FilterOrbitBeamID(FilterDownloads):
    """Filter downloads by Orbit Number and Beam ID"""
    def Filtered(to_download: List[str], orbit: str, beam_id: str) -> List[str]:
        return [file for file in to_download if (orbit in file) & (beam_id in file)]
 
class FilterStartEnd(FilterDownloads):
    """Filter downloads by start and end data"""
    
    def ExtractDates(to_download: List[str]) -> List[datetime.date]:
        """Convert list of dates to datetimes for comparison"""
        dates = [f[4:12] for f in to_download]
        dates = [datetime.strptime(d, '%Y%m%d') for d in dates]
        return dates
    
    def Filtered(to_download: List[str], start: str, end: str) -> List[str]:
        
        # Convert Start + End to datetime for comparison
        start_dt = datetime.strptime(start, '%Y%m%d') 
        end_dt = datetime.strptime(end, '%Y%m%d')
        
        # Compare list of dates with start and end
        dates = FilterStartEnd.ExtractDates(to_download)
        f_dates = [dt for dt in dates if (dt <= end_dt) & (dt >= start_dt)]
        f_dates = [dt.strftime('%Y%m%d') for dt in f_dates]  # Convert back to strings
        
        # Take advantage of numpy boolean indexing to filter original downloads
        date_good = np.zeros(len(to_download))
        
        for idx, file in enumerate(to_download):
            for f_date in f_dates:
                if f_date in file:
                    date_good[idx] = 1.
        
        date_good = date_good.astype(bool)
        to_download = np.array(to_download)
        
        return to_download[date_good].tolist()


class FileDownloader:
    """Class to download filtered files"""    
    
    def Downloader(to_download: List[str],
                   user: str,
                   password: str,
                   url: str,
                   supersite: str,
                   down_dir: str) -> None:
        
        for file in to_download:
            
            URL = path.join(url, supersite, file)
            
            print('Downloading:', file)
            response = requests.get(URL, auth=(user, password), stream=True)
            total_size_in_bytes= int(response.headers.get('content-length', 0))
            block_size = 1024 #1 Kibibyte
            
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
            with open(down_dir+file, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()
            
            
            if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                print("ERROR, something went wrong with the download")


def main():
    
    # Config Parameters
    cfg = Config()
    print("TSX Downloader Configuration Parameters")
    print('Supersite:', cfg.supersite)
    print('Orbit:', cfg.orbit)
    print('BeamID:', cfg.beam_id)
    print('Dates between: %s and %s' % (cfg.start, cfg.end))
    
    print('Downloading TSX files to:', cfg.down_dir)
    
    # Find Appropriate Files
    files = HTMLscraper.find_files(cfg.url, cfg.supersite)
    files = FilterTSX.Filtered(files)
    files = FilterOrbitBeamID.Filtered(files, cfg.orbit, cfg.beam_id)
    files = FilterStartEnd.Filtered(files, cfg.start, cfg.end)
    
    # Check files isn't empty
    if len(files) == 0:
        print('\nThere are no available files that match that search.')
        pass
    else:
        print('\nThere are %i files available that match that search.' %len(files))
    
    print("\n")
    
    # Download Files
    FileDownloader.Downloader(files, cfg.user, cfg.password, cfg.url, cfg.supersite, cfg.down_dir)
    
    return cfg, files

if __name__ == "__main__":
    main()
    
