from zipfile import ZipFile
import os
import numpy as np

def unzipmesh(fn, base_path, mesh_name):
    print(f"Extracting {fn} to {base_path}")
    with ZipFile(fn, 'r') as z:
        fns = z.namelist()
        # find meshes
        fn_mesh = [fn for fn in fns if fn[-5:] == ".data"]
        print(fn_mesh)
        data = z.read(fn_mesh[0])
        with open(f"{mesh_name}.data", "wb") as f:
            f.write(data)


    return

fn = "/home/hcwinsemius/Downloads/Mesh_Raider_WebGL_builds-20210607T114757Z-001.zip"
unzipmesh(fn, os.path.split(fn)[0], "mesh")