import pandas as pd
import streamlit as st
import requests
import json
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
import shap
from streamlit_shap import st_shap

sample = pd.read_parquet('sample.parquet').drop(columns = 'TARGET')

def main():
    
    st.set_page_config(layout="wide")
    
    api_prediction = "https://api-p7-a17981e4f527.herokuapp.com/predict"    
    api_distribution = "https://api-p7-a17981e4f527.herokuapp.com/distribution"    
    api_shap = "https://api-p7-a17981e4f527.herokuapp.com/" 
    
    shap_values =  np.asarray(requests.get(api_shap).json())
    
    variables = [
    'Notation bancaire',
    "Âge",
    'Crédits en cours',
    'Prix biens consommation',
    'Crédits clos',
    "Enseignement supérieur",
    'Crédits refusés',
    'Mois avec retard de paiement',
    'Montant total prêt'
]

    threshold = 0.46

    st.title('Tableau de bord solvabilité client')
    
    st.write('Un client vous sollicite pour l\'octroi d\'un crédit. Ce tableau de bord permet de prédire s\'il aura des difficultés de remboursement (retards importants et chroniques de paiement des échéances). Merci de remplir les informations ci-dessous et cliquer sur le bouton "Prédire la solvabilité". Si vous ignorez une valeur, inscrivez 0 par défaut.')
    
    col1, col2, col3 = st.columns([1, 2, 2])
    
    with col1:
        
        var1 = st.number_input('Notation bancaire du client', min_value=0.0, max_value = 1.0,value=0.45, step=0.01)
        st.session_state['Notation bancaire'] = var1

        var2 = st.number_input('Âge en années',min_value=0.0, value=36.00, step=1.0)
        st.session_state['Âge'] = var2
        
        var3 = st.number_input('Nombre de crédits en cours dans notre agence', min_value=0.0, value=9.0, step=1.0)
        st.session_state['Crédits en cours'] = var3

        var4 = st.number_input('Si crédit à la consommation, prix total des biens pour le prêt demandé', min_value=0.0, value=1035000.0, step=0.1)
        st.session_state['Prix biens consommation'] = var4
        
        var5 = st.number_input('Nombre de crédit clos dans notre agence', min_value=0.0, value=4.0, step=100.0)
        st.session_state['Crédits clos'] = var5
        
        var6 = st.number_input('Combien de demandes de crédits ont été refusées par le passé ?', min_value=0.0, value=0.0, step=1.0)
        st.session_state['Crédits refusés'] = var6

        var7 = st.number_input('Combien de mois connus avec retard de paiement de crédit?', min_value=0.0, value=0.0, step=1.0)
        st.session_state['Mois avec retard de paiement'] = var7

        var8 = st.number_input('Montant total du prêt demandé', min_value=0.0, value=1035000.0, step=1.0)
        st.session_state['Montant total prêt'] = var8
        
        var9 = st.checkbox("Le client a un diplôme de l'enseignement supérieur")
        st.session_state['Enseignement supérieur'] = var9

    with col2:
        
        st.write("Corrélation des variables")
        
        var_corr_1 = st.selectbox("Choisir une 1ère variable à étudier", variables)
        var_corr_2 = st.selectbox("Choisir une 2ème variable à étudier", variables)
        
        response_corr_1 = requests.post(api_distribution, data=var_corr_1.encode("latin1")).json()
        response_corr_2 = requests.post(api_distribution, data=var_corr_2.encode("latin1")).json()
        
        if var_corr_1 == 'Enseignement supérieur' :
            response_corr_1[0] = [float(s) for s in response_corr_1[0]]
            response_corr_1[1] = [float(s) for s in response_corr_1[1]]
        
        if var_corr_2 == 'Enseignement supérieur' :
            response_corr_2[0] = [float(s) for s in response_corr_2[0]]
            response_corr_2[1] = [float(s) for s in response_corr_2[1]]
            
        fig, ax = plt.subplots()
        plt.title("Corrélation des variables "+var_corr_1+" et "+var_corr_2)
        plt.xlabel(var_corr_1)
        plt.ylabel(var_corr_2)
        plt.scatter(st.session_state[var_corr_1], st.session_state[var_corr_2], c = "blue", zorder=3, marker='D', s=50)
        plt.scatter(response_corr_1[0], response_corr_2[0], c = "green", zorder=2, s=5)
        plt.scatter(response_corr_1[1], response_corr_2[1], c = "red", zorder=2, s=5)
        ax.legend(["Votre client","Solvables","Non solvables"])
        
        st.pyplot(fig)
        
        
    with col3 :
        
        st.write("Distribution des variables")
        
        var_distribution = st.selectbox("Choisir une variable à étudier", variables)
        
        response = requests.post(api_distribution, data=var_distribution.encode("latin1")).json()
        
        if var_distribution == 'Enseignement supérieur' :
            response[0] = [float(s) for s in response[0]]
            response[1] = [float(s) for s in response[1]]
        
        fig, ax = plt.subplots()
        plt.axvline(x=st.session_state[var_distribution], color = "blue")
        plt.title("Distribution de la variable "+var_distribution)
        ax.hist(response[0], color = "green")
        ax.hist(response[1], color = "red")
        ax.legend(["Votre client","Solvables","Non solvables"])

        st.pyplot(fig)

    predict_btn = st.button('Prédire la solvabilité', use_container_width=True, type = "primary")

    if predict_btn:
        
        data = {
            
            'Notation bancaire':  var1,
            'Âge': var2,
            'Crédits en cours': var3,
            'Prix biens consommation':var4,
            'Crédits clos': var5,
            'Enseignement supérieur': var9,
            'Crédits refusés': var6,
            'Mois avec retard de paiement':var7,
            'Montant total prêt': var8
            
            } 
                
        json_data = json.dumps(data)
                
        response = requests.post(api_prediction, json=json_data).json()
        
        prediction = response[0][0]
        
        json_response_shap = response[1]
    
        shap_values_dict_reconstructed = json.loads(json_response_shap)

        shap_values_reconstructed = shap.Explanation(
            values=np.array(shap_values_dict_reconstructed['values']),
            base_values=np.array(shap_values_dict_reconstructed['base_values']),
            data=np.array(shap_values_dict_reconstructed['data']),
            feature_names=shap_values_dict_reconstructed['feature_names']
        )[0]
        
        solvable = prediction < threshold
        
        threshold_gauge = threshold*100
        
        fig, ax = plt.subplots()
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            number = {'suffix': " %", 'prefix':'Indicateur de défaillance : ', 'font': {'size': 20}},
            value = prediction*100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
        'bar': {'color': "#838383"},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, threshold_gauge], 'color': '#5DFF6C'},
            {'range': [threshold_gauge, 100], 'color': '#FF7171'}],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': prediction*100}}))


        
        col1, col2, col3 = st.columns(3)
    
        with col1:
        
            st.plotly_chart(fig)        
            
            if solvable:
                st.write("Il est possible d'accorder le prêt demandé par ce client.")
            else:
                st.write("Il n'est pas possible d'accorder le prêt demandé par ce client.")
            
        with col2:
            
            st.write("Explication de la prédiction")
        
            fig, ax = plt.subplots()
            fig = shap.plots.bar(shap_values_reconstructed)
            st_shap(fig, width=700, height = 400)
            
            st.write("Chaque variable a un poids positif ou négatif, plus ou moins fort, sur la prédiction réalisée pour ce client. Vous trouverez ci-dessus les explications concernant le score de défaillance prédit.")
            
        with col3:
            
            st.write("Explication générale du modèle")
          
            fig, ax = plt.subplots()
            fig = shap.summary_plot(shap_values, features=sample)
            st_shap(fig, width=700, height = 400)
            
            st.write("Vous trouverez ci-dessus l'impact général de chaque variable sur l'algorithme de prédiction du score de défaillance. Par exemple, plus la notation est forte, plus le score de défaillance sera faible. A l'inverse plus le nombre de prêts refusés est fort, plus le score de défaillance sera fort.")
        
        

if __name__ == '__main__':
    main()
