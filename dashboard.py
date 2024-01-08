import pandas as pd
import streamlit as st
import requests
import json
import plotly.graph_objects as go


def main():
    api_url = "https://api-p7-a17981e4f527.herokuapp.com/predict"  
    
    threshold = 0.4

    st.title('Tableau de bord solvabilité client')

    var1 = st.number_input('var1', min_value=0, value=1, step=1)

    var2 = st.number_input('var2', min_value=0, value=1, step=1)

    var3 = st.number_input('var3', min_value=0, value=5, step=1)

    var4 = st.number_input('var4', min_value=0, value=5, step=1)

    var5 = st.number_input('var5', min_value=0, value=1425, step=100)

    predict_btn = st.button('Prédire')
    if predict_btn:
        
        data = {
    "features": [[var1, var2, var3, var4, var5]] 
    }
        
        json_data = json.dumps(data)
        
        headers = {'Content-Type': 'application/json'}

        response = requests.post(api_url, data=json_data, headers=headers).json()[0]
        
        solvable = response < threshold
        
        threshold_gauge = (1-threshold)*100
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            number = {'suffix': " % pour cet emprunt", 'prefix':'Client fiable à ', 'font': {'size': 20}},
            value = (1-response)*100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
        'bar': {'color': "#838383"},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, threshold_gauge], 'color': '#FF7171'},
            {'range': [threshold_gauge, 100], 'color': '#5DFF6C'}],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': (1-response)*100}}))
    
        if response < threshold:
            st.write("Il est possible d'accorder le prêt demandé par ce client.")
        else:
            st.write("Il n'est pas possible d'accorder le prêt demandé par ce client.")
        
        st.plotly_chart(fig)

if __name__ == '__main__':
    main()
