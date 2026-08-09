import os
import streamlit as st
import pandas as pd

from reports import generar_excel

from excel import cargar_excel

from database import (
    crear_base_datos,
    guardar_conteo,
    linea_ya_contada,
    ver_conteos,
    limpiar_conteos,
)

from inventory import buscar_sku, total_lineas_excel


# ==================================================
# CONFIGURACIÓN
# ==================================================

st.set_page_config(page_title="Almacén General", page_icon="📦", layout="wide")

crear_base_datos()

RUTA_EXCEL = "data/archivos_excel/inventario.xlsx"


# ==================================================
# SESSION STATE
# ==================================================

if "inventario" not in st.session_state:
    st.session_state.inventario = None

if "nombre_archivo" not in st.session_state:
    st.session_state.nombre_archivo = None


# ==================================================
# CARGAR INVENTARIO AUTOMÁTICAMENTE
# ==================================================

if st.session_state.inventario is None:
    if os.path.exists(RUTA_EXCEL):
        try:
            st.session_state.inventario = cargar_excel(RUTA_EXCEL)

            st.session_state.nombre_archivo = "inventario.xlsx"

        except Exception as error:
            st.error(f"Error cargando el inventario guardado: {error}")


# ==================================================
# ENCABEZADO
# ==================================================

st.title("📦 Almacén General")

st.caption("Sistema de conteo físico de inventario")


# ==================================================
# ACTUALIZAR INVENTARIO
# ==================================================

with st.expander("📄 Actualizar inventario del día"):
    st.write(
        "Esta opción es opcional. "
        "Utilízala únicamente cuando tengas "
        "un Excel actualizado."
    )

    archivo = st.file_uploader("Seleccionar Excel", type=["xlsx"])

    if archivo is not None:
        if st.button("📥 Usar este inventario", type="primary"):
            try:
                nuevo_inventario = cargar_excel(archivo)

                # Guardar físicamente el Excel nuevo
                with open(RUTA_EXCEL, "wb") as destino:
                    destino.write(archivo.getbuffer())

                st.session_state.inventario = nuevo_inventario

                st.session_state.nombre_archivo = archivo.name

                st.success("✅ Inventario actualizado correctamente.")

                st.rerun()

            except Exception as error:
                st.error(f"Error cargando el Excel: {error}")


# ==================================================
# COMPROBAR INVENTARIO
# ==================================================

if st.session_state.inventario is None:
    st.warning("No existe ningún inventario cargado.")

    st.info("Abre 'Actualizar inventario del día' y carga un archivo Excel.")

    st.stop()


inventario = st.session_state.inventario


st.write(f"📄 **Inventario actual:** {st.session_state.nombre_archivo}")


# ==================================================
# CALCULAR PROGRESO
# ==================================================

total = total_lineas_excel(inventario)

lineas_contadas = 0


for indice, fila in inventario.iterrows():
    contado = linea_ya_contada(fila["SKU"], fila["Lote"], fila["Ubicacion"])

    if contado:
        lineas_contadas += 1


pendientes = max(total - lineas_contadas, 0)


if total > 0:
    porcentaje = lineas_contadas / total

else:
    porcentaje = 0


porcentaje = min(porcentaje, 1.0)


# ==================================================
# DASHBOARD
# ==================================================

st.divider()

st.subheader("📊 Progreso del inventario")


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric("Total líneas", total)


with col2:
    st.metric("Contadas", lineas_contadas)


with col3:
    st.metric("Pendientes", pendientes)


with col4:
    st.metric("Avance", f"{porcentaje * 100:.1f}%")


st.progress(porcentaje)


# ==================================================
# LÍNEAS PENDIENTES
# ==================================================

st.divider()


with st.expander(f"📋 Ver líneas pendientes ({pendientes})"):
    lineas_pendientes = []

    for indice, fila in inventario.iterrows():
        contado = linea_ya_contada(fila["SKU"], fila["Lote"], fila["Ubicacion"])

        if not contado:
            caducidad = fila["Caducidad"]

            # ======================================
            # FORMATEAR CADUCIDAD
            # ======================================

            if pd.isna(caducidad):
                caducidad_texto = "-"

            elif hasattr(caducidad, "strftime"):
                caducidad_texto = caducidad.strftime("%d/%m/%Y")

            else:
                caducidad_texto = str(caducidad)

            lineas_pendientes.append(
                {
                    "SKU": fila["SKU"],
                    "Lote": fila["Lote"],
                    "Descripción": fila["Descripcion"],
                    "Ubicación": fila["Ubicacion"],
                    "Caducidad": caducidad_texto,
                    "Stock ERP": fila["Stock"],
                }
            )

    # ==============================================
    # MOSTRAR PENDIENTES
    # ==============================================

    if len(lineas_pendientes) == 0:
        st.success("✅ No quedan líneas pendientes.")

    else:
        tabla_pendientes = pd.DataFrame(lineas_pendientes)

        st.dataframe(tabla_pendientes, use_container_width=True, hide_index=True)


# ==================================================
# BUSCAR SKU
# ==================================================

st.divider()

st.subheader("🔍 Buscar SKU")


sku = st.text_input("SKU", placeholder="Ingrese el SKU")


# ==================================================
# RESULTADO DE BÚSQUEDA
# ==================================================

if sku:
    resultado = buscar_sku(inventario, sku)

    if resultado.empty:
        st.error("❌ SKU no encontrado.")

    else:
        descripcion = str(resultado.iloc[0]["Descripcion"])

        st.success(f"{sku} - {descripcion}")

        st.write(f"**Líneas encontradas: {len(resultado)}**")

        # ==================================================
        # MOSTRAR CADA LÍNEA
        # ==================================================

        for indice, fila in resultado.iterrows():
            sku_fila = str(fila["SKU"])

            lote = str(fila["Lote"])

            ubicacion = str(fila["Ubicacion"])

            descripcion_fila = str(fila["Descripcion"])

            caducidad = fila["Caducidad"]

            stock = int(fila["Stock"])

            # ==============================================
            # CADUCIDAD
            # ==============================================

            if pd.isna(caducidad):
                caducidad_texto = "-"

            elif hasattr(caducidad, "strftime"):
                caducidad_texto = caducidad.strftime("%d/%m/%Y")

            else:
                caducidad_texto = str(caducidad)

            # ==============================================
            # VER SI LA LÍNEA YA FUE CONTADA
            # ==============================================

            anterior = linea_ya_contada(sku_fila, lote, ubicacion)

            # ==============================================
            # TARJETA DE LA LÍNEA
            # ==============================================

            with st.container(border=True):
                st.write(f"### {descripcion_fila}")

                col1, col2 = st.columns(2)

                # ------------------------------------------
                # INFORMACIÓN
                # ------------------------------------------

                with col1:
                    st.write(f"**SKU:** {sku_fila}")

                    st.write(f"**Lote:** {lote}")

                    st.write(f"📍 **Ubicación:** {ubicacion}")

                with col2:
                    st.write(f"📅 **Caducidad:** {caducidad_texto}")

                    st.write(f"📦 **Stock ERP:** {stock}")

                # ==========================================
                # ESTADO
                # ==========================================

                if anterior:
                    st.success("✅ Línea ya contada")

                    valor_inicial = int(anterior[0])

                    diferencia_anterior = int(anterior[1])

                    st.write(f"**Diferencia guardada:** {diferencia_anterior:+d}")

                else:
                    st.warning("🟡 Pendiente")

                    valor_inicial = 0

                # ==========================================
                # FORMULARIO INDIVIDUAL
                # ==========================================

                with st.form(key=(f"form_{indice}_{sku_fila}_{lote}_{ubicacion}")):
                    conteo = st.number_input(
                        "Conteo físico",
                        min_value=0,
                        value=valor_inicial,
                        step=1,
                        key=(f"conteo_{indice}_{sku_fila}_{lote}_{ubicacion}"),
                    )

                    observacion = st.text_area(
                        "Observación",
                        value=anterior[2] if anterior else "",
                        placeholder="Escribe una observación (opcional)",
                        key=(f"obs_conteo_{indice}_{sku_fila}_{lote}_{ubicacion}"),
                    )

                    # ======================================
                    # DIFERENCIA
                    # ======================================

                    diferencia_nueva = int(conteo) - int(stock)

                    st.write(f"**Diferencia:** {diferencia_nueva:+d}")

                    # ======================================
                    # BOTÓN INDIVIDUAL
                    # ======================================

                    guardar = st.form_submit_button(
                        "💾 Guardar esta línea",
                        type="primary",
                        use_container_width=True,
                    )

                    # ======================================
                    # GUARDAR SOLO ESTA LÍNEA
                    # ======================================

                    if guardar:
                        guardar_conteo(
                            sku_fila,
                            lote,
                            descripcion_fila,
                            ubicacion,
                            caducidad_texto,
                            stock,
                            conteo,
                            observacion,
                        )

                        st.success("✅ Línea guardada correctamente.")

                        st.rerun()


# ==================================================
# CONTEOS REALIZADOS
# ==================================================

st.divider()

with st.expander("📋 Ver conteos realizados"):
    datos = ver_conteos()

    if len(datos) == 0:
        st.info("Todavía no hay conteos realizados.")

    else:
        # ==========================================
        # CREAR TABLA
        # ==========================================

        tabla = pd.DataFrame(
            datos,
            columns=[
                "SKU",
                "Lote",
                "Descripción",
                "Ubicación",
                "Caducidad",
                "Stock ERP",
                "Conteo físico",
                "Diferencia",
                "Observación",
            ],
        )

        # ==========================================
        # FILTRO
        # ==========================================

        filtro = st.selectbox(
            "Mostrar",
            [
                "Todos",
                "Con diferencia",
                "Sin diferencia",
                "Diferencia positiva",
                "Diferencia negativa",
            ],
        )

        # ==========================================
        # APLICAR FILTRO
        # ==========================================

        if filtro == "Con diferencia":
            tabla_filtrada = tabla[tabla["Diferencia"] != 0]

        elif filtro == "Sin diferencia":
            tabla_filtrada = tabla[tabla["Diferencia"] == 0]

        elif filtro == "Diferencia positiva":
            tabla_filtrada = tabla[tabla["Diferencia"] > 0]

        elif filtro == "Diferencia negativa":
            tabla_filtrada = tabla[tabla["Diferencia"] < 0]

        else:
            tabla_filtrada = tabla

        st.write(f"**Registros encontrados: {len(tabla_filtrada)}**")

        if tabla_filtrada.empty:
            st.info("No hay registros para este filtro.")

        else:
            st.dataframe(
                tabla_filtrada,
                use_container_width=True,
                hide_index=True,
            )


# ==================================================
# DESCARGAR EXCEL
# ==================================================

st.divider()

st.subheader("📥 Exportar conteo")

datos = ver_conteos()

if len(datos) == 0:
    st.info("Todavía no hay conteos para exportar.")

else:
    archivo_excel = generar_excel(datos)

    st.download_button(
        label="📥 Descargar conteo en Excel",
        data=archivo_excel,
        file_name="Conteo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
# ==================================================
# OPCIONES
# ==================================================

st.divider()


with st.expander("⚙️ Opciones"):
    st.warning("Reiniciar los conteos eliminará todo el trabajo realizado.")

    confirmar = st.checkbox("Confirmo que quiero reiniciar todos los conteos")

    if st.button("🗑️ Reiniciar conteos", use_container_width=True):
        if confirmar:
            limpiar_conteos()

            st.success("✅ Conteos eliminados.")

            st.rerun()

        else:
            st.warning("⚠️ Debes confirmar primero.")
