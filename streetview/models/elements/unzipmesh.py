from zipfile import ZipFile
import os
def unzipmesh(fn, trg_path, mesh_name):
    """
    Unzips relevant files from a unity game and renames to a standardized name
    :param fn: .zip file containing a unity game
    :param trg_path: path to unzip targets
    :param mesh_name: name of mesh (used to standardize name)
    :return: None
    """
    print(f"Extracting {fn}")
    with ZipFile(fn, 'r') as z:
        fns = z.namelist()
        # find mesh, framework, loader and wasm files, if there are multiple, only the first is considered
        fn_mesh = [fn for fn in fns if fn[-5:] == ".data"][0]
        fn_framework = [fn for fn in fns if "framework.js" in fn][0]
        fn_loader = [fn for fn in fns if "loader.js" in fn][0]
        fn_wasm = [fn for fn in fns if ".wasm" in fn][0]
        print(fn_mesh)
        if not(os.path.isdir(trg_path)):
            os.makedirs(trg_path)
        # unzip mesh
        with open(os.path.join(trg_path, f"{mesh_name}.data"), "wb") as f:
            f.write(z.read(fn_mesh))
        # unzip framework
        with open(os.path.join(trg_path, f"{mesh_name}.framework.js"), "wb") as f:
            f.write(z.read(fn_framework))
        # unzip loader
        with open(os.path.join(trg_path, f"{mesh_name}.loader.js"), "wb") as f:
            f.write(z.read(fn_loader))
        # unzip framework
        with open(os.path.join(trg_path, f"{mesh_name}.wasm"), "wb") as f:
            f.write(z.read(fn_wasm))
    return
