from zipfile import ZipFile
import os
def unzipmesh(fn, trg_path, mesh_name):
    print(f"Extracting {fn}")
    with ZipFile(fn, 'r') as z:
        fns = z.namelist()
        # find meshes
        fn_mesh = [fn for fn in fns if fn[-5:] == ".data"]
        print(fn_mesh)
        if not(os.path.isdir(trg_path)):
            os.makedirs(trg_path)
        # data = z.read(fn_mesh[0])
        with open(os.path.join(trg_path, f"{mesh_name}.data"), "wb") as f:
            f.write(z.read(fn_mesh[0]))
    return
