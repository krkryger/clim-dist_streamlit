import pandas as pd
import numpy as np
import streamlit as st
import folium
from streamlit_folium import folium_static
import seaborn as sns
from matplotlib import pyplot as plt
import json

st.title(
    'Rigasche Zeitung 1802-1888'
)

st.write("""#""")
st.subheader('Data')

st.write("""
The data comes from the collections of the National Library of Latvia and consists of all the numbers of a single periodical - the Rigasche Zeitung - that was published from 1802 to 1888.
Each issue is divided into articles which in turn make up the entries of the dataframe. In total, the dataset has 289 705 articles for a period of 86 years.
""")

st.image('data_histogram.png')

st.write("""#""")
st.subheader('Article headings')

st.write("""
This interactive graph allows you to explore the 50 most common article titles through the whole observation period. The popularity of these headings is presented in a _relative_ manner. This means that the popularity of any given article title is given as its share of the total number of articles from that year.

For a better overview, some of the headings have been normalized. Most notably, dates have been removed from titles like "Paris, den 18. October". Some common spelling and OCR variations have also been homogenised (i.e. _Todes-Anzeige_ vs _Todes - Anzeige_ vs _Todes-Anzeigen_), as well as some cases of semantic similarity (i.e. _Telegraphische Nachrichten_ has been joined with _Telegramme_).

Please take these visualizations with a grain of salt. Most importantly, keep in mind that the structure of headings and sub-headings can be very complex in the actual newspapers and might thus not be always accurately reflected in the data - some titles are "invisible" in these metrics because they are _inside_ another article.

""")

with open('top_headings.json', 'r', encoding='utf8') as f:
    contents = f.read()
    top_headings = json.loads(contents)

@st.cache()
def load_headings_df():
    return pd.read_csv('headings_df.tsv', sep='\t', encoding='utf8')

headings_df = load_headings_df()

ticksrange = np.arange(1802,1889)
xlabels = [num if num%5==0 else '' for num in np.arange(1802,1889)]

heading_options = st.multiselect(label='Select the headings you are interested in:', options=top_headings)
print(heading_options, type(heading_options))

if len(heading_options) > 0:

    headings_plot_df = headings_df[['year', 'heading2', 'weight']][headings_df.heading2.isin(heading_options)].copy()
    pt = headings_plot_df.pivot_table(index='year', columns='heading2')
    
    fig = plt.figure(figsize=(12,7))
    ax = fig.add_subplot()   
    ax.set_ylabel('popularity', labelpad=15)
    headings_plot = pt['weight'].plot(ax=ax, linewidth=2)
    headings_plot.legend()
    plt.xticks(ticks=ticksrange, labels=xlabels)
    plt.tick_params(axis ='x', rotation = 45, labelsize=12)
    plt.tick_params(axis ='y', labelsize=12)

    st.pyplot(fig)

else:

    fig = plt.figure(figsize=(12,7))
    ax = fig.add_subplot()   
    ax.set_ylabel('popularity', labelpad=15)

    st.pyplot(fig)




st.write("""#""")
st.subheader('Locations in article headings')

@st.cache()
def import_loc_headings_data():
    with open('places_by_year.json', 'r', encoding='utf8') as f:
        contents = f.read()
        places_by_year = json.loads(contents)

    return places_by_year

places_by_year = import_loc_headings_data()

st.write("""
This is a representation of all the geographical data in the headings. The toponymes have been detected using a custom SpaCy NER model and linked with the help of GeoNames data.

Again, this visualisation does not represent all of the geographical data present in the newspapers, but only the headings. Above all, this leaves out many Baltic and Russian locations that are often found under _Inland_ or other sections and are thus not reflected in the headings. On the other hand, 19th century newspapers were usually more concerned with news from abroad.

""")

map_timerange = st.slider('Select a timerange', min_value=1802, max_value=1888, value=(1802,1888))


def generate_map_from_timerange(timerange, places_by_year):

    timerange = range(timerange[0], timerange[1])

    m = folium.Map(location=[50, 15],
                   zoom_start=3,
                   tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}',
                   attr='Tiles &copy; Esri &mdash; Source: US National Park Service')
    
    places_in_timerange = {}
    
    for year in timerange:

        year_data = places_by_year[str(year)]
        max_count = 0
        
        for i, j in zip(year_data['name'].keys(), year_data['name'].values()):
            
            placename = j
            x = year_data['x'][i]
            y = year_data['y'][i]
            count = year_data['count'][i]
            
            if placename in places_in_timerange.keys():
                places_in_timerange[j]['count'] += count
                if places_in_timerange[j]['count'] > max_count:
                    max_count = places_in_timerange[j]['count']
                
            else:
                places_in_timerange[j] = {'x': x,
                                          'y': y,
                                          'count': count}
                
    for place in places_in_timerange.keys():
        
        location_data = places_in_timerange[place]
        
        x = location_data['x']
        y = location_data['y']
        count = location_data['count']
        size = count*(max_count/(len(timerange)))+10000
        
        folium.Circle(location=[y, x],
                    popup=f'{place}: {count}',
                    radius=size,
                    color="#3186cc",
                    fill=True,
                    fill_color="#3186cc").add_to(m)
    
    return folium_static(m)


generate_map_from_timerange(map_timerange, places_by_year)












