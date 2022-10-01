# Purpose: An interactive app that allows users to test how a drug can potentially impact gastric H/K ATPase activity

# Before using this, make sure you have downlaoded padel.sh and padel-descriptor from the following:
# padel.sh: https://github.com/dataprofessor/bioinformatics/raw/master/padel.sh
# padel.zip:  https://github.com/dataprofessor/bioinformatics/raw/master/padel.zip

# You also need to have run through the .ipynb file once to get a new pickle file

# Libraries
import streamlit as st # quick app development for models
import pandas as pd # dataframe management
import pickle # save and reuse already trained models 
import subprocess # access subprocesses
import os # access folders and files in operating system
import base64 # convert strings to base64 to download file

# Molecular descriptor calculator from user uploaded drug molecules
def padel_descriptor():
    # calculate descriptors by bashing padel.sh padel.sh
    process = subprocess.Popen(["bash","padel.sh"], stdout=subprocess.PIPE)
    output, error = process.communicate()
    os.remove('molecule.smi')

# Download predictions
def pred_download(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download your predictions!</a>'
    return href

# Model building
def build_model(input_data):
    # Reads in saved regression model
    with open('gastricactivity_knn_model.pkl', 'rb') as f:
        load_model = pickle.load(f)
    # Apply model to make predictions
    prediction = load_model.predict(input_data)
    # output prediction
    st.header('**Prediction output**')
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(pred_molecules[1], name='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    st.markdown(pred_download(df), unsafe_allow_html=True)

# App title and description
st.markdown("""
# Gastric H/K ATPase Inhibition Prediction App 
---
This app allows you to predict the inhibition of the Gastric H/K ATPase protein by various drugs. This protein is responsible for making the stomach acidic, which is important in cases where patients uncontrollably aspirate.
---
""")

# Sidebar to upload data
with st.sidebar.header('1. Upload your CSV data'):
    uploaded_file = st.sidebar.file_uploader("Upload input file", type=['txt'])
    st.sidebar.markdown("""
Each row should be a separate drug with the first column as the drug's SMILE and the second column as the drug's CHEMBL ID, separated by a comma.
""")

# allow user to make prediction with uploaded molecule names
if st.sidebar.button('Make a Prediction!'):
    # load in prediction molecules and save as molecule.smi
    pred_molecules = pd.read_table(uploaded_file, sep=',', header=None)
    pred_molecules.to_csv('molecule.smi', sep = '\t', header = False, index = False)

    # show molecules have been uploaded and their names as dataframe
    st.header('**Original input data**')
    st.write(pred_molecules)

    # calculate molecule descriptors
    with st.spinner("Calculating molecular descriptors"):
        padel_descriptor()

    # Read in calculated descriptors and display the dataframe and shape
    st.header('**Molecular Descriptors**')
    molecule_descriptors = pd.read_csv('descriptors.csv')
    st.write(molecule_descriptors)
    st.write(molecule_descriptors.shape)

    # Read descriptor list used in previously built model and shrink predicted molecule descriptors to model molecule descriptors
    st.header('**Subset of descriptors from previously built models**')
    molecule_descriptors_model_cols = list(pd.read_csv('featuredata.csv').columns)
    molecule_descriptors_sub = molecule_descriptors[molecule_descriptors_model_cols]
    st.write(molecule_descriptors_sub)
    st.write(molecule_descriptors_sub.shape)

    # Apply trained model to make prediction on query compounds
    build_model(molecule_descriptors_sub)
else:
    st.info('Follow instructions in sidebar to begin')