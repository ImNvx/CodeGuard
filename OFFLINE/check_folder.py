from API.CodeGuard_Similarity import *
from pathlib import Path
import sys
from termcolor import colored, cprint

def get_folder_data(root_folder):
    root = Path(root_folder)

    folders_data = {}

    for folder in sorted(root.rglob("*")):
        if folder.is_dir():

            # fisierle direct din folderu asta
            file_array = [
                str(f)
                for f in sorted(folder.iterdir())
                if f.is_file()
            ]

            if file_array:
                scores = get_scores(file_array)

                folders_data[str(folder)] = {
                    "file_array": file_array,
                    "scores": scores
                }

    return folders_data


def get_scores(file_array):
    code_array = []
    for file_path in file_array:
        with open(file_path, 'r') as file:
            file_content = file.read()
            code_array.append(file_content)
    

    score_array = get_similarity(code_array)

    for i in range(len(score_array)):
        score_array[i] = round(score_array[i], 2)
    return score_array


def print_tree(root_folder, folders_data):
    root = Path(root_folder)

    def walk(folder, prefix=""):
        items = sorted(folder.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))

        folder_info = folders_data.get(str(folder), {})
        file_array = folder_info.get("file_array", [])
        scores = folder_info.get("scores", [])

        score_map = {
            path: score
            for path, score in zip(file_array, scores)
        }

        for index, item in enumerate(items):
            is_last = index == len(items) - 1
            connector = "└── " if is_last else "├── "

            if item.is_dir():
                print(f"{prefix}{connector}{item.name}/")

                extension = "    " if is_last else "│   "
                walk(item, prefix + extension)

            else:
                score = score_map.get(str(item), "?")
                if(score >= 70):
                    cprint(f"{prefix}{connector}[{score}] {item.name}", 'red', attrs=['bold'])
                elif(score >=50):
                    print(f"{prefix}{connector}[{score}] {item.name}")
                else:
                    cprint(f"{prefix}{connector}[{score}] {item.name}", 'green')

    print(f"{root.name}/")
    walk(root)


if __name__ == '__main__':
    root_path = input('path-ul catre folderul radacina: ')
    #root_path = "OFFLINE/example"
    folders_data = get_folder_data(root_path)

    print_tree(root_path, folders_data)

