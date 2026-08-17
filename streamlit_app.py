import streamlit as st
import pandas as pd

from reports import generar_excel
from excel import cargar_excel

from database import (
    crear_base_datos,
    guardar_inventario,
    obtener_inventario,
    limpiar_inventario,
    guardar_conteo,
    obtener_todos_los_conteos,
    limpiar_conteos,
)

from inventory import (
    buscar_material,
    total_lineas_excel,
)


# ==================================================
# CONFIGURACIÓN
# ==================================================

st.set_page_config(
    page_title="Almacén General",
    page_icon="📦",
    layout="wide",
)

crear_base_datos()


# ==================================================
# SESSION STATE
# ==================================================

if "inventario" not in st.session_state:
    inventario_guardado = obtener_inventario()
    st.session_state.inventario = inventario_guardado

if "nombre_archivo" not in st.session_state:
    st.session_state.nombre_archivo = (
        "Inventario guardado" if st.session_state.inventario is not None else None
    )


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

    archivo = st.file_uploader(
        "Seleccionar Excel",
        type=["xlsx"],
    )

    if archivo is not None:
        if st.button(
            "📥 Usar este inventario",
            type="primary",
        ):
            try:
                nuevo_inventario = cargar_excel(archivo)

                # Guardar inventario permanentemente en SQLite
                guardar_inventario(nuevo_inventario)

                # Actualizar memoria de la sesión
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
# CARGAR TODOS LOS CONTEOS UNA SOLA VEZ
# ==================================================

datos_conteos = obtener_todos_los_conteos()


# ==================================================
# CREAR DICCIONARIO DE CONTEOS
# ==================================================

conteos_dict = {}

for registro in datos_conteos:
    (
        material,
        lote,
        texto_breve_material,
        parte_numero,
        ubic_wm,
        fe_caduc_fe_prefer_cons,
        stock_disponible,
        conteo_fisico,
        diferencia,
        observacion,
    ) = registro

    clave = (
        str(material),
        str(lote),
        str(ubic_wm),
    )

    conteos_dict[clave] = {
        "conteo_fisico": conteo_fisico,
        "diferencia": diferencia,
        "observacion": observacion or "",
    }


# ==================================================
# OBTENER CONTEO DESDE MEMORIA
# ==================================================


def obtener_conteo_memoria(
    material,
    lote,
    ubic_wm,
):

    clave = (
        str(material),
        str(lote),
        str(ubic_wm),
    )

    return conteos_dict.get(clave)


# ==================================================
# CALCULAR PROGRESO
# ==================================================

total = total_lineas_excel(inventario)

lineas_contadas = 0


for _, fila in inventario.iterrows():
    clave = (
        str(fila["Material"]),
        str(fila["Lote"]),
        str(fila["Ubic WM"]),
    )

    if clave in conteos_dict:
        lineas_contadas += 1


pendientes = max(
    total - lineas_contadas,
    0,
)


if total > 0:
    porcentaje = lineas_contadas / total

else:
    porcentaje = 0


porcentaje = min(
    porcentaje,
    1.0,
)


# ==================================================
# DASHBOARD
# ==================================================

st.divider()

st.subheader("📊 Progreso del inventario")


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Total líneas",
        total,
    )


with col2:
    st.metric(
        "Contadas",
        lineas_contadas,
    )


with col3:
    st.metric(
        "Pendientes",
        pendientes,
    )


with col4:
    st.metric(
        "Avance",
        f"{porcentaje * 100:.1f}%",
    )


st.progress(porcentaje)


# ==================================================
# LÍNEAS PENDIENTES
# ==================================================

st.divider()


with st.expander(f"📋 Ver líneas pendientes ({pendientes})"):
    lineas_pendientes = []

    for _, fila in inventario.iterrows():
        clave = (
            str(fila["Material"]),
            str(fila["Lote"]),
            str(fila["Ubic WM"]),
        )

        contado = conteos_dict.get(clave)

        if not contado:
            fecha = fila["FeCaduc/FePreferCons"]

            if pd.isna(fecha):
                fecha_texto = "-"

            elif hasattr(
                fecha,
                "strftime",
            ):
                fecha_texto = fecha.strftime("%d/%m/%Y")

            else:
                fecha_texto = str(fecha)

            lineas_pendientes.append(
                {
                    "📦 Material": fila["Material"],
                    "📝 Descripción": fila["Texto breve de material"],
                    "🔖 Parte Número": fila["Parte Número"],
                    "📍 Ubicación": fila["Ubic WM"],
                    "🏷️ Lote": fila["Lote"],
                    "📅 Fecha vencimiento": fecha_texto,
                    "📊 Stock disponible": fila["stock Disponible"],
                }
            )

    if len(lineas_pendientes) == 0:
        st.success("✅ No quedan líneas pendientes.")

    else:
        tabla_pendientes = pd.DataFrame(lineas_pendientes)

        st.dataframe(
            tabla_pendientes,
            use_container_width=True,
            hide_index=True,
        )


# ==================================================
# BUSCAR MATERIAL
# ==================================================

st.divider()

st.subheader("🔍 Buscar Material")


material = st.text_input(
    "Material",
    placeholder="Ingrese el Material",
)


# ==================================================
# RESULTADO DE BÚSQUEDA
# ==================================================

if material:
    resultado = buscar_material(
        inventario,
        material,
    )

    if resultado.empty:
        st.error("❌ Material no encontrado.")

    else:
        descripcion = str(resultado.iloc[0]["Texto breve de material"])

        st.success(f"{material} - {descripcion}")

        st.write(f"**Líneas encontradas: {len(resultado)}**")

        # ==================================================
        # MOSTRAR CADA LÍNEA
        # ==================================================

        for indice, fila in resultado.iterrows():
            material_fila = str(fila["Material"])

            texto_material = str(fila["Texto breve de material"])

            parte_numero = str(fila["Parte Número"])

            lote = str(fila["Lote"])

            ubic_wm = str(fila["Ubic WM"])

            fecha = fila["FeCaduc/FePreferCons"]

            stock = int(fila["stock Disponible"])

            unidad_medida = str(fila["Unidad medida  base"])

            # ==============================================
            # FORMATEAR FECHA
            # ==============================================

            if pd.isna(fecha):
                fecha_texto = "-"

            elif hasattr(
                fecha,
                "strftime",
            ):
                fecha_texto = fecha.strftime("%d/%m/%Y")

            else:
                fecha_texto = str(fecha)

            # ==============================================
            # BUSCAR CONTEO EN MEMORIA
            # ==============================================

            anterior = obtener_conteo_memoria(
                material_fila,
                lote,
                ubic_wm,
            )

            # ==============================================
            # TARJETA
            # ==============================================

            # ==============================================
            # TARJETA DEL MATERIAL
            # ==============================================

            with st.container(border=True):
                # ENCABEZADO
                st.markdown(f"### 📦 {material_fila} · {texto_material}")

                st.divider()

                # ==========================================
                # INFORMACIÓN DEL MATERIAL
                # ==========================================

                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"🔖 **Parte Número:** {parte_numero}")

                    st.write(f"🏷️ **Lote:** {lote}")

                    st.write(f"📍 **Ubicación:** {ubic_wm}")

                with col2:
                    st.write(f"📅 **Fecha vencimiento:** {fecha_texto}")

                    st.write(f"📊 **Stock disponible:** {stock}")

                    st.write(f"📏 **Unidad de Medida:** {unidad_medida}")

                st.divider()

                # ==========================================
                # ESTADO
                # ==========================================

                if anterior:
                    st.success("✅ Línea ya contada")

                    valor_inicial = int(anterior["conteo_fisico"])

                    diferencia_anterior = int(anterior["diferencia"])

                    if diferencia_anterior == 0:
                        st.success("🟢 Diferencia guardada: 0 — Stock correcto")

                    elif diferencia_anterior > 0:
                        st.info(
                            f"🔵 Diferencia guardada: +{diferencia_anterior} — Sobrante"
                        )

                    else:
                        st.error(
                            f"🔴 Diferencia guardada: {diferencia_anterior} — Faltante"
                        )

                else:
                    st.warning("🟡 Pendiente de conteo")

                    valor_inicial = 0

                # ==========================================
                # FORMULARIO
                # ==========================================

                with st.form(key=f"form_{indice}_{material_fila}_{lote}_{ubic_wm}"):
                    conteo = st.number_input(
                        "🔢 Conteo físico",
                        min_value=0,
                        value=valor_inicial,
                        step=1,
                        key=f"conteo_{indice}_{material_fila}_{lote}_{ubic_wm}",
                    )

                    observacion = st.text_area(
                        "📝 Observación",
                        value=(anterior["observacion"] if anterior else ""),
                        placeholder=("Escribe una observación (opcional)"),
                        key=f"obs_conteo_{indice}_{material_fila}_{lote}_{ubic_wm}",
                    )

                    # ======================================
                    # DIFERENCIA
                    # ======================================

                    diferencia_nueva = int(conteo) - int(stock)

                    if diferencia_nueva == 0:
                        st.success("🟢 Diferencia: 0 — Stock correcto")

                    elif diferencia_nueva > 0:
                        st.info(f"🔵 Diferencia: +{diferencia_nueva} — Sobrante")

                    else:
                        st.error(f"🔴 Diferencia: {diferencia_nueva} — Faltante")

                    # ======================================
                    # GUARDAR
                    # ======================================

                    guardar = st.form_submit_button(
                        "💾 Guardar conteo",
                        type="primary",
                        use_container_width=True,
                    )

                    if guardar:
                        guardar_conteo(
                            material_fila,
                            lote,
                            texto_material,
                            parte_numero,
                            ubic_wm,
                            fecha_texto,
                            stock,
                            conteo,
                            observacion,
                        )

                        st.success("✅ Conteo guardado correctamente.")

                        st.rerun()


# ==================================================
# CONTEOS REALIZADOS
# ==================================================

st.divider()


with st.expander("📋 Ver conteos realizados"):
    datos = datos_conteos

    if len(datos) == 0:
        st.info("Todavía no hay conteos realizados.")

    else:
        tabla = pd.DataFrame(
            datos,
            columns=[
                "📦 Material",
                "🏷️ Lote",
                "📝 Descripción",
                "🔖 Parte Número",
                "📍 Ubicación",
                "📅 Fecha vencimiento",
                "📊 Stock disponible",
                "🔢 Conteo físico",
                "Diferencia",
                "📝 Observación",
            ],
        )

        # ==============================================
        # FILTRO
        # ==============================================

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


datos = datos_conteos


if len(datos) == 0:
    st.info("Todavía no hay conteos para exportar.")

else:
    archivo_excel = generar_excel(datos)

    st.download_button(
        label="📥 Descargar conteo en Excel",
        data=archivo_excel,
        file_name="Conteo.xlsx",
        mime=("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        use_container_width=True,
    )


# ==================================================
# OPCIONES
# ==================================================

st.divider()


with st.expander("⚙️ Opciones"):
    st.warning("Reiniciar los conteos eliminará todo el trabajo realizado.")

    confirmar = st.checkbox("Confirmo que quiero reiniciar todos los conteos")

    if st.button(
        "🗑️ Reiniciar conteos",
        use_container_width=True,
    ):
        if confirmar:
            limpiar_conteos()

            st.success("✅ Conteos eliminados.")

            st.rerun()

        else:
            st.warning("⚠️ Debes confirmar primero.")
