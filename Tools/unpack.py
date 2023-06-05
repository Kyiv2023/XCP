#!/usr/bin/env python
import argparse
from clickerai_dataset_tools.clicker_zip import unpack_clicker_zip
def _main(args):
    unpack_clicker_zip(args.zip_file, args.out_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Unpacks ZIP_FILE and creates PNG files that are combinations of TIFF files in the archive.')
    parser.add_argument('zip_file', type=str, help='The path to the zip file')
    parser.add_argument('out_path', type=str, help='The path where to unpack')
    args = parser.parse_args()
    _main(args)
