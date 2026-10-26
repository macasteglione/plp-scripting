#!/usr/bin/python
import io
import subprocess as sp


def main():
    timido = sp.Popen(["python", "./timido.py"], stdin=sp.PIPE, stdout=sp.PIPE)
    nc = sp.Popen(
        ["nc", "192.168.166.180", "4444"], stdin=timido.stdout, stdout=sp.PIPE
    )

    timidoin = io.TextIOWrapper(timido.stdin, encoding="utf-8")
    ncout = io.TextIOWrapper(nc.stdout, encoding="utf-8")

    msg = "Hola Mundo"

    print("Le digo a Brandon: " + msg)
    timidoin.write(msg + "\n")
    timidoin.close()  # cierra la entrada de griton (también cierra griton.stdin)

    # rs = timidoout.readline()
    # print("JUAN dice: " + rs.strip())
    # timidoout.close()  # cierra la salida de timido (también cierra timido.stdout)
    ncout.close()
    nc.wait()  # espera a que termine griton
    timido.wait()  # espera a que termine timido


if __name__ == "__main__":
    main()
