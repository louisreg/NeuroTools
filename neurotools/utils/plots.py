import imageio as iio
from pathlib import Path
import os
import numpy as np
import matplotlib.pyplot as plt
from shutil import rmtree
from tqdm import tqdm

def create_gif (animate: callable, n_frames: int, savefile: str) -> None:
    for i in tqdm(range(n_frames),desc= "GIF creation"):
        fig = animate(i)
        thisfile_path = str(Path(os.path.dirname(__file__)))
        save_path =  thisfile_path + "/temp_imgs/"
        Path(save_path).mkdir(parents=True, exist_ok=True)
        fig.savefig(f"{save_path}/{i}.jpg")
        plt.close(fig)
    frames = np.stack([iio.imread(f"{save_path}/{i}.jpg") for i in range(n_frames)], axis = 0)
    rmtree(save_path)
    print("Conversion to gif.... ", end="")
    iio.mimwrite(savefile, frames,subrectangles = True)
    print("Done!")

