# Servidor TFTP
# Núria Galera, C.Gustavo Vergara

import socket
from socket import AF_INET, SOCK_DGRAM
from struct import *
import random 

def crearPaquet(*args):
    #PRE: Argumentos para crear los paquetes
    #POST: Un string de bytes con los argumentos necesarios para enviar un DATA, ACK u OAK valido.
    
    #DATA
    if args[0] == 3:
        print("Creando paquete DATA\n", "Parametros: ")
        print("Numero de bloque -> ", args[1])
        print("Tamaño de datos -> ", len(args[2]))
        
        # Especificamos cantidad de bytes de los argumentos y añadimos los marcadores de estos
        formatter = '!HH{}s'
        # Especificamos el tamaño de los string, introducimos argumentos en los marcadores, 
        formatter = formatter.format(len(args[2]))   
        print("Formato -> ", formatter, "\n")
        # Creamos segmento en formato string de bytes indicando la codificación de los argumentos enviados.
        paquete = pack(formatter, 3, args[1], args[2])

    #ACK
    elif args[0] == 4:
        print("Creando paquete ACK\n", "Parametros: ")
        print("Numero de bloque -> ", args[1], "\n")
        
        # Creamos segmento en formato string de bytes, indicando la cantidad de bytes por argumento.
        paquete = pack('!HH', 4, args[1])

    #OAK
    elif args[0] == 6:
        print("Creando paquete OACK\n","Parametros: ")
        print("Opción -> ", args[1])
        print("Valor -> ", args[2])
        print("Opción2 -> ", args[3])
        print("Valor2 -> ", args[4])
        
        # Especificamos cantidad de bytes de los argumentos y añadimos los marcadores de estos
        formatter = '!H{}sB{}sB{}sB{}sB'
        # Especificamos el tamaño de los string, introducimos argumentos en los marcadores,
        formatter = formatter.format(len(args[1]), len(str(args[2])), len(args[3]), len(str(args[4])))
        print("Formato -> ", formatter,"\n")
        # Creamos segmento en formato string de bytes indicando la codificación de los argumentos enviados.
        paquete = pack(formatter, 6, bytes(args[1], 'utf-8'), 0, bytes(str(args[2]), 'utf-8'), 0, bytes(args[3], 'utf-8'), 0, bytes(str(args[4]), 'utf-8'), 0)	

    return paquete
	
def desempaquetar(tipus, contingut):
    #PRE: Tipo y contenido del segmento a decodificar. RRQ/WRQ, DATA o ACK
    #POST: Una tupla con los argumentos del segmento decodificado.

    #RRQ o WRQ
    if tipus == 'RQ':
        print("Contenido de RQ: ", contingut)
        print("Desempaquetando paquete RQ\n","Parametros: ")
        # Obtenemos opcode codificado de tamaño 2 bytes y decodificamos 
        opcode = contingut[0:2]
        opcode = unpack('!H', opcode)
        print("Opcode -> ", opcode[0])
        
        # Obtenemos 0 que indica donde acaba el final del nombre del archivo 
        nameEnd = contingut.find(b'\x00',2)
        # Obtenemos el nombre codificado y decodificamos
        filename = contingut[2:nameEnd].decode('utf-8')
        print("Filename -> ", filename)
        
        # Obtenemos 0 que indica donde acaba el final del modo 
        modeEnd = contingut.find(b'\x00', nameEnd+1)
        # Obtenemos el modo codificado y decodificamos
        mode = contingut[nameEnd+1:modeEnd].decode('utf-8')
        print("Mode -> ", mode)
        
        # Obtenemos 0 que indica donde acaba el final de la opción 
        opcioEnd = contingut.find(b'\x00', modeEnd+1)
        # Obtenemos la opción codificada y decodificamos
        opcio = contingut[modeEnd+1:opcioEnd].decode('utf-8')
        print("Opción -> ", opcio)
        
        # Obtenemos 0 que indica donde acaba el final del valor
        valorEnd = contingut.find(b'\x00', opcioEnd+1)
        # Obtenemos el valor codificado y decodificamos
        valor = contingut[opcioEnd+1:valorEnd].decode('utf-8')
        print("Valor -> ", valor)

        # Obtenemos 0 que indica donde acaba el final de la opcion 2 y del valor, despues los decodificamos
        opcio2End = contingut.find(b'\x00', valorEnd+1)
        opcio2 = contingut[valorEnd+1:opcio2End].decode('utf-8')
        valor2End = contingut.find(b'\x00', opcio2End+1)
        valor2 = contingut[opcio2End+1:valor2End].decode('utf-8')
        
        return opcode[0], filename, mode, opcio, int(valor), opcio2, int(valor2)

    #DATA
    elif tipus == 'DATA':
        print("Desempaquetando DATA\n", "Parametros: ")
        size = len(contingut)
        print("Tamaño paquete -> ", size)
        
        # Obtenemos opcode codificado de tamaño 2 bytes y decodificamos 
        opcode = contingut[0:2]
        opcode = unpack('!H', opcode)
        print("Opcode -> ", opcode[0])
        
        # Obtenemos el numero de bloque codificado de tamaño 2 bytes y decodificamos 
        block_num = contingut[2:4]
        block_num = unpack('!H', block_num)
        print("Número de bloque -> ", block_num[0])
        
        # Obtenemos el contenido del archivo codificado de tamaño hasta el final del segmento. 
        data = contingut[4:size]
        print("Tamaño del contenido -> ", len(data), "\n")
    
        return opcode[0], block_num[0], data
    
    #ACK
    elif tipus == 'ACK':
        print("Desempaquetando ACK\n", " Parametros: ")
        # Obtenemos opcode codificado de tamaño 2 bytes y decodificamos 
        opcode = contingut[0:2]
        opcode = unpack('!H', opcode)
        print("Opcode -> ", opcode[0])
        
        # Obtenemos el número de bloque codificado de tamaño 2 bytes y decodificamos 
        block_num = contingut[2:4]
        block_num = unpack('!H', block_num)
        print("Número de bloque -> ", block_num[0], "\n")

        return opcode[0], block_num[0]

def compruebaACK(num_paquete, contador, DATA, clientAddress, fitxer):

    #Comprobamos que el número de bloque del paquete recibido es igual al del enviado
    while num_paquete != contador:
        print("ERROR: Numero de paquete del ACK diferente al paquete enviado")
        # Creamos DATA
        DATA = crearPaquet(3, contador, content)
        # Enviamos DATA
        serverSocket.sendto(DATA, clientAddress)
        print("Paquete DATA se ha vuelto a enviar \n")
        
        #Comprobamos que el TID del cliente es el mismo que el acordado en la conexión
        nou_clientAddress = (0,0)
        while clientAddress != nou_clientAddress:
            # Esperamos ACK del cliente
            ACK, nou_clientAddress = serverSocket.recvfrom(valor)
            opcode, num_paquete = desempaquetar('ACK', ACK)
        
# ---- PROGRAMA PRINCIPAL ----
while True:
    # El servidor comienza escuchando por el puerto 69
    serverPort = 69

    # Crear un socket de escucha IPv4 por UDP
    server_escolta_Socket = socket.socket(AF_INET, SOCK_DGRAM)
  
    # Especificamos la escucha, introducimos la IP del host y el puerto de escucha 69
    server_escolta_Socket.bind((socket.gethostbyname(socket.gethostname()), serverPort))

    print("El Servidor esta listo para escuchar por el puerto 69 \n")

    # Esperamos paquete RQ
    RQ, clientAddress = server_escolta_Socket.recvfrom(512)
    print("Paquete RQ recibido \n")
    peticion, filename, mode, opcio, valor, opcio2, valor2 = desempaquetar('RQ', RQ);
    print("Paquete RQ, desempaquetado \n")

    #Abrimos nuevo Socket y establcemos un nuevo puerto aleatorio (RCF 1350)
    serverPort = random.randrange(49152, 65535)
    serverSocket = socket.socket(AF_INET, SOCK_DGRAM)
    # Especificamos la escucha, introducimos la IP del host y el puerto de escucha
    serverSocket.bind((socket.gethostbyname(socket.gethostname()), serverPort))
    print("El Servidor conectado al puerto", serverPort, "\n")
    
    # Empaquetamos OAK
    OAK = crearPaquet(6, opcio, valor, opcio2, valor2);
    print("Paquete OAK desempaquetado")
    # Enviamos OAK
    serverSocket.sendto(OAK, clientAddress)
    print("Paquete OAK enviado \n")
 
    if peticion == 1: #GET
        # Esperamos el ACK del cliente
        ACK, clientAddress = serverSocket.recvfrom(valor)
        opcode, num_paquete = desempaquetar('ACK', ACK)
        print("ACK desempaquetado \n")
        
        # Abrimos el fitxero a enviar en modo lectura por byte
        fitxer = open(filename,"rb")
        
        print('El client ', clientAddress,' vol un archiu \n')
    
        content = 1
        #Establecemos un contador de bloques enviados
        contador = 0

        #Enviamos contenido mientras el archivo sea leido
        while content:
            content = fitxer.read(valor)
            #Mostramos por pantalla lo que hemos leido
            print("Cotenido: ", content, "\n")
            
            contador = (contador + 1) % (2**16)
            print("Numero de bloque: ", contador, "\n")
            
            # Creamos DATA
            DATA = crearPaquet(3, contador, content)
            # Enviamos DATA
            serverSocket.sendto(DATA, clientAddress)
            print("Paquete DATA enviado \n")

            #Comprobamos que el TID del cliente es el mismo que el acordado en la conexión
            nou_clientAddress = (0,0)
            while clientAddress != nou_clientAddress:
                #Recibimos ACK del cliente
                ACK, nou_clientAddress = serverSocket.recvfrom(valor)
                opcode, num_paquete = desempaquetar('ACK', ACK)

            compruebaACK(num_paquete, contador, DATA, clientAddress, fitxer)
            print("Paquete enviado correctamente \n")

            # Si tamaño del contenido leido no es multiple del tamaño asignado, se sale del bucle, en caso contrario se envia un segmento DATA vacio
            if(len(content) < valor):
                content = 0
            
        print("El archivo se ha enviado correctamente. \n")
    
    elif peticion == 2: #PUT   
        #Abrimos el fitxero en modo escritura por byte
        fitxer = open(filename,"wb")
        print('EL client ', clientAddress,' vol enviar un archiu \n')
                                 
        # Esperamos segmento DATA
        DATA, clientAddress = serverSocket.recvfrom(valor+4)
        print("Paquete DATA recibido \n")
        block_num_anterior = 0

        # Entramos en el bucle siempre y cuando el paquete recibido se corresponda con el tamaño acordado del segmento DATA
        while len(DATA) == valor+4:
            #Desempaquetamos DATA y obtenemos los parametros 
            opcode, block_num, content = desempaquetar('DATA', DATA)

            #Comprobamos que el numero de bloque del segmento DATA es diferente al del ACK enviado
            if block_num != block_num_anterior:
                print("Nuevo paquete recibido, numero de bloque: ", block_num, "\n")
                #Escribimos en el archivo y enviamos ACK
                fitxer.write(content)
                ACK = crearPaquet(4, block_num)
                serverSocket.sendto(ACK, clientAddress)
                print("Paquete ACK enviado \n")

                #Cambiamos número de bloque de ACK enviado
                block_num_anterior = block_num
                
                #Mostramos por pantalla el contenido que hemos recibido de DATA
                print("Contenido: ", content)
                
            else:
                print("ERROR: Paquete con numero de bloque: ", block_num, " ya recibido")
                # Volvemos a enviar ACk
                ACK = crearPaquet(4, block_num)
                serverSocket.sendto(ACK, clientAddress)
                print("Se vuelve a enviar paquete ACK", block_num, "\n")

            # Comprobamos que el TID del cliente es el mismo que el acordado en la conexión
            nou_clientAddress = (0,0)
            while clientAddress != nou_clientAddress:
                #Recibimos nuevo segmento DATA
                DATA, nou_clientAddress = serverSocket.recvfrom(valor+4)
            print("Paquete DATA recibido \n")

        # Desempaquetamos último segmento DATA
        opcode, block_num, content = desempaquetar('DATA', DATA)

        # Escribimos en el archivo
        fitxer.write(content)
        print("Numero de bloque", block_num, "\n")
        #Enviamos último ACK
        ACK = crearPaquet(4, block_num)
        serverSocket.sendto(ACK, clientAddress)
        
        # Comprobamos que el último ACK se ha enviado correctamente (RFC 1350)
        serverSocket.settimeout(1)
        env = False
        while not env:
            try:
                #Comprobamos que el TID del cliente es el mismo que el acordado en la conexión
                nou_clientAddress = (0,0)
                while clientAddress != nou_clientAddress:
                    #Esperamos a recibir nuevo segmento DATA
                    DATA, clientAddress = serverSocket.recvfrom(valor+4)
                #Volvemos a enviar ACK
                ACK = crearPaquet(4, block_num)
                serverSocket.sendto(ACK, clientAddress)
                print("ERROR: ACK se ha vuelto a enviar")
                
            except socket.timeout:
                # Si al pasar un tiempo no se recibe nada más se confirma que el ACK ha sido bien recibido
                env = True
                
        print("El archivo se recibido correctamente. \n")
  
    fitxer.close()
    serverSocket.close()
