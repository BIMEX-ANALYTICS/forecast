import streamlit as st
import pandas as pd
from functions import *
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Configuración básica de la aplicación
st.set_page_config(page_title="Forecast de Proyectos IT", layout="wide")

## Pestañas de la aplicación
st.title("FORECAST BIMEX ANALYTICS")
tabs = st.tabs(["Introducción de Datos", "Resumen de Forecast", "Análisis Gráfico", "Datos Maestros","Proyección Financiera"])

# Pestaña 1: Introducción de Datos
with tabs[0]:
    st.header("Introducir Datos de Forecast")
    with st.form("data_input_form"):
        proyecto = st.text_input("Nombre del Proyecto")
        probabilidad = st.slider("Probabilidad de Éxito (%)", 0, 100, 50) / 100
        tarifa = st.number_input("Tarifa por Jornada (€)", min_value=0, step=100)
        jornadas = st.number_input("Número de Jornadas", min_value=0, step=1)
        estado = st.selectbox("Estado del Proyecto", ["Abierto", "Cerrado"])
        tecnologia = st.multiselect("Tecnología", ["SAP", "Microsoft", "Otros"])
        clientes = leer_clientes()
        cliente = st.selectbox("Cliente", clientes)
        comentarios = st.text_area("Comentarios")
        fecha_ini = st.date_input("Fecha Inicio")
        fecha_fin = st.date_input("Fecha Fin")
        
        # Botón para añadir los datos
        submitted = st.form_submit_button("Añadir al Forecast")
        
        if submitted:
            # Cálculo de forecast y actualización de datos
            forecast = calcular_forecast(probabilidad, tarifa, jornadas)
            tecnologias_str = ", ".join(tecnologia)  # Convertir a cadena de texto
            insertar_proyecto(proyecto, probabilidad, tarifa, jornadas, forecast, estado, tecnologias_str, cliente, comentarios,fecha_ini,fecha_fin)
            st.success(f"Proyecto '{proyecto}' añadido exitosamente al forecast.")

# Pestaña 2: Resumen de Forecast
with tabs[1]:
    st.header("Resumen de Forecast")
    
    # Cargar los proyectos desde la base de datos
    df_proyectos = leer_proyectos()
     # Convertir "Estado" a booleano: True para "Abierto", False para "Cerrado"
    df_proyectos["Estado"] = df_proyectos["Estado"].apply(lambda x: True if x == "Abierto" else False)
    
     # Agregar columna de botones "Eliminar"
    df_proyectos['Eliminar'] = False


    # Mostrar la tabla editable con st.data_editor
    edited_df = st.data_editor(df_proyectos.drop(columns=["ID"]), use_container_width=True, key='data_editor')

    # Manejo de eliminación de filas
     # Botón para eliminar los seleccionados
    if st.button("Eliminar filas"):
        # Identificar los IDs de los proyectos seleccionados para eliminar
        proyectos_seleccionados = df_proyectos[df_proyectos['Eliminar']].ID.tolist()
        
        if proyectos_seleccionados:
            eliminar_proyectos(proyectos_seleccionados)
            st.success(f"Proyectos eliminados exitosamente.")
            st.experimental_rerun()  # Recargar la página para actualizar la tabla sin los proyectos eliminados
        else:
            st.warning("Por favor, selecciona al menos un proyecto para eliminar.")


    # Confirmar cambios
    if st.button("Confirmar Cambios"):
        # Recoger los cambios realizados en la tabla
        edited_rows = st.session_state.get('data_editor', {}).get('edited_rows', {})

        for row_idx, edited_data in edited_rows.items():
            # print(row_idx)
            # Actualizar solo las filas que fueron editadas
            for columna, valor_nuevo in edited_data.items():
                valor_original = df_proyectos.at[row_idx, columna]
                print("COLUMNA",columna.lower(),"new",valor_nuevo,"OLD" ,valor_original)
                if valor_original != valor_nuevo:
                    print(df_proyectos.at[row_idx, "ID"])
                    proyecto_id = int(df_proyectos.at[row_idx, "ID"])
                    print("Actualizando proyecto con ID:", proyecto_id)
                    actualizar_proyecto(proyecto_id, columna.lower(), valor_nuevo)
                    # actualizar_proyecto(1, columna.lower(), valor_nuevo)
        
        st.success("Cambios guardados exitosamente.")
    if st.button("Publicar"):
        st.success("Cambios publicados en Snowflake exitosamente.")

# Pestaña 3: Análisis Gráfico y Escenarios
with tabs[2]:
    st.header("Análisis de Escenarios")
    if not df_proyectos.empty:
        # Selección de escenario
        ajuste_probabilidad = st.slider("Ajuste de Escenario (% Probabilidad)", -50, 50, 0)
        
        # Aplicar ajuste y mostrar datos ajustados
        df_ajustado = aplicar_escenario(df_proyectos, ajuste_probabilidad)
        st.write(f"Forecast ajustado con un {ajuste_probabilidad}% de cambio en la probabilidad:")
        st.dataframe(df_ajustado[["Nombre", "Probabilidad Ajustada", "Forecast Ajustado (€)", "Estado", "Tecnología", "Cliente"]], use_container_width=True)
        # Gráfico de barras por proyecto ajustado
        st.bar_chart(df_ajustado.set_index("Nombre")["Forecast Ajustado (€)"])
    else:
        st.info("Introduce datos en la pestaña de 'Introducción de Datos' para ver el análisis gráfico.")

# Pestaña 4: Datos Maestros
with tabs[3]:
    st.header("Gestión de Datos Maestros")
    
    # Sección de creación de Clientes en un formulario separado
    with st.form("crear_cliente"):
        st.subheader("Crear Nuevo Cliente")
        nuevo_cliente = st.text_input("Nombre del Cliente")
        submit_cliente = st.form_submit_button("Añadir Cliente")
        
        if submit_cliente:
            if insertar_cliente(nuevo_cliente):
                st.success(f"Cliente '{nuevo_cliente}' añadido exitosamente.")
            else:
                st.error(f"El cliente '{nuevo_cliente}' ya existe en la base de datos.")
    
    # Mostrar lista de clientes
    st.write("Lista de Clientes Existentes:")
    st.write(pd.DataFrame(leer_clientes(), columns=["Cliente"]))
    
    # Sección de creación de Proyectos en un formulario separado
    with st.form("crear_proyecto"):
        st.subheader("Crear Nuevo Proyecto")
        nuevo_proyecto = st.text_input("Nombre del Proyecto (Datos Maestros)")
        submit_proyecto = st.form_submit_button("Añadir Proyecto Maestro")
        
        if submit_proyecto:
            insertar_proyecto(nuevo_proyecto, 0, 0, 0, 0, "Abierto", "", "", "")
            st.success(f"Proyecto '{nuevo_proyecto}' añadido a los datos maestros.")
    
    # Mostrar lista de proyectos maestros
    st.write("Lista de Proyectos Existentes:")
    st.write(leer_proyectos()[["Nombre"]])
# Pestaña 5: Proyección Financiera
with tabs[4]:
    st.header("Proyección Financiera: Totales y KPIs")

    # Dividimos la sección de entrada en dos columnas
    col1, col2 = st.columns(2)

    # Sección de entrada manual para Actual y Forecast de Gastos
    with col1:
        st.subheader("Gastos")
        actual_gastos = st.number_input("Total de Gastos Realizados (€)", min_value=0.0, step=100.0)
        forecast_gastos = st.number_input("Total de Gastos Previstos (€)", min_value=0.0, step=100.0)

    # Sección de entrada manual para Actual y Forecast de Ventas
    with col2:
        st.subheader("Ventas")
        actual_ventas = st.number_input("Total de Ventas Realizadas (€)", min_value=0.0, step=100.0)
        
        # Calcular forecast de ventas automáticamente a partir de los proyectos abiertos
        df_proyectos = leer_proyectos()
        forecast_ventas = df_proyectos[df_proyectos["Estado"] == "Abierto"]["Forecast"].sum()
        st.metric("Total Forecast Ventas (€)", f"{forecast_ventas:,.2f} €")

    # KPIs: Cálculos adicionales
    total_ventas = actual_ventas + forecast_ventas
    total_gastos = actual_gastos + forecast_gastos
    ventas_menos_gastos = total_ventas - total_gastos
    porcentaje_gastos_sobre_ventas = (total_gastos / total_ventas) * 100 if total_ventas != 0 else 0
    porcentaje_beneficio_sobre_ventas = ((total_ventas - total_gastos) / total_ventas) * 100 if total_ventas != 0 else 0

    # KPI Style Settings
    # kpi_style = {"font-size": "24px", "font-weight": "bold"}
    # kpi_color_positive = "green"
    # kpi_color_negative = "red"

    # KPI Colores para porcentajes
    # color_gastos = kpi_color_positive if porcentaje_gastos_sobre_ventas < 50 else kpi_color_negative
    # color_beneficio = kpi_color_positive if porcentaje_beneficio_sobre_ventas > 0 else kpi_color_negative

    # Mostrar KPIs
    st.subheader("KPIs")
    kpi_col1, kpi_col2, kpi_col3,kpi_col4= st.columns(4)

    with kpi_col1:
        # st.markdown(f"<div style='text-align:center; {kpi_style}'>Ventas - Gastos (€)<br><span>{ventas_menos_gastos:,.2f} €</span></div>", unsafe_allow_html=True)
        st.metric("Margen",ventas_menos_gastos,delta_color="normal")
    with kpi_col2:
        # st.markdown(f"<div style='text-align:center; color:{color_gastos}; {kpi_style}'>% Gastos sobre Ventas<br><span>{porcentaje_gastos_sobre_ventas:.2f} %</span></div>", unsafe_allow_html=True)
        st.metric("Tot ventas",total_ventas)
    with kpi_col3:
        st.metric("Tot gastos",total_gastos)
    with kpi_col4:
        st.metric("% EBITDA",porcentaje_beneficio_sobre_ventas,delta_color="normal")
    # Crear gráfico comparativo entre Actual y Forecast para Gastos y Ventas con Plotly
    fig = make_subplots(rows=1, cols=1)

    # Datos de Actual y Forecast
    categories = ['Gastos', 'Ventas']
    actual_values = [actual_gastos, actual_ventas]
    forecast_values = [forecast_gastos, forecast_ventas]

    # Gráfico de barras apiladas con Plotly
    fig.add_trace(go.Bar(name="Actual", x=categories, y=actual_values, marker_color="blue"))
    fig.add_trace(go.Bar(name="Forecast", x=categories, y=forecast_values, marker_color="orange"))

    # Configuración del diseño del gráfico
    fig.update_layout(
        barmode='stack',
        title="Comparación Total: Actual vs Forecast (Gastos y Ventas)",
        xaxis_title="Categoría",
        yaxis_title="€",
        title_font_size=20,
        title_x=0.5,
        showlegend=True
    )

    # Mostrar el gráfico
    st.plotly_chart(fig)