from time import sleep


def input_bytes():
    hexes = input().split()
    return ''.join(chr(int(h, 16)) for h in hexes)


if __name__ == '__main__':
    print("Welcome to signature database manager\n")
    filepath = 'D:\\Antivirus\\Server\\Signatures.bin'
    with open(filepath, "rb") as file:
        username = 'Igor Kirilin'
        real_password = 'qwerty'
        print("Signature base by " + username + "\nInput password: ")

    input_password = input()
    if real_password == input_password:
        print("Access permitted\n")
    else:
        print("Wrong password. Access denied. Terminating...\n")
        sleep(1)
        print("Good bay!")
        exit()

    print("Input 'A' to ADD new signature\n"
          "Input 'S' to SHOW all signatures\n"
          "Input 'EXIT' to TERMINATE manager")

    while True:
        print("\nInput command: ")
        command = input()
        if command == "A":
            print("Input signature name: ")
            signature_name = input()
            print("Input signature: ")
            signature = input()
            name = ("\n[" + signature_name + "]\n")
            with open(filepath, "ab") as file:
                file.write(name.encode('utf-8'))
                file.write(bytes.fromhex(signature))
        if command == "S":
            with open(filepath, "rb") as file:
                signatures = file.readlines()[2:]
                for signature in signatures:
                    print(signature.rstrip())
        if command == "EXIT":
            print("Manager is terminating...\n")
            sleep(1)
            print("Good bay!")
            break