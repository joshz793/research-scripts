"""
png2gif.py combines .png files into a .gif file.
This is originally made as a helper script to generate rotating molecular orbitals animations.
For the expected directory tree, return a .gif with Y frames, with X .pngs per frame
Expected directory tree:
png_dir (sys.argv[1])
 | - pngs0
 | | - 1.png
 | | - 2.png
 | . . .
 | | - X.png
 | - pngs1
 | - pngs2
. . .
 | - pngsY
"""    
from PIL import Image
import sys, os, re
import numpy as np

def sort_dir(s : str):
    '''
    Extracts everything after the fourth character in a string and attempt to return as an int
    '''
    return int(s[4:])

def sort_png(s : str):
    '''
    Takes a string of format "*X.png"
    where "X" is a string of at least 1 digits from [0-9] followed by ".png" 
    and returns "X" as an integer
    '''
    return int(re.findall(r"([\d]+)\.png", s)[0])

def get_pseudo_square(n : int):
    '''
    Returns the number of columns and rows needed to fit "n" entries
    abs(n_cow - n_row) <= 1
    '''
    n_sqrt = np.sqrt(n)
    n_col = np.ceil(n_sqrt)
    n_row = np.floor(n_sqrt)
    if n_row * n_col < n:
        n_row = np.round(n_sqrt)
    return n_col, n_row

def combine_pngs(dir : str):
    '''
    Take all files in "dir" (assume all are .png files), and combine onto a single .png
    Returns an PIL.Image object
    '''
    png_list = sorted(next(os.walk(dir))[2], key=sort_png)
    
    # Find minimal square to fit all images on
    n_col, n_row = get_pseudo_square(len(png_list))
    
    # Gather pngs files
    pngs = [Image.open(os.path.join(png_dir, dir, png)) for png in png_list]
    width, height = pngs[0].size    # Assume all .pngs are of the same size
    
    # Preallocate new image that can fit n_col*n_row images.
    # This combined image will be 1 frame of the .gif
    new_im = Image.new('RGB', (int(width*n_col), int(height*n_row)))
    x_offset = 0
    y_offset = 0
    # Paste each image onto the new combined image
    for idx, im in enumerate(pngs):
        new_im.paste(im, (x_offset,y_offset))
        x_offset = width * int((idx+1)%n_col)
        y_offset = height * int((idx+1)%n_row)
    return new_im

def render_gif(imgs, out_file="combined.gif", fps=12):
    '''
    Generates a .gif from "imgs" with framerate "fps" to a file "out_file"
    '''
    imgs[0].save(fp=out_file, format='GIF', append_images=imgs,
        save_all=True, duration=1000/fps, loop=0)

fps = 12 # Frames per second to render the .gifs
png_dir = sys.argv[1]   # Directory to find .png files
if len(sys.argv) > 2:   # Default .gif filename of "combined.gif"
    out_file = sys.argv[2]
else:
    out_file = "combined.gif"

collated_imgs = []
# Iterate through each sub_directory
for dir in sorted(next(os.walk(png_dir))[1], key=sort_dir):
    collated_imgs += [combine_pngs(os.path.join(png_dir, dir))]
render_gif(collated_imgs, out_file=out_file, fps=fps)
# Generate the .gif file from the combined images
