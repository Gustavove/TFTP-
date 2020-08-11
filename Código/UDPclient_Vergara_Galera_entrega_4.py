# Cliente TFTP
# Núria Galera, C.Gustavo Vergara

import socket
from socket import AF_INET, SOCK_DGRAM
from struct import *

def crearPaquet(*args):
    #PRE: Argumentos para crear los paquetes
    #POST: Un string de bytes con los argumentos necesarios para enviar un RRQ/WRQ, DATA o ACK valido.
    
    paquete = b'0'
    
    #RRQ / WRQ
    if args[0] == 1 or args[0] == 2:
        print("Creando paquete RRQ\n", "Parametros: ")
        print("Nombre del archivo -> ", args[1])
        print("Modo -> ", args[2])
        print("Opción -> ", args[3])
        print("Valor -> ", args[4])
        
        # Especificamos cantidad de bytes de los argumentos y añadimos los marcadores de estos
        formatter = '!H{}sB{}sB{}sB{}sB{}sB{}sB'
        # Especificamos el tamaño de los string, introducimos argumentos en los marcadores, 
        formatter = formatter.format(len(args[1]), len(args[2]), len(args[3]), len(str(args[4])), len("tsize"), len("0"))
        print("Formato -> ", formatter, "\n")
        # Creamos segmento en formato string de bytes indicando la codificación de los argumentos enviados.
        paquete = pack(formatter, args[0], bytes(args[1], 'utf-8'), 0, bytes(args[2], 'utf-8'), 0, bytes(args[3], 'utf-8'), 0, bytes(str(args[4]), 'utf-8'), 0, bytes("tsize", 'utf-8'), 0, bytes("0", 'utf-8'), 0)
        
            
    #DATA
    elif args[0] == 3:
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
    else:
        print("Creando paquete ACK\n", "Parametros: ")
        print("Numero de bloque -> ", args[1], "\n")
        
        # Creamos segmento en formato string de bytes, indicando la cantidad de bytes por argumento.
        paquete = pack('!HH', 4, args[1])
        
    return paquete
	
def desempaquetar(tipus, contingut):
    #PRE: Tipo y contenido del segmento a decodificar. DATA, ACK u OAK
    #POST: Una tupla con los argumentos del segmento decodificado.

   #DATA
   if tipus == 'DATA':
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

   #OACK
   elif tipus == 'OACK':
    print("Desempaquetando OACK\n", "Parametros: ")
    print(contingut)
    # Optenemos opcode codificado de tamaño 2 bytes y decodificamos 
    opcode = contingut[0:2]
    opcode = unpack('!H', opcode)
    print("Opcode -> ", opcode[0])
    
    # Obtenemos 0 que indica donde acaba el final de la opción 
    opcioEnd = contingut.find(b'\x00', 2)
    # Obtenemos la opción codificada y decodificamos 
    opcio = contingut[2:opcioEnd].decode('utf-8')
    print("Opció -> ", opcio)
    
    # Obtenemos 0 que indica donde acaba el final del valor
    valorEnd = contingut.find(b'\x00', opcioEnd+1)
    # Obtenemos valor codificado y decodificamos
    valor = contingut[opcioEnd+1:valorEnd].decode('utf-8')
    print("Valor -> ", valor, "\n")

    return opcode[0], opcio, valor

def enviaACK(DATA, clientSocket, serverName, serverPort):
    # PRE: Segmento DATA, tupla con la información del cliente, IP servidor, puerto destino
    # POST: El número de bloque del ACK enviado

    #Desempaquetamos segmento DATA
    opcode, block_num, content = desempaquetar('DATA', DATA)
    print("DATA desempaquetado", "\n")

    # Escribimos en el archivo el contenido extraido del segmento DATA
    fitxer.write(content)
    print("Contenido del archivo: ", content, "\n")
    
    #Creamos ACK y lo enviamos
    ACK = crearPaquet(4, block_num)
    clientSocket.sendto(ACK,(serverName,serverPort))
    print("ACK con numero de bloque ", block_num, " enviado \n")
    
    return block_num

def recibeACK(block_num, DATA, serverName, serverPort):
    # PRE: Número de bloque del paquete enviado, segmento DATA, IP servidor, puerto destino
    # POST: El número de bloque del ACK enviado
    
    reciv = False          
    #Espera a recibir bien el ACK del server
    while not reciv:
        try:
            ACK, serverAddress = clientSocket.recvfrom(512)
            opcode, num = desempaquetar('ACK', ACK)
            print("Nuevo ACK ", num, " recibido correctamente \n")
            #Si el número de bloque del ACK recibido es igual al número del bloque enviado se sale del bucle
            if num == block_num:
                reciv = True
                    
        except socket.timeout:
            # Si se produce un time_out se vuelve a enviar el segmento DATA
            print("Paquete no recibido corectamente (Time_Out)")
            clientSocket.sendto(DATA,(serverName,serverPort))
            print("Paquete DATA enviado \n")

# ---- PROGRAMA PRINCIPAL ----
# Obtenemos la IP del servidor introducida por el usuario
host = input('Introduce el identificador del servidor: ')
serverName = host
# Para hacer la primera transmissión asignamos al servidor el puerto 69
serverPort = 69
# Solicitud IPv4 con comunicación UDP
clientSocket = socket.socket(AF_INET, SOCK_DGRAM)
# Establecemos tiempo de espera de 1 segundo
clientSocket.settimeout(1)
# Leemos los inputs del usuario
peticion = input('Elige peticion a usar: ') # Petición a usar GET/PUT
size_paquete = int(input('Escribe el numero de bytes a transmitir:')) # Tamaño de segmentos DATA (RFC 1783)
file_name = input('Escribe el nombre del archivo a recibir/enviar:') # Nombre del archivo a enviar o recibir
print('Contacto con el servidor ', serverName, ' por el puerto ', serverPort, '')

if peticion == 'GET':
    #Creamos paquete RRQ compatible con RFC 1783, en modo octeto y se lo enviamos al servidor.
    RRQ = crearPaquet(1,file_name,'octet', 'blksize', size_paquete)
    #Enviamos RRQ al servidor con puerto destino 69
    clientSocket.sendto(RRQ,(serverName,serverPort))
    print("Paquete RRQ enviado \n")

    # Abrimos el fichero a escribir en modo escritura de bytes
    fitxer = open(file_name,"wb")

    # Esperamos recibir paquete OAK del servidor, obtenemos la IP y el TID del servidor
    OACK, serverAddress = clientSocket.recvfrom(512)
    print("OAK recibido")
    opcode, opcio, size_paquete = desempaquetar('OACK', OACK )

    print('Conexión establecida con el servidor ', serverAddress[0], ' por el puerto ', serverAddress[1], '')

    #Creamos paquete ACK y establecemos el tamaño de los segmentos según la respuesta del servidor
    size_paquete = int(size_paquete)
    ACK = crearPaquet(4, 0)
    clientSocket.sendto(ACK,serverAddress)
    print("Paquete ACK enviado \n")
    clientSocket.settimeout(3)
    # Esperamos a recibir el primer paquete DATA 
    DATA, serverAddress = clientSocket.recvfrom(size_paquete+4)
    print("Paquete DATA recibido \n")
    clientSocket.settimeout(1)
    # Entramos en el bucle siempre y cuando el paquete recibido se corresponda con el tamaño especificado del segmento DATA
    while len(DATA) == size_paquete+4:
        #Al recibir correctamente el segmento DATA enviamos un ACK
        block_num = enviaACK(DATA, clientSocket, serverAddress[0], serverAddress[1])
        reciv = False

        # Al recibir un nuevo segmento DATA comprobamos que se recibe el segmento DATA correcto 
        while not reciv:
            try:
                DATA, serverAddress = clientSocket.recvfrom(size_paquete+4)
                print("Comprobando que el numero de bloque sea correcto....")
                opcode, block_num_reciv, content = desempaquetar('DATA', DATA)
                # Comprobamos que el numero de bloque del nuevo segmento DATA sea diferente al escrito anteriormente
                if block_num_reciv != block_num:
                    print("Nuevo DATA recibido correctamente \n")
                    reciv = True
                else:
                    print("ERROR: Número de bloque incorrecto \n")
          
            except socket.timeout:
                # En caso de time_out se vuelve a enviar el ACK
                print("ERROR: Paquete no recibido corectamente (Time_Out)")
                ACK = crearPaquet(4, block_num)
                clientSocket.sendto(ACK,serverAddress)
                print("Paquete ACK enviado \n")

    # Una vez recibido el ultimo segmento DATA del archivo enviado por el servidor, enviamos el último ACK
    block_num = enviaACK(DATA, clientSocket, serverAddress[0], serverAddress[1])
    env = False
    # Comprobamos que el ACK se ha enviado correctamente (RFC 1350)
    while not env:
        try:
            DATA, serverAddress = clientSocket.recvfrom(size_paquete+4)
            # Si se recibe un nuevo segmento DATA se vuelve a enviar el ACK
            print("ERROR: ACK no enviado correctamente \n")
            ACK = crearPaquet(4, block_num)
            clientSocket.sendto(ACK,serverAddress)
        except socket.timeout:
            # Si al pasar un tiempo no se recibe nada más se confirma que el servidor ha cerrado conexión
            env = True
            
    print("El archivo se ha recibido correctamente.")
  
elif peticion == 'PUT':
    # Creamos paquete WRQ compatible con RFC 1783, en modo octeto y se lo enviamos al servidor
    WRQ = crearPaquet(2,file_name,'octet','blksize',size_paquete)
    clientSocket.sendto(WRQ,(serverName,serverPort))
    print("Paquete WRQ enviado \n")
    clientSocket.settimeout(3)
    # Esperamos recibir paquete OAK del servidor, obtenemos la IP y el TID del servidor           
    OACK, serverAddress = clientSocket.recvfrom(512)
    print("OAK recibido")
    opcode, opcio, size_paquete = desempaquetar('OACK', OACK )
    clientSocket.settimeout(1)
    print('Conexión establecida con el servidor ', serverAddress[0], ' por el puerto ', serverAddress[1], '')
                       
    # Establecemos el tamaño de los segmentos según la respuesta del servidor
    size_paquete = int(size_paquete)
  
    # Se abre el archivo en modo lectura de bytes
    fitxer = open(file_name, "rb")
    content = 1
    block_num = 0

    while content:
        # Leemos el archivo según el tamaño de segmento DATA asignado
        content = fitxer.read(size_paquete)
        print("Contenido: ", content, "\n")
        # Establecemos el número de bloque (RFC 1350)
        block_num = (block_num + 1) % (2**16)
        print("Numero de bloque: ", block_num, "\n")
        # Creamos segmento DATA y lo enviamos al servidor
        DATA = crearPaquet(3, block_num, content)
        clientSocket.sendto(DATA,serverAddress)
        print("Paquete DATA enviado \n")
                       
        # Esperamos a recibir bien el ACK del servidor
        recibeACK(block_num, DATA, serverAddress[0], serverAddress[1])

        # Si tamaño del archivo leido no es multiplo del tamaño asignado, se sale del bucle, en caso contrario se envia un segmento DATA vacio
        if(len(content) < size_paquete):
                content = 0
            
    print("El archivo se ha enviado correctamente.")

# Cerramos opertura del archivo y cerramos socket
fitxer.close()
clientSocket.close()
