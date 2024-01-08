import pandas as pd
import streamlit as st
import requests
import json

def main():
    api_url = "https://api-p7-a17981e4f527.herokuapp.com/predict"  

    st.title('Tableau de bord solvabilité client')

    var1 = st.number_input('var1',
                                 min_value=0., value=3.87, step=1.)

    var2 = st.number_input('var2',
                              min_value=0., value=28., step=1.)

    var3 = st.number_input('var3',
                                   min_value=0., value=5., step=1.)

    var4 = st.number_input('var4',
                                     min_value=0., value=1., step=1.)

    var5 = st.number_input('var5',
                                 min_value=0, value=1425, step=100)

    predict_btn = st.button('Prédire')
    if predict_btn:
        
        data = {
    "features": [[var1, var2, var3, var4, var5]] 
    }
        
        json_data = json.dumps(data)
        
        headers = {'Content-Type': 'application/json'}

        response = requests.post(api_url, data=json_data, headers=headers).json()
    
                
        st.write(format(response))


if __name__ == '__main__':
    main()
