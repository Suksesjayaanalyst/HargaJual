import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import openpyxl

#Membuat Harga Jual

col1,col2 = st.columns(2)

excel = col1.file_uploader("Upload your excel file", type=['xlsx'])

hargajual = col2.file_uploader("Upload Harga Jual v2", type=['xlsx'])

masterdata = st.file_uploader("Upload Master Data", type=['xlsx'])



if excel is not None and hargajual is not None and masterdata is not None:
    data = pd.read_excel(excel)
    dataharga = pd.read_excel(hargajual)
    master = pd.read_excel(masterdata)
    dataharga['Margin_Lusin'] = dataharga['Margin_Lusin'].str.replace('%','').str.replace(',','').astype(float) / 100
    dataharga['Margin_Koli'] = dataharga['Margin_Koli'].str.replace('%','').str.replace(',','').astype(float) / 100
    dataharga['Margin_Special'] = dataharga['Margin_Special'].str.replace('%','').str.replace(',','').astype(float) / 100
    master.rename(columns={'Item No.':'ItemCode'}, inplace=True)
    data['ItemCode'] = data['ItemCode'].str.upper()
    data = pd.merge(data, master[['ItemCode', 'Sub Item']], on='ItemCode', how='left').rename(columns={'Sub Item':'Sub_Item'})

    data = data[['ItemCode', 'Sub_Item', 'Modal']]
    

    start = st.button("Start")
    if start:
        fornewitem = dataharga.groupby('Sub_Item').mean().reset_index()
        fornewitem.rename(columns={'Margin_Lusin':'Margin_Lusin_New', 'Margin_Koli':'Margin_Koli_New', 'Margin_Special':'Margin_Special_New'}, inplace=True)

        final = pd.merge(data, dataharga, on='ItemCode', how='left').rename(columns={'Harga_Modal':'Modal Terakhir'})
        final.fillna(0, inplace=True)
        
        final = final[['Sub_Item_x','ItemCode', 'Modal', 'Modal Terakhir', 'Margin_Lusin', 'Margin_Koli', 'Margin_Special','Harga_Jual_Lusin', 'Harga_Jual_Koli', 'Harga_Jual_Special']].rename(columns={'Sub_Item_x':'Sub_Item'})

        final = pd.merge(final, fornewitem[['Sub_Item', 'Margin_Lusin_New', 'Margin_Koli_New', 'Margin_Special_New']], on='Sub_Item', how='left')

        final['HargaLusinFinal'] = np.where(final['Margin_Lusin_New'] == 0,(((final['Modal'] * final['Margin_Lusin']) + final['Modal'])/500).round() * 500 ,(((final['Modal'] * final['Margin_Lusin_New']) + final['Modal'])/500).round() * 500 )

        final['HargaKoliFinal'] = np.where(final['Margin_Koli_New'] == 0,(((final['Modal'] * final['Margin_Koli'])+final['Modal'])/500).round() * 500 ,(((final['Modal'] * final['Margin_Koli_New'])+final['Modal'])/500).round() * 500 )

        final['HargaSpecialFinal'] = np.where(final['Margin_Special_New'] == 0,(((final['Modal'] * final['Margin_Special'])+final['Modal'])/500).round() * 500 ,(((final['Modal'] * final['Margin_Special_New'])+final['Modal'])/500).round() * 500 )

        st.dataframe(final)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            final.to_excel(writer, index=False, sheet_name="FinalHargaJual")
        st.download_button("Download List Upload", data=output.getvalue(), file_name="Harga Jual.xlsx")


if excel is None or hargajual is None or masterdata is None:
    st.warning("Please upload your excel file")