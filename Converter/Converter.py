#!/usr/bin/env python
# coding: utf-8

# # **Stap 1: Packages**
# 
# In Python worden "libraries" vaak vertaald als "bibliotheken" of "modules." Een library (bibliotheek) in Python is een verzameling van vooraf geschreven code die functies en hulpmiddelen biedt om specifieke taken uit te voeren zonder dat je die code zelf hoeft te schrijven. Deze bibliotheken kunnen functies en klassen bevatten die handig zijn voor verschillende soorten taken, zoals het verwerken van gegevens, het maken van grafieken, het uitvoeren van wiskundige berekeningen, en nog veel meer. Het gebruik van bibliotheken bespaart programmeurs tijd en moeite, omdat ze bestaande code kunnen hergebruiken in plaats van alles vanaf nul te schrijven.


import pandas as pd
import random
import streamlit as st

uploaded_file = st.file_uploader("Upload File")

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    def replace_words_v2(description, row):
        if not isinstance(description, str):  # Controleren of de beschrijving een string is
            return description
        
        for header in df.columns:
            if header in description:
                value = row[header]
                if pd.isna(value):  # Als de waarde NaN is, sla deze kolom over
                    continue
                description = description.replace(f'[{header}]', str(value))
        return description



    # Update de beschrijvingen in de 'Product description' kolom opnieuw
    df['Product description updated'] = df.apply(lambda row: replace_words_v2(row['Product description'], row), axis=1)

    # Toon de eerste paar rijen van de bijgewerkte DataFrame
    df[['Product description', 'Product description updated']].head()

    excel = df.to_excel("output.xlsx")
