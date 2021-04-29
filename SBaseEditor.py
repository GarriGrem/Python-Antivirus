from time import sleep


def input_bytes():
    hexes = input().split()
    return ''.join(chr(int(h, 16)) for h in hexes)


if __name__ == '__main__':
    print("Здесь вы можете добавить сигнатуру в базу.")
    filepath = 'D:\\Antivirus\\Server\\Signatures.bin'
    with open(filepath, "rb") as file:
        username = file.readline().decode('utf-8').rstrip()
        real_password = '12345'
        print("Автор программы Кирилин Игорь. \nВведите пароль")

    input_password = input()
    if real_password == input_password:
        print("Пароль верный\n")
    else:
        print("Неправильный пароль. Выход из программы.\n")
        sleep(1)
        exit()

    print("Введите '1', чтобы добавить сигнатуру.\n"
          "Введите '2', чтобы посмотреть сигнатуры из файла.\n"
          "Введите '0', чтобы выйти из программы.\n")

    while True:
        print("\nОжидание ввода... ")
        command = input()
        if command == '1':
            print("Введите имя сигнатуры: ")
            signature_name = input()
            print("Введите сигнатуру в формате XXXX XXXX XXXX: ")
            signature = input()
            name = ("\n[" + signature_name + "]\n")
            with open(filepath, "ab") as file:
                file.write(name.encode('utf-8'))
                file.write(bytes.fromhex(signature))
        if command == '2':
            with open(filepath, "rb") as file:
                signatures = file.readlines()[2:]
                for signature in signatures:
                    print(signature.rstrip())
        if command == '0':
            print("Выход из программы\n")
            sleep(1)
            break
