from pathlib import Path
import pefile

def find_exe(filepath) -> list:
    files = sorted(Path(filepath).rglob("*.exe"))
    return list(map(str, files))


def scan(exe, flag) -> str or bool:
    names = []
    signatures = []
    with open("D:\\Antivirus\\Server\\Signatures.bin", "rb") as file:
        signatures_data = file.readlines()[3:]
        for i in range(len(signatures_data)):
            if i % 2 == 0:
                names.append(signatures_data[i].rstrip())
            else:
                signatures.append(signatures_data[i].rstrip())
    try:
        pe = pefile.PE(exe)
        print(exe)
        text_section = pe.sections[0].get_data()
        for i in range(len(signatures)):
            if flag:
                break
            if signatures[i] in text_section:
                print(str(names[i]) + " was founded")
    except pefile.PEFormatError:
        return False


if __name__ == '__main__':
    path = str(input())
    exes = find_exe(path)
    for exe in exes:
        scan(exe)

# C:\\Program Files (x86)\\DOSBox-0.74-3