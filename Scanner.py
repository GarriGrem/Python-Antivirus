from pathlib import Path
import pefile


# def find_exe(filepath) -> list or bool:
#     files = sorted(Path(filepath).rglob("*.exe"))
#     return list(map(str, files))

def find_exe(filepath) -> list or bool:
    mz = b'MZ'
    pe = b'PE'
    result = []
    files = sorted(Path(filepath).rglob("*.exe"))
    if len(files) == 0:
        return files
    for file in files:
        with open(file, 'rb') as current_file:
            data = current_file.read(500)
            if data.__contains__(mz) & data.__contains__(pe):
                result.append(file)
    return list(map(str, result))


def scan(exe) -> dict:
    names = []
    signatures = []
    with open("D:\\Antivirus\\Server\\Signatures.bin", "rb") as file:
        signatures_data = file.readlines()
        for i in range(len(signatures_data)):
            if i % 2 == 0:
                names.append(signatures_data[i].rstrip())
            else:
                signatures.append(signatures_data[i].rstrip())
    try:
        pe = pefile.PE(exe)
        # print(exe)
        text_section = pe.sections[0].get_data()
        for i in range(len(signatures)):
            if signatures[i] in text_section:
                print(str(names[i]) + " was founded")
                return {'exe': exe, 'name': names[i]}
    except pefile.PEFormatError:
        return False


if __name__ == '__main__':
    path = str(input())
    exes = find_exe(path)
    for exe in exes:
        scan(exe)

#  C:\TURBOC3

# C:\\Program Files (x86)\\DOSBox-0.74-3
# "D:\\Antivirus\\Server\\Signatures.bin"