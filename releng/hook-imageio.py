from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('imageio', subdir="resources")

hiddenimports = collect_submodules('imageio')
hiddenimports.extend(["imageio.plugins.*"])
