# importando as biblitecas necessárias
import streamlit as st
import pandas as pd
import datetime as dt
from datetime import datetime
from datetime import date, timedelta
import numpy as np
import plotly.graph_objects as go
import investpy as inv
import numpy as np
import re
import plotly_express as px


################################################################################# Funções auxíliares ###################################################################

def log(f):
    def wrapper(df, *args, **kwargs):
        tic = dt.datetime.now()
        result= f(df, *args, **kwargs)
        toc= dt.datetime.now()
        print(f"{f.__name__} took {toc-tic}")
        return result
    return wrapper

def dates_map():
    meses = {'OUT':'10','DEZ':'12', 'AGO':'8','FEV':'2', 'MAR':'3', 'ABR':'4', 'SET':'9', 'NOV':'11', 'JAN':'1','JUL':'7', 'JUN':'6', 'MAI':'5'}
    return meses 


################################################################################# Funções de endpoints de dados ###################################################################
@st.cache()
def get_sector_data():
    df= pd.read_pickle('https://github.com/NicolasWoloszko/OECD-Weekly-Tracker/blob/main/Data/sectors/sv_weekly_agg_yo2y.pkl?raw=true')
    df= df.reset_index()
    return df


@st.cache
def get_agg_data():
    df= pd.read_csv('https://raw.githubusercontent.com/NicolasWoloszko/OECD-Weekly-Tracker/main/Data/weekly_tracker.csv')
    df= df.reset_index()
    return df

################################################################################# Func for data manipulation ###################################################################

@log
def country_sector_plot(df, country):
    ''' See recent trends for a giving country and its agg subsectors and makes a plot '''
    #subseting df1 weekly
    df = df[df.region==f'{country}'].dropna().set_index('date').copy()
    df = df.drop('region', axis=1)
    df =  df.rolling(4).mean().dropna().reset_index()
    long_df = df.melt(id_vars= 'date',var_name='sector',value_name='yo2y')

    #make fig = 
    colors = ['#031820','#7AADD4','#0A3254','#30587C','#7891B0','#A7B7CF','#BFCBDE','#10022D','#090437','#060C41','#081E4B',]
    fig = px.bar(long_df, x='date', y='yo2y', color="sector", title="Long-Form Input",  color_discrete_sequence=colors)

    fig.update_layout(title={ 'text': '<b>'+ 'Tracking GDP growth in real time for the ' + country.title()+'<b>','y':0.9,'x':0.5,'xanchor': 'center','yanchor': 'top'},
                            paper_bgcolor='rgba(0,0,0,0)', #added the backround collor to the plot 
                            plot_bgcolor='rgba(0,0,0,0)',
                             title_font_size=14,
                             yaxis_title='level compared with pre-covid trend', 
                             xaxis_title='', 
                             template='plotly_white',
                             font_family="Verdana",
                             images=[dict(source='https://raw.githubusercontent.com/caiquecober/Research/master/LOGO_COD_T-PhotoRoom%20(1).png',
                                 xref="paper", yref="paper",
                                 x=0.5, y=0.5,
                                 sizex=0.85, sizey=0.85,
                                 opacity=0.2,
                                 xanchor="center",
                                 yanchor="middle",
                                 sizing="contain",
                                 visible=True,
                                 layer="below")],
                             legend=dict(
                                 orientation="h",
                                 yanchor="bottom",
                                 y=-0.5,
                                 xanchor="center",
                                 x=0.5,
                                 font_family='Verdana'),
                                 autosize=True,height= 550,
                                 )
    return fig

@log
def weekly_plot(df, df2,country):


    #plotly plot section
    p1_fig = go.Figure()
    colors = ['#E0D253', '#0A3254', '#B2292E','#7AADD4','#336094']
    indice = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
    config = dict({'scrollZoom': True,'displayModeBar': False})
    
    p1_fig.add_trace(go.Scatter(x=df.index, y=df['High (counterfactual)'],
                                   name='High (counterfactual)',
                                   fill=None,
                                   mode=None,
                                   line_color='lightgray', showlegend=False
                                   ))

    p1_fig.add_trace(go.Scatter(x=df.index, y=df['Low (counterfactual)'], name='Min',
                                   fill='tonexty',  # fill area between trace0 and trace1
                                   mode=None, line_color='lightgray', showlegend=False))

    p1_fig.add_trace(go.Scatter(x=df.index, y=df['Pre covid Trend'], name='Pre covid Trend',
                                   line=dict(color='black', width=4, dash='dot')))
    p1_fig.add_trace(go.Scatter(
                x=df.index, y=df['Tracker (counterfactual)'], line=dict(color=colors[1], width=4), name='Tracker (counterfactual)'))
    
   
    p1_fig.update_layout(title={ 'text': '<b>'+ 'Tracking GDP growth in real time for ' + country.title()+'<b>','y':0.9,'x':0.5,'xanchor': 'center','yanchor': 'top'},
                            paper_bgcolor='rgba(0,0,0,0)', #added the backround collor to the plot 
                            plot_bgcolor='rgba(0,0,0,0)',
                             title_font_size=14,
                             yaxis_title='level compared with pre-covid trend', 
                             template='plotly_white',
                             font_family="Verdana",
                             images=[dict(source='https://raw.githubusercontent.com/caiquecober/Research/master/LOGO_COD_T-PhotoRoom%20(1).png',
                                 xref="paper", yref="paper",
                                 x=0.5, y=0.5,
                                 sizex=0.85, sizey=0.85,
                                 opacity=0.2,
                                 xanchor="center",
                                 yanchor="middle",
                                 sizing="contain",
                                 visible=True,
                                 layer="below")],
                             legend=dict(
                                 orientation="h",
                                 yanchor="bottom",
                                 y=-0.4,
                                 xanchor="center",
                                 x=0.5,
                                 font_family='Verdana'),
                                 autosize=False, height= 550, width=750
                                 )
    return p1_fig


@log
def country_plot(df,df2, country):
    ''' See recent trends for a giving country and make a plot '''
    #subseting df1 weekly
    df = df[df.region==f'{country}'].dropna().set_index('date')
    df = df[['Tracker (counterfactual)', 'Low (counterfactual)','High (counterfactual)']]
    df['Pre covid Trend'] = 0
    #subseting df2 monthly
    fig = weekly_plot(df,df2, country)
    return fig, df

############################################# Streamlit  HTML     ##################################################################################################
html_header="""
<head>
<style> @import url('https://fonts.googleapis.com/css2?family=Mulish:wght@400;500;600;700;800&display=swap'); 
@import url('https://fonts.googleapis.com/css2?family=Crimson+Text:wght@400;600;700&display=swap'); </style>
<title>C0D_ATA </title>
<meta charset="utf-8">
<meta name="keywords" content="Economics, data science, OCDE, GDP, streamlit, visualizer, data">
<meta name="description" content="C0D_ATA Data Project">
<meta name="author" content="@Cober">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<h1 style="font-size:300%; color:#0A3254; font-family:Mulish; font-weight:800"> OECD Weekly Gdp Visualizer   
<br>
 <hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1px;"></h1>
"""

html_line_2="""
<br>
<hr style= "  display: block;
  margin-top: 0.3em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1px;">
"""

link_png = 'https://raw.githubusercontent.com/caiquecober/Research/master/logo_sem_nome.-PhotoRoom.png'

st.set_page_config(page_title="C0D_DATA - OCDE Weekly data visualizer", page_icon=link_png, layout="wide")

padding = 1.2
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)

st.markdown('<style>body{background-color: #D2D5D4}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style> 
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)


############################## ST APP ###################### ################################################################################################

paginas = st.sidebar.selectbox('',['Selected countries','select country'])

############################### Page 1 #######################################################################################################################
df_sec = get_sector_data()
df_agg = get_agg_data()

if paginas == 'Selected countries':

    #pegando os dados específicos com o df1 além do df inicial que é usado como base para todas as perspectivas
    fig0, _ = country_plot(df_agg,df_sec,'Brazil')
    fig1, _ = country_plot(df_agg,df_sec,'United States')
    
    fig2 = country_sector_plot(df_sec,'Brazil')
    fig3 = country_sector_plot(df_sec,'United States')

    config = {"displayModeBar": False, "showTips": False}
    ################## ST LAYOUT ###################################################################################################
    #     
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig0, use_container_width=True)
    col2.plotly_chart(fig1, use_container_width= True)

    col1, col2 = st.columns(2)
    col1.plotly_chart(fig2, use_container_width=True)
    col2.plotly_chart(fig3, use_container_width= True)



if paginas == 'select country':
    with st.sidebar.expander("Choose country"): 
        lst_countries = df_agg.region.unique()
        selected_country= st.selectbox('',lst_countries)

        
    #plotting data of the selected country
    fig3, _ = country_plot(df_agg, df_agg, selected_country)
    fig4 = country_sector_plot(df_sec,selected_country)


    ################## ST LAYOUT  do paginina 2####################################################################################################
    config = {"displayModeBar": False, "showTips": False}
    st.plotly_chart(fig3, use_container_width=True,config=config)
    st.plotly_chart(fig4, use_container_width=True,config=config)
    
    # col1,col2 = st.columns(2)
    # col1.write(f'Analising real time data we se that overal in {selected_country} has observed a jump in the estimated gdp in the last month,since overal gdp is 5% higher then 4 week ago')
    # col2.write(f'Analising real time data we se that overal in {selected_country} has observed a jump in the estimated gdp in the last month,since overal gdp is 5% higher then 4 week ago')

################## ST LAYOUT do parte inferior ####################################################################################################
html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)

html_line="""
<br>
<br>
<br>
<br>
<p style="color:Gainsboro; text-align: left;">Source: OECD, Nicolas Woloszko.</p>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;">
<p style="color:Gainsboro; text-align: right;">Application developed by: C0D_ATA</p>
"""
st.markdown(html_line, unsafe_allow_html=True)