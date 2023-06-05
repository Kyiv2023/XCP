import shutil

import os
import tempfile
import zipfile
import argparse
from PIL import Image
import PIL

import tqdm


def unpack_clicker_zip(zip_file, result_directory):
    """
    Unpacks ZIP_FILE and creates PNG files that are combinations of TIFF files in the archive.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)
        
        if not os.path.exists(result_directory):
            os.makedirs(result_directory)

        for file in os.listdir(tmp_dir):
            if file.endswith((".csv", ".json", ".yaml")):
                file_path = os.path.join(tmp_dir, file)
                shutil.move(file_path, result_directory)



        tiff_files = sorted([
            os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir) 
            if f.lower().endswith('.tif') or f.lower().endswith('.tiff')
        ])
        
        prev_image = None
        
        for tiff_file in tqdm.tqdm(tiff_files, desc=f"UNPACK {os.path.basename(zip_file)[:7]}", position=0):
            try:
                curr_image = Image.open(tiff_file)
            except (PIL.UnidentifiedImageError, OSError):
                
                break
                
            if prev_image is not None:
                curr_image = Image.alpha_composite(prev_image, curr_image)
            
            png_file = os.path.join(result_directory, os.path.splitext(os.path.basename(tiff_file))[0] + '.png')
            curr_image.save(png_file)
            
            prev_image = curr_image

            # update the progress bar with the current file name
            # tqdm.tqdm.write(f"{os.path.basename(tiff_file)} -> {png_file}")
            # tqdm.tqdm.write(f"{os.path.basename(tiff_file)[:5]}")

