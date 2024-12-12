from PIL import Image
import sys, os, re
import numpy as np
def sort_dir(s):
    return int(s[4:])

def sort_png(s):
    
    return int(re.findall(r"([\d]+)\.png", s)[0])

# png_dir='./pngs/'
png_dir = sys.argv[1]
if len(sys.argv) > 2:
    out_file = sys.argv[2]
else:
    out_file = "combined.gif"
collated_imgs = []
for dir in sorted(next(os.walk(png_dir))[1], key=sort_dir):
    png_list = sorted(next(os.walk(os.path.join(png_dir, dir)))[2], key=sort_png)
    root_len_png_list = np.sqrt(len(png_list))
    n_col = np.ceil(root_len_png_list)
    n_row = np.floor(root_len_png_list)
    print(n_col, n_row)
    if n_row * n_col < len(png_list):
        n_row = np.round(root_len_png_list)
    
    orbitals = [Image.open(os.path.join(png_dir, dir, png)) for png in png_list]
    width, height = orbitals[0].size
        
    new_im = Image.new('RGB', (int(width*n_col), int(height*n_row)))
    x_offset = 0
    y_offset = 0
    for idx, im in enumerate(orbitals):
        new_im.paste(im, (x_offset,y_offset))
        x_offset = width * int((idx+1)%n_col)
        y_offset = height * int((idx+1)/n_row)
    collated_imgs += [new_im]
collated_imgs[0].save(fp=out_file, format='GIF', append_images=collated_imgs,
        save_all=True, duration=1000/12, loop=0)
