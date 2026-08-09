from excel import cargar_excel
from inventory import buscar_sku, contar_sku, total_lineas_excel
from database import (
    crear_base_datos,
    ver_conteos,
    sku_ya_contado,
    limpiar_conteos,
    total_lineas_contadas,
)


def contar_productos(inventario):

    while True:
        sku = input("\nIngrese el SKU (o escriba VOLVER): ")

        if sku.upper() == "VOLVER":
            break

        if sku_ya_contado(sku):
            print("\n⚠️ Este SKU ya fue contado.")

            respuesta = input("¿Desea volver a contarlo? (S/N): ")

            if respuesta.upper() != "S":
                continue

        resultado = buscar_sku(inventario, sku)

        contar_sku(resultado)


def mostrar_conteos():

    conteos = ver_conteos()

    print("\n========== CONTEOS ==========\n")

    if len(conteos) == 0:
        print("No hay conteos registrados.")
    else:
        for conteo in conteos:
            print(conteo)


def borrar_conteos():

    respuesta = input("\n¿Está seguro de borrar todos los conteos? (S/N): ")

    if respuesta.upper() == "S":
        limpiar_conteos()

        print("\n✅ Todos los conteos fueron eliminados.")

    else:
        print("\nOperación cancelada.")


def mostrar_progreso(inventario):

    total = total_lineas_excel(inventario)

    contadas = total_lineas_contadas()

    pendientes = total - contadas

    porcentaje = (contadas / total) * 100 if total > 0 else 0

    print("\n" + "=" * 50)
    print("        PROGRESO DEL INVENTARIO")
    print("=" * 50)

    print(f"Líneas del Excel : {total}")
    print(f"Líneas contadas  : {contadas}")
    print(f"Líneas pendientes: {pendientes}")
    print(f"Avance           : {porcentaje:.2f}%")


def main():

    crear_base_datos()

    inventario = cargar_excel("data/archivos_excel/inventario.xlsx")

    while True:
        print("\n" + "=" * 50)
        print("      SISTEMA DE INVENTARIO")
        print("=" * 50)
        print("1. Contar productos")
        print("2. Ver progreso")
        print("3. Ver conteos")
        print("4. Limpiar conteos")
        print("5. Salir")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            contar_productos(inventario)

        elif opcion == "2":
            mostrar_progreso(inventario)

        elif opcion == "3":
            mostrar_conteos()

        elif opcion == "4":
            borrar_conteos()

        elif opcion == "5":
            print("\nHasta luego.")
            break

        else:
            print("\n❌ Opción no válida.")


if __name__ == "__main__":
    main()
