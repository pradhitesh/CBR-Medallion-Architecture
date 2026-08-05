import os
import json

from src.asset.download import download_assets

def load_codebook(use_latest=True):
    """
    Load codebooks from JSON files and create a configuration
    
    Args:
        use_latest (bool): Whether to download the latest codebooks from CBR Data Assets Server
    """    
    
    # Check if codebooks need to be downloaded
    if use_latest:
        download_assets(codebook_only=True)

    # Define allowed codebooks  
    ALLOWED_CODEBOOKS = ['Clinical', 'BBC', 'AFT', 
                         'AUDIO', 'COGNITO', 'APOE',
                         'GAIT', 'MRI', 'OCT', 
                         'Socio', 'SPIRO', 'Balance', 
                         'Alamar', "Simoa"]
    
    config = {}
    for codebook_name in ALLOWED_CODEBOOKS:
        path = f"assets/Codebook_{codebook_name}.json"

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Codebook file not found for {codebook_name}"
            )
        
        try:
            with open(path, 'r') as file:
                cb = json.load(file)
        except Exception as e:
            raise ValueError(
                f"Error loading codebook JSON for {codebook_name}: {str(e)}"
            )

        # Important: Loop through all the questions and add them to the config
        # Raises an error if a duplicate question is detected
        for q in cb.get("questions", []):
            q_name = q["name"]
            # # Rule 1: Check if q_name from Codebook exists in shared.local_concept
            # if q_name not in df["source_field_name"].to_list():
            #     raise ValueError(f"'{q_name}' not found in the table 'shared.local_concept'. Available from: '{get_latest_concept_id()+1}'")
            
            # Rule 2: Check if q_name is duplicated
            if q_name in config:
                raise ValueError(f"Duplicate question detected: {q_name}")

            q['codebook'] = codebook_name
            config[q_name] = q

    return config
