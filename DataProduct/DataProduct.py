import os, folium, streamlit as st, pandas as pd, plotly.express as px, plotly.graph_objects as go
from datetime import datetime as dt
from streamlit_folium import folium_static

# Cargamos el contenido del json en un Data Frame obteniendo la ruta q contiene el archivo y luego combinando
# Con con el nombre del json
db=pd.read_json(os.path.join(os.path.dirname(__file__), '..', 'base de datos.json'))
db=db.transpose() # Transponer el dataframe
db = db.drop('Info', axis=1)

with st.container():
    st.title("El déficit de electricidad en Cuba")
    st.write("""
         En los últimos annos el país ha experimentado importantes afectaciones relacionadas con el Sistema Electroenergético Nacional, que unido a varias factores
         la disponibilidad del petróleo y otros han generado gran descontento en la población. Es por eso que mediante el siguiente estudio se pretende que la población
         adquiera un mayor conocimiento sobre el tema y de esta forma generar una mayor conciencia de por qué resulta importante el ahorro de electricidad.
         """)

with st.expander("Comportamiento de los parámetros"):
    #Titulo de la visualizacion
    st.title("Comportamiento de los diferentes parámetros a lo largo del tiempo")
    categories = ["MW disponibles","Demanda del dia","MW indisponibles por averias","MW en mantenimiento","MW limitados en la generacion termica"]
    
    if 'start_date' not in st.session_state:
        st.session_state.start_date = dt(db.index.min().year, db.index.min().month, db.index.min().day)
    if 'end_date' not in st.session_state:
        st.session_state.end_date = dt(db.index.max().year, db.index.max().month, db.index.max().day)
    
    fig = go.Figure()

    # Agregar un selector de fechas para elegir el rango de fechas a mostrar
    start_date = st.date_input(label='Fecha de inicio', value=db.index.min(), min_value=db.index.min(), max_value=st.session_state.end_date)
    st.session_state.start_date = dt(start_date.year, start_date.month, start_date.day)
    end_date = st.date_input(label='Fecha de fin', value=db.index.max(), min_value=st.session_state.start_date, max_value=db.index.max())
    st.session_state.end_date = dt(end_date.year, end_date.month, end_date.day)

    # Filtrar la bd con respecto a las fechas seleccionadas
    filter_df = db[(db.index >= st.session_state.start_date) & (db.index <= st.session_state.end_date)]
    filter_df = filter_df.drop(['Termoelectricas fuera de servicio', 'Termoelectricas en mantenimiento'], axis = 1)

    # Crear el gráfico
    for line in filter_df:
        fig.add_scatter(x=filter_df.index , y=filter_df[line], mode="lines", name=line)
    fig.update_layout(title='Comportamiento de los parámetros', xaxis_title='Tiempo', yaxis_title='Cantidad')
    st.plotly_chart(fig)

mariandb = db
mariandb.index.name = 'Fecha'
mariandb = mariandb.reset_index()
if mariandb['Fecha'].dtype != 'datetime64[ns]':
    mariandb['Fecha'] = pd.to_datetime(mariandb['Fecha'])
        
mariandb['Mes'] = mariandb['Fecha'].dt.month
mariandb['Mes']=mariandb['Mes'].astype (str)
mariandb['Año'] = mariandb['Fecha'].dt.year

with st.expander("Máxima afectación durante el horario pico"):
    st.write("---")
    st.title("Máxima afectación durante el horario pico:")
    st.write(f"""A la largo de los annos las cifras de las máximas afectaciones durante el horario pico han sido bastante elevadas, principalmente en el anno 2022, donde alcanzaron los valores más elevados.
             La maxima afectación del anno 2022 se reportó en el mes de octubre, cuyas afectaciones promedio en el mes fueron de  1138 MW aproximadamente. 
             Sin embargo en 2023, la maxima afectacion por mes fue de 473.5 MW en el mes de abril, esto nos demuestra la existencia de factores que, unido a las diferentes
             medidas tomadas por la empresa el'ectrica de conjunto con otros organismos, han posibilitado la disminución de la afectación.
             De igual forma, el comportamiento de la variable no es igual entre ambos annos. Las máximas afectaciones de 2022 corresponden a los meses desde agosto hasta noviembre,
             mientras que en 2023 las máximas afectaciones se corresponden a abril, septiembre, octubre y noviembre.
             El mes de menor afectación en el anno 2022 es marzo, mientras que el mes de menor afectación en el 2023 es julio.
             
             """)
 
    #Calcular la media por mes de la máxima afectación en el horario pico para cada año
    media_por_mes = mariandb.groupby(['Año', 'Mes'])['Maxima afectacion'].mean().reset_index()
    fig = px.bar(media_por_mes, x='Mes', y='Maxima afectacion', barmode="group",color='Año' ,color_discrete_sequence=px.colors.qualitative.Plotly)

    # Mostrar el gráfico en Streamlit
    st.write("Media de máxima afectación en el horario pico por mes")
    st.plotly_chart(fig)
    
    #hacer un grafico de cajas:
    # Crear un selectbox para seleccionar el año
    ano = st.selectbox("Selecciona un año", mariandb['Año'].unique())
    # Filtrar el dataframe basado en la selección del usuario
    mariandb_filtrado = mariandb[mariandb['Año'] == ano]
    # Crear el boxplot
    boxplot = px.box(mariandb_filtrado, x="Mes", y="Maxima afectacion",
                    title='Distribución de Máxima Afectación durante Horario Pico de Megawatts por Mes',
                    labels={'Max_Afectacion_Horario_Pico_MW': 'Máxima Afectación (MW)', 'x': 'Mes'},
                    color_discrete_sequence=['#2B83BA'])
    st.plotly_chart(boxplot)
    
with st.expander("Demanda vs Disponibilidad"):
    st.write("---")
    st.title("Disponibilidad vs Demanda")
    st.write("""
             La disponibilidad y la demanda del sistema electroenergetico nacional varia con el transcurso del día, por lo que, para el análisis de esta variable hemos
             analizado la disponibilidad y la demanda a las 6:00-7:00 am.
             Resulta imposible hablar de disponibilidad sin hablar de demanda y viceversa, lo cual se comprueba en el siguiente grafico que muestra la fuerte correlaci'on exitente entre las dos variables:
             """)
    #grafico de dispersion
    fig = px.scatter(mariandb_filtrado, x='Demanda del dia', y='MW disponibles', text='Mes', title='Demanda vs. Disponibilidad')
    # Personalizar el diseño del gráfico
    fig.update_traces(marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')),
                    selector=dict(mode='markers+text'))
    # Visualizar el gráfico en Streamlit
    st.plotly_chart(fig)
    
    st.write("""
             De la misma forma, en dependencia de la disponibilidad y la demanda del día es posible conocer el déficit diario de electricidad, y de esta forma conocer los meses de mayor déficit.
             De esta forma los meses de mayor deficit de electricidad de 2022 corresponden con junio, septiembre y noviembre.
             En 2023 el mayor deficit estuvo dado en los meses de septiembre, octubre, noviembre y junio. 
             Por lo que coinciden los meses de junio, septiembre y noviembre como meses con mayor deficit de electricidad en el anno.
             """
    )
    
    deficit=mariandb["Demanda del dia"]-mariandb["MW disponibles"]
    deficit[deficit<0]=0
    mariandb["Deficit"]=deficit
    year=st.selectbox("Seleccione el anno",mariandb['Año'].unique())
    media_deficit = mariandb.groupby(['Año', 'Mes'])['Deficit'].mean().reset_index()
    mariandb_filtrado2 = mariandb[mariandb['Año'] == year]
    fig=px.bar(mariandb_filtrado2, x='Mes', y='Deficit', title=f'Déficit por mes en {ano}')
    st.plotly_chart(fig)
    
with st.expander("MW limitados en la generación térmica"):
    st.write("---")
    st.title("MW limitados y generación térmica:")
    st.write("""
             
             """)
    
with st.expander('Termoeléctricas fuera de servicio y en mantenimiento'):
    st.title('Análisis de las termoeléctricas fuera de servicio y en mantenimiento')
    st.markdown('En el país existen ocho centrales termoeléctricas con un total de 20 bloques en explotación, que constituyen la parte más importante de la generación base del sistema eléctrico.')
    st.markdown('Fundada por el líder histórico de la Revolución, Fidel Castro, la termoeléctrica Guiteras destaca por encontrarse en la zona occidental de la Isla, donde se concentran las mayores cargas, y por consumir crudo nacional por oleoducto, sin necesidad de gastos por concepto de transportación, entre otras ventajas. Esta es la de mayor generación en el país.')
    

    #Realizar los analisis
    #un mapa con las localizaciones
    st.subheader('Localización de las termoeléctricas')

    #cargar el archivo de las localizaciones de las termoelectricas
    df=pd.DataFrame(
        {
            
            "Latitude":[20.728433644751583,23.160837163922988,21.567053113289774,
                        23.019279319106403,23.1302452430394,23.10243454755323,
                        22.159797344832885,23.125633165882828,],
            'Longitude':[-75.5967566913524,-81.96305989167605,-77.2713085457038,
                         -82.74817643083628,-82.33771615913784,-81.52929387263102,
                         -80.45564991842924,-82.35890043084758],
            'Names':['CTE Lidio Ramón Pérez(Felton)','CTE Ernesto Guevara(Santa Cruz)','CTE Diez de Octubre(Nuevitas)','CTE Máximo Gómez(Mariel)',
                               'CTE Antonio Maceo(Renté)','CTE Antonio Guiteras','CTE Carlos M de Cespedes(Cienfuegos)',
                               "CTE Otto Parellada(Tallapiedra)"]
        }
    )
    
    mapa=folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=6)
    for i in range(len(df)):
        folium.Marker([df.iloc[i]['Latitude'], df.iloc[i]['Longitude']], popup=df.iloc[i]['Names']).add_to(mapa)    
    folium_static(mapa)

    
    #un grafico de lineas de dos variables para mostrar las cantidades a lo largo del tiempo
    st.subheader('Cantidad de termoeléctricas dependiendo de su estado a lo largo del tiempo')

    if 'fecha_minima' not in st.session_state:
        st.session_state.fecha_minima = dt(db.index.min().year, db.index.min().month, db.index.min().day)
    if 'fecha_maxima' not in st.session_state:
        st.session_state.fecha_maxima = dt(db.index.max().year, db.index.max().month, db.index.max().day)
    
    # Crear un selector de fechas en Streamlit para la fecha de inicio del rango
    fecha_inicio = st.date_input("Selecciona la fecha a partir de cuándo quiere ver el análisis", min_value=db.index.min(), max_value=st.session_state.fecha_maxima, value=st.session_state.fecha_minima)

    # Crear un selector de fechas en Streamlit para la fecha de fin del rango
    fecha_fin = st.date_input("Selecciona la fecha de finalización", min_value=st.session_state.fecha_minima, max_value=db.index.max(), value=st.session_state.fecha_maxima)

    # Convertir las fechas seleccionadas a formato datetime
    st.session_state.fecha_minima = dt(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day)
    st.session_state.fecha_fin = dt(fecha_fin.year, fecha_fin.month, fecha_fin.day)

    # Filtrar el dataframe por el rango de fechas seleccionado
    filter = db[(db.index >= st.session_state.fecha_minima) & (db.index <= st.session_state.fecha_fin)]
    
    cant_fs= []#cantidad de unidades fuera de servicio
    cant_m=[]#cantidad de unidades en mantenimiento
    for i in filter['Termoelectricas en mantenimiento']:
        c=0
        if i!=None:
            for j in i:
                c+=1
        cant_m.append(c)
    for i in filter['Termoelectricas fuera de servicio']:
        c=0
        if i!=None:
            for j in i:
                c+=1
        cant_fs.append(c)
    
    fig_t=go.Figure()
    fig_t.add_scatter(x=filter.index , y=cant_fs, mode="lines", name="Fuera de servicio")
    fig_t.add_scatter(x=filter.index , y=cant_m, mode="lines", name="En Mantenimiento")
    fig_t.update_layout(
    title='Cantidad de termoeléctricas por su estado',
    xaxis_title='Fecha',
    yaxis_title='Cantidad de termoeléctricas'
    )
    st.plotly_chart(fig_t)

    # #un grafico de barras apiladas por termoelectricas
  
    st.markdown('La vida útil de una termoeléctrica está entre 30 y 35 años. En nuestro caso, excepto los dos bloques de Felton, que llevan 25 y 21 años sincronizados, los demás tienen más de 30 años de explotación y siete de ellos acumulan más de 40 años operando')
    st.markdown('Mediante el gráfico anterior se puede apreciar las comparaciones de los dos estados respectos a sus cantidades, por lo que si hay un número significativamente mayor de termoeléctricas fuera de servicio a las que están en mantenimiento, esto podría indicar problemas graves en la capacidad de generación de energía del país. Por otro lado, si hay una proporción mayor de termoeléctricas en mantenimiento en comparación con las que están fuera de servicio, podría sugerir que el país está tomando medidas proactivas para mantener y mejorar su infraestructura energética.')
    
    st.subheader('Frecuencias de las termoeléctricas por estado')
    # Crear un selectbox para seleccionar el año
    year = st.selectbox("Seleccione un año", mariandb['Año'].unique())
    # Filtrar el dataframe basado en la selección del usuario
    filtrado = mariandb[mariandb['Año'] == year]
    
    thermoelectric=[]
    for i in filtrado['Termoelectricas en mantenimiento']:
        if i:
            for j in i:
                if j not in thermoelectric:
                    thermoelectric.append(j)
    for i in filtrado['Termoelectricas fuera de servicio']:
        if i:
            for j in i:
                if j not in thermoelectric:
                    thermoelectric.append(j)
    
    f_s=[]#almacena la cantidad de veces q se repiten las unidades q estan fuera de servicio 
    for j in thermoelectric:
        c=0   
        for i in filtrado['Termoelectricas fuera de servicio']:
            if i :
                if j in i:
                   c+=1
        f_s.append(c)

    m=[]#se almacenan la cantidad de veces q se repiuten cuando estan en mantenimineto
    for i in thermoelectric:
        c=0
        for j in filtrado['Termoelectricas en mantenimiento']:
            if j :
                if i in j:
                    c+=1
        m.append(c)
                    
   
    fig_b = go.Figure()

    fig_b.add_trace(go.Bar(x=thermoelectric, y=f_s, name='Fuera de servicio', marker_color='blue'))
    fig_b.add_trace(go.Bar(x=thermoelectric, y=m, name='En mantenimiento', marker_color='red'))
    fig_b.update_layout(
    title='Frecuencias de las termoeléctricas por estado',
    xaxis_title='Nombres de las termoeléctricas',
    yaxis_title='Frecuencia'
    )
    fig_b.update_layout(barmode='group')

    st.plotly_chart(fig_b)
    st.markdown('Se puede obtener una visión detallada de la distribución geográfica de las instalaciones afectadas. Este gráfico podría proporcionar información sobre las regiones específicas del país que podrían haber experimentado interrupciones en el suministro de energía debido a la falta de funcionamiento de las termoeléctricas. También podría revelar áreas donde se están realizando esfuerzos significativos para el mantenimiento y la mejora de la infraestructura energética.')
    st.markdown('Al analizar los nombres de las termoeléctricas afectadas, se podría identificar si ciertas plantas tienen un historial recurrente de problemas, esto podría ser útil para comprender mejor los desafíos específicos que enfrenta cada planta y para tomar decisiones informadas sobre la asignación de recursos para el mantenimiento y la reparación.')

with st.expander('MW indisponible por averías y por mantenimiento'):
    if 'start_day' not in st.session_state:
        st.session_state.start_day = dt(db.index.min().year, db.index.min().month, db.index.min().day)
    if 'end_day' not in st.session_state:
        st.session_state.end_day = dt(db.index.max().year, db.index.max().month, db.index.max().day)
    
    start_day = st.date_input(label='Fecha inicial', value=st.session_state.start_day, min_value=db.index.min(), max_value=st.session_state.end_day)
    st.session_state.start_day = dt(start_day.year, start_day.month, start_day.day)
    end_day = st.date_input(label='Fecha final', value=st.session_state.end_day, min_value=st.session_state.start_day, max_value=db.index.max())
    st.session_state.end_day = dt(end_day.year, end_day.month, end_day.day)

    # Filtrar la bd con respecto a las fechas seleccionadas
    filter_df2 = db[(db.index >= st.session_state.start_day) & (db.index <= st.session_state.end_date)]
    filter_df2 = filter_df2[['MW indisponibles por averias', 'MW en mantenimiento']]

    column = [i for i in filter_df2]
    st.write(f'A continuación observamos el gráfico de {column[0]} y {column[1]} desde el {start_day.day}/{start_day.month}/{start_day.year} hata el {st.session_state.end_day.day}/{st.session_state.end_day.month}/{st.session_state.end_day.year}, fecha que se puede modificar como usted desee.')

    fig1 = go.Figure()
    for i in filter_df2:
        fig1.add_scatter(x=filter_df2.index, y=filter_df2[i], mode='lines', name=i)
    
    st.write(f'Empezando con el análisis de sus datos elegidos, les mostraré las medidas de tendencia central correspondientes, como por ejemplo, {round(filter_df2[column[0]].mean(), 2)} es, aproximadamente, el promedio de {column[0]} que hubo en el período de tiempo seleccionado y {round(filter_df2[column[1]].mean(), 2)} es el aproximado correspondiente a {column[1]}. Además de esto, también tenemos una mediana de {filter_df2[column[0]].median()} en los {column[0]} y de {filter_df2[column[1]].median()} en {column[1]}.')
    if len(filter_df2[column[0]].mode()) == 1 and len(filter_df[column[1]].mode()) == 1:
        st.write(f'En el caso de la moda, no necesariamente es un solo valor pero, en el rango que usted eligió en este caso, si es un solo valor en ambas columnas y estos son {filter_df[column[0]].mode()[0]} y de {filter_df[column[1]].mode()[0]} respectivamente')
    elif len(filter_df2[column[0]].mode()) == 1 and len(filter_df[column[1]].mode()) > 1 or len(filter_df2[column[0]].mode()) > 1 and len(filter_df[column[1]].mode()) == 1:
        if len(filter_df2[column[0]].mode()) > 1:
            mw = column[0]
            liste = [str(i) for i in filter_df[column[0]].mode()]
        else:
            mw = column[1]
            liste = [str(i) for i in filter_df[column[1]].mode()]
        st.write(f'En el caso de la moda, no necesariamente es un solo valor, de echo, en el rango que usted eligió en este caso, si es un solo valor en ambas columnas y estos son {filter_df[column[0]].mode()[0]} y de {filter_df[column[1]].mode()[0]} respectivamente')
    else:
        liste = [str(i) for i in filter_df[column[0]].mode()]
        st.write(f'En el caso de la moda, no necesariamente es un solo valor, de echo, en el rango q usted eligió son {len(filter_df[column].mode())} valores y estos son {", ".join(liste)}')
    st.write(f'Ahora toca mostrar el valor máximo, que en este conjunto de datos es de {filter_df[column].max()} y el valor mínimo que es de {filter_df[column].min()}')
    st.write(f'Gracias a la desviación estándar podemos observar cuanto se aleja de su media, en este caso su valor es de aproximadamente {round(filter_df[column].std(), 2)}, a continuación muestro un gráfico comparando la desviación estándar y el gráfico de arriba:')
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=filter_df2.index, y=filter_df2[column], mode='lines', name=column))
    fig2.add_trace(go.Scatter(x=[filter_df2.index[-1], filter_df2.index[0]], y=[filter_df2[column].std(), filter_df2[column].std()], mode='lines', name='Desviación Estándar'))
    fig.update_layout(title=column, xaxis_title='Fecha', yaxis_title='MW')
    st.plotly_chart(fig2)
    st.write(f'')
    st.write(f'')

