#!/usr/bin/python
import io
import subprocess as sp

def main():
  griton = sp.Popen(
    ['./griton.py'],
    stdin=sp.PIPE,
    stdout=sp.PIPE
    )
  timido = sp.Popen(
    ['./timido.py'],
    stdin=griton.stdout,
    stdout=sp.PIPE
    )

  gritonin = io.TextIOWrapper(
    griton.stdin,
    encoding='utf-8'
  )
  timidoout = io.TextIOWrapper(
    timido.stdout,
    encoding='utf-8'
  )

  msg = 'Hola Mundo'

  print('Le digo a griton: ' + msg)
  gritonin.write(msg+'\n')
  gritonin.close()        # cierra la entrada de griton (también cierra griton.stdin)
  
  rs = timidoout.readline()
  print('Timido dice: ' + rs.strip())
  timidoout.close()       # cierra la salida de timido (también cierra timido.stdout)

  griton.wait()           # espera a que termine griton
  timido.wait()           # espera a que termine timido

if __name__ == "__main__":
  main()
