import re

# Expresiones regulares usadas durante la ejecucion del script para validar las líneas del archivo de entrada y buscar información
regex_venta = r"^\((([A-Z][A-Za-z0-9\- ]+)|([1-9][0-9]*)-[0-9k])\.((#[A-Z1-9][A-Z0-9]*\b)|(\b[a-z0-9][a-z0-9.-]*\b))(\->)(([A-Z][A-Za-z0-9\- ]+)|([1-9][0-9]*)-[0-9kK])\.x((\d*[1-9]+\d*)(\.\d*[1-9]+\d*)?|0*\.[0-9]*[1-9]+\d*)\)$"
regex_empresa = r"^([A-Z][A-Za-z0-9\- ]+)\.([1-9][0-9]*)-[0-9kK]\.\[#[A-Z1-9][A-Z0-9]*\b-\$\d+(\.\d{3})*-\b[a-z0-9][a-z0-9.-]*\b(?:,#\b[A-Z1-9][A-Z0-9]*\b-\$\d+(\.\d{3})*-\b[a-z0-9][a-z0-9.-]*\b)*\]"
regex_verEmpresa = r"\bver_empresa\b\s(([A-Z][A-Za-z0-9\- ]+)|([1-9][0-9]*)-[0-9kK])"
regex_verVentas = r"\bver_ventas\b\s(([A-Z][A-Za-z0-9\- ]+)|([1-9][0-9]*)-[0-9kK])"
regex_BuscarMP = r"\bbuscar_MP\b\s(([A-Z][A-Za-z0-9\- ]+)|([1-9][0-9]*)-[0-9kK])"
regex_infoProducto = r"(#[A-Z1-9][A-Z0-9]*\b)-(\$\d+(\.\d{3})*)-(\b[a-z0-9][a-z0-9.-]*\b)"

class Empresa:
    def __init__(self, nombre, rut, productos):
        '''
        ***
        nombre : Tipo (String)
        rut : Tipo (String)
        productos : Tipo (Lista de Strings)
        ***
        None
        ***
        Esta función inicializa un objeto de la clase Empresa con el nombre, RUT y productos.
        '''
        
        self.nombre = nombre
        self.rut = rut
        self.productos = productos

class GrafoDirigido:
    #Inicializar el grafo con un diccionario vacío de empresas y otro de conexiones
    def __init__(self):
        '''
        ***
        None
        ***
        None
        ***
        Esta función inicializa un objeto de la clase GrafoDirigido con diccionarios vacíos de empresas y conexiones.
        '''
        self.empresas = {}
        self.matriz_adyacencia = {}

    #Agregar una empresa al grafo
    def agregar_empresa(self, empresa):
        '''
        ***
        empresa : Tipo (Objeto de la clase Empresa)
        ***
        None
        ***
        Esta función agrega una empresa a la línea de producción.
        Si la empresa ya existe en la línea de producción, se escribe un mensaje en el archivo 'output.txt' indicando que la empresa ya está presente.
        Si la empresa tiene el mismo RUT que otra empresa en la línea de producción, se escribe un mensaje en el archivo 'output.txt' indicando que el RUT ya está en uso.
        Si el RUT de la empresa no es válido, se escribe un mensaje en el archivo 'errores.txt' indicando que el RUT no es válido.
        Por ultimo el ID de  producto de la empresa a agregar ya esta asociado a otro producto en la red, se escribe un mensaje en el archivo 'output.txt' indicando que el
        producto ya esta asociado a otro producto en la red.
        '''
        #validando si la empresa tiene un rut valido segun la formula de validacion de rut
        if not validarRut(empresa.rut):
            escribirArchivo('errores.txt', f"El RUT '{empresa.rut}' de la empresa '{empresa.nombre}' no es válido.\n")
            return
        
        #verificando si la empresa ya existe
        if empresa.nombre in self.empresas:
            escribirArchivo('output.txt', f"'{empresa.nombre}' ya se encuentra en linea de produccion.")
            return
        elif empresa.rut in [emp.rut for emp in self.empresas.values()]:
            escribirArchivo('output.txt', f"'{empresa.rut}' ya se encuentra en linea de produccion.")
            return
        
        #verificando si el ID de  producto de la empresa a agregar ya esta asociado a otro producto en la red
        for producto in empresa.productos:
            info_producto_empresa = re.match(regex_infoProducto, producto)
            for emp in self.empresas.values():
                for p in emp.productos:
                    info_producto_otra_empresa = re.match(regex_infoProducto, p)
                    if info_producto_empresa.group(1) == info_producto_otra_empresa.group(1):
                        escribirArchivo('output.txt', f"El producto '{info_producto_empresa.group(1)}' de la empresa '{empresa.nombre}' ya está asociado a otro producto en la red.\n")
                        return
        
        #agregando la empresa al diccionario de empresas
        self.empresas[empresa.nombre] = empresa
        self.matriz_adyacencia[empresa.nombre] = {}
        print(f"Empresa {empresa.nombre} agregada.")

    def agregar_conexion(self, empresa_vende, producto, cantidad, empresa_compra, linea):
        '''
        ***
        empresa_vende : Tipo (String)
        producto : Tipo (String)
        cantidad : Tipo (String)
        empresa_compra : Tipo (String)
        linea : Tipo (String)
        ***
        None
        ***
        Esta función agrega una conexión entre dos empresas en la línea de producción.
        Si una o ambas empresas no existen en la línea de producción, se escribe un mensaje en el archivo 'output.txt' indicando que no se pudo crear la conexión.
        Si ambas empresas existen, se agrega la conexión entre ellas.
        Si la empresa que vende no existe en la línea de producción, se escribe un mensaje en el archivo 'errores.txt' indicando que no se pudo crear la conexión.
        Si la empresa que compra no existe en la línea de producción, se escribe un mensaje en el archivo 'errores.txt' indicando que no se pudo crear la conexión.
        '''
        empresa_vende_obj = self.buscar_empresa_por_nombre_o_rut(empresa_vende)
        empresa_compra_obj = self.buscar_empresa_por_nombre_o_rut(empresa_compra)

        #verificando si las empresas existen
        if not empresa_vende_obj:
            escribirArchivo('output.txt', f"No se pudo crear conexion no existe tal {empresa_vende}")
            return
        if not empresa_compra_obj:
            escribirArchivo('output.txt', f"No se pudo crear conexion no existe tal {empresa_compra}")
            return        
        if empresa_vende == empresa_compra:
            escribirArchivo('output.txt', f"No se pudo crear conexion {empresa_vende} no puede venderse a si mismo")
            return
        self.matriz_adyacencia[empresa_vende_obj.nombre][empresa_compra_obj.nombre] = (producto, cantidad)
        print(f"Conexión entre {empresa_vende_obj.nombre} y {empresa_compra_obj.nombre} agregada.")


    def buscar_empresa_por_nombre_o_rut(self, nombre_o_rut):
        '''
        ***
        nombre_o_rut : Tipo (String)
        ***
        Retorno Tipo Objeto de la clase Empresa
        ***
        Esta función busca una empresa en la línea de producción por su nombre o RUT.
        Si encuentra la empresa, devuelve el objeto de la empresa.
        Si no encuentra la empresa, devuelve None.
        '''
        for empresa in self.empresas.values():
            if empresa.nombre == nombre_o_rut or empresa.rut == nombre_o_rut:
                return empresa
        return None

    def imprimir_conexiones(self):
        '''
        ***
        None
        ***
        None
        ***
        Esta función imprime las conexiones entre empresas recorriendo la línea de producción e imprimiendo
        en el formato "empresa_vende vende cantidad unidades de producto a empresa_compra".
        '''
        for empresa_vende, conexiones in self.matriz_adyacencia.items():
            for empresa_compra, (producto, cantidad) in conexiones.items():
                print(f"{empresa_vende} vende {cantidad} unidades de {producto} a {empresa_compra}.")

# Función para parsear la línea y crear objetos Empresa
def parsear_linea(linea):
    '''
    ***
    linea : Tipo (String)
    ***
    Retorno Tipo Objeto de la clase Empresa
    ***
    Esta función recibe una línea de texto y la divide en el nombre de la empresa, el RUT y los productos.
    Crea un objeto de la clase Empresa con los datos obtenidos y lo retorna.
    '''
    resultado = re.split(r'\[', linea, 1)
    if len(resultado) == 2:
        encabezado = resultado[0]
        #Dividiendo en encabezado por puntos
        encabezado = re.split(r'\.', encabezado.rstrip('.'))
        #dividiendo los productos por comas
        productos = re.split(r',', resultado[1].rstrip(']\n'))


        return Empresa(encabezado[0], encabezado[1], productos)

# Función para parsear la línea de conexión y agregarla al grafo
def parsear_linea_conexion(linea, grafo):
    '''
    ***
    linea : Tipo (String)
    grafo : Tipo (Objeto de la clase GrafoDirigido)
    ***
    None
    ***
    Esta función recibe una línea de texto con una conexión entre empresas, las separa mediente una 
    expresion regular y la agrega al grafo mediante la función agregar_conexion.
    '''
    venta = re.match(regex_venta, linea)
    empresa_vende = venta.group(1)
    producto = venta.group(4)
    cantidad = venta.group(11)
    empresa_compra = venta.group(8)
    grafo.agregar_conexion(empresa_vende, producto, cantidad, empresa_compra,linea)

def validarRut(rut):
    '''
    ***
    rut : Tipo (String)
    ***
    Retorno Tipo Boolean
    ***
    Esta función recibe un RUT y verifica si es válido.
    Si el RUT es válido, devuelve True. Si no es válido, devuelve False.
    '''
    if re.match(r"^\d{1,2}\d{3}\d{3}-[\dk]$", rut):
        #Removiendo puntos y /o guión del RUT y convirtiendolo en una lista de dígitos
        rut = rut.replace('.', '').replace('-', '')
        rut_digits = [int(d) for d in rut[:-1]]  # Excluyendo el dígito verificador
        digito_verificador = rut[-1]

        # Serie numérica para multiplicar los dígitos del RUT
        serie_numerica = [2, 3, 4, 5, 6, 7]

        # Suma de los productos de cada dígito por la serie numérica
        suma_productos = sum(d * s for d, s in zip(rut_digits[::-1], serie_numerica * (len(rut_digits) // len(serie_numerica) + 1)))

        # Obtener el resto de la división por 11
        resto = suma_productos % 11

        # Calcular el dígito verificador
        if resto == 0:
            digito_calculado = '0'
        elif resto == 1:
            digito_calculado = 'k'
        else:
            digito_calculado = str(11 - resto)

        # Comprobar si el dígito verificador calculado coincide con el proporcionado
        return digito_calculado == digito_verificador

def escribirArchivo(nombre_archivo, contenido):
    '''
    ***
    nombre_archivo : Tipo (String)
    contenido : Tipo (String)
    ***
    None
    ***
    Esta función recibe un nombre de archivo y un contenido y escribe el contenido en el archivo.
    Si el archivo no existe, lo crea. Si ya existe, agrega el contenido al final del archivo.Por último, 
    si ocurre un error al escribir en el archivo, imprime un mensaje de error.
    '''
    try:
        with open(nombre_archivo, 'a+') as archivo:
            archivo.seek(0)  # Mover el puntero al inicio del archivo
            primer_caracter = archivo.read(1)
            if not primer_caracter:
                # El archivo está vacío
                archivo.write(contenido)
            else:
                archivo.write('\n' + contenido)
    except Exception as e:
        print(f"Error al escribir en el archivo '{nombre_archivo}': {str(e)}")

def buscarProducto(nombre_o_rut,itemID_itemName, grafo):
    '''
    ***
    nombre_o_rut : Tipo (String)
    itemID_itemName : Tipo (String)
    grafo : Tipo (Objeto de la clase GrafoDirigido)
    ***
    Retorno Tipo Diccionario
    ***
    Esta función busca un producto en la línea de producción de una empresa por su ID o nombre.
    Si encuentra el producto, devuelve un diccionario con el ID, precio y nombre del producto.
    Si no encuentra el producto, devuelve un mensaje indicando que no se encontró la empresa.
    '''
    empresa = grafo.buscar_empresa_por_nombre_o_rut(nombre_o_rut)
    if empresa:
        #bucando el porducto por su id y obteniendo el precio y nombre
        for producto in empresa.productos:
            infoProducto = re.match(regex_infoProducto, producto)


            if  infoProducto.group(1)== itemID_itemName or infoProducto.group(4)== itemID_itemName:
                producto_info = {
                    "ID": infoProducto.group(1),
                    "Precio": infoProducto.group(2),
                    "Nombre": infoProducto.group(4)
                }
                return producto_info
    else:
        return "No se encontró ninguna empresa con el nombre o RUT especificado."


def ver_informacion_empresa(nombre_o_rut, grafo):
    '''
    ***
    nombre_o_rut : Tipo (String)
    grafo : Tipo (Objeto de la clase GrafoDirigido)
    ***
    Retorno Tipo String
    ***
    Esta función busca una empresa en la línea de producción por su nombre o RUT mediante la funcion buscar_empresa_por_nombre_o_rut()  
    y devuelve un mensaje con la información de la empresa con el formato establecido en la tarea. Si no se encuentra la empresa, 
    se escribe un mensaje en el archivo 'output.txt' indicando que no se encontró la empresa.
    '''
    empresa = grafo.buscar_empresa_por_nombre_o_rut(nombre_o_rut)
    if empresa:
        informacion = f"VER EMPRESA :\n - {empresa.nombre}\n - {empresa.rut}\n - [\n"
        for producto in empresa.productos:
            informacion += f"   {producto}\n"
        informacion += " ]"
        escribirArchivo('output.txt', informacion)
    else:
        escribirArchivo('output.txt', "No se encontró ninguna empresa con el nombre/RUT especificado.(" + nombre_o_rut + ")")

def ver_ventas(nombre_o_rut, grafo):
    '''
    ***
    nombre_o_rut : Tipo (String)
    grafo : Tipo (Objeto de la clase GrafoDirigido)
    ***
    None
    ***
    Esta función busca una empresa en la línea de producción por su nombre o RUT mediante la funcion buscar_empresa_por_nombre_o_rut()
    y devuelve un mensaje con las ventas de la empresa con el formato establecido en la tarea. Si no se encuentra la empresa,
    se escribe un mensaje en el archivo 'output.txt' indicando que no se encontró la empresa.
    '''
    empresa = grafo.buscar_empresa_por_nombre_o_rut(nombre_o_rut)
    if empresa:
        ventas_info = f"VER VENTAS :\n - {empresa.nombre}\n - {empresa.rut}\n - [\n"
        if empresa.nombre in grafo.matriz_adyacencia:
            conexiones = grafo.matriz_adyacencia[empresa.nombre]
            for empresa_compra, (producto, cantidad) in conexiones.items():
                infoProducto = buscarProducto(nombre_o_rut, producto, grafo)
                precioUnitario = float(re.split(r'\$', infoProducto["Precio"])[1])           
                precio_final = "{:.3f}".format(precioUnitario * float(cantidad))
                ventas_info += f"   {infoProducto['ID']}  {infoProducto['Precio']} {infoProducto['Nombre']} x{cantidad} {precio_final} -> {empresa_compra}\n"
        ventas_info += " ]\n"

        escribirArchivo('output.txt', ventas_info)
    else:
        escribirArchivo('output.txt', "No se encontró ninguna empresa con el nombre/RUT especificado.(" + nombre_o_rut + ")")



# Crear el grafo y agregar empresas y conexiones
grafo = GrafoDirigido()

#Eliminando el archivo errores.txt si existe
with open('errores.txt', 'w') as errores:
    errores.write("")
    errores.close()

with open('output.txt', 'w') as output:
    output.write("")
    output.close()


#Leyndo el archivo linea por linea
with open('input.txt', 'r') as archivo:

    for linea in archivo:
        if re.match(regex_venta, linea):
            parsear_linea_conexion(linea, grafo)

        elif re.match(regex_empresa, linea):
            empresa = parsear_linea(linea)
            grafo.agregar_empresa(empresa)

        elif re.match(regex_verEmpresa, linea):
            resultado = re.match(regex_verEmpresa, linea)
            print(ver_informacion_empresa(resultado.group(1), grafo))
            print("\n")

        elif re.match(regex_verVentas, linea):
            resultado = re.match(regex_verVentas, linea)
            ver_ventas(resultado.group(1), grafo)
            print("\n")

        elif re.match(regex_BuscarMP, linea):
            resultado = re.match(regex_BuscarMP, linea)
            print("Se esta solicitando buscar el producto de la empresa ", resultado.group(1))
            print(linea)
        else:
            #escrbiendo el arcivho errores.txt
            escribirArchivo('errores.txt', linea)




#Imprimiendo el grafo
#print(grafo.matriz_adyacencia)
print(grafo.imprimir_conexiones())

