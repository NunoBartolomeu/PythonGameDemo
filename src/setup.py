from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["pygame"],
    "includes": [],
    "excludes": [],
    "include_files": ["client/", "common/"],  # Ensure these folders are included
}

setup(
    name="MyGame",
    version="1.0",
    description="A Pygame-based game",
    options={"build_exe": build_exe_options},
    executables=[Executable("client/main.py", base="Win32GUI")],
)
