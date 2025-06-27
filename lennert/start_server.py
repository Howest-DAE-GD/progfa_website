from pathlib import Path
import zipfile
import subprocess


# Function to zip the contents of the ./Resources directory into a Resources subfolder in the zip file
def zip_game():
    root_dir = Path(__file__).parent.resolve()
    resources_dir = root_dir / 'Resources'

    # Directories whose contents should not be zipped in the game
    exclude_dirs = [root_dir / 'docs', root_dir / '.git', root_dir / '.idea',
                    root_dir / '__pycache__', root_dir / 'pyodide']

    with (zipfile.ZipFile('game.zip', 'w', zipfile.ZIP_DEFLATED) as zipf):
        # Zip all python files in your project (but not from excluded directories)
        for file_path in root_dir.rglob('*.*'):
            if (file_path.is_file()
                    and not any(exclude_dir in file_path.parents for exclude_dir in exclude_dirs)):
                zipf.write(file_path, file_path.relative_to(root_dir))
        # Zip all files in the Resources directory
        for file_path in resources_dir.rglob('*'):
            zipf.write(file_path, file_path.relative_to(root_dir))
    print("game.zip was (re)created successfully.")


# Function to start the HTTP server
def start_http_server():
    root_dir = Path(__file__).parent.resolve()
    subprocess.run(['python3', '-m', 'http.server'], cwd=root_dir)


if __name__ == "__main__":
    zip_game()
    start_http_server()