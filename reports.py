import pandas as pd
from io import BytesIO


def generar_excel(datos):

    columnas = [
        "Material",
        "Lote",
        "Texto breve de material",
        "Parte Número",
        "Ubic WM",
        "FeCaduc/FePreferCons",
        "stock Disponible",
        "Conteo físico",
        "Diferencia",
        "Observación",
    ]

    df = pd.DataFrame(
        datos,
        columns=columnas,
    )

    salida = BytesIO()

    with pd.ExcelWriter(
        salida,
        engine="openpyxl",
    ) as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Conteo",
        )

        hoja = writer.sheets["Conteo"]

        # Ajustar automáticamente el ancho
        # de las columnas
        for columna in hoja.columns:
            longitud = max(
                len(str(celda.value)) if celda.value is not None else 0
                for celda in columna
            )

            hoja.column_dimensions[columna[0].column_letter].width = longitud + 3

    salida.seek(0)

    return salida
