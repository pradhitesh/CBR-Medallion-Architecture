import requests
import argparse
import urllib3
import os
import re

# To suppress certification issues
urllib3.disable_warnings()

# Define CBR Data Assets download API
BASE_URL = "https://data-assets.cbr-iisc.ac.in/api/v1/assets/download"

# List of Assets to be downloaded from the CBR Data Assets Server
ASSETS = [
    "Mappings_Nurse_Short_Nurse_S2_SANSCOG_TLSA",
    "Mappings_Clinical_Short_Clinical_S2_SANSCOG_TLSA",
    "Mappings_Socio_S1_SANSCOG_TLSA",
    "Mappings_Home_S1_SANSCOG_TLSA",
    "vocabulary_download_v5_{111ec373-c766-4e16-ac86-c8d9e77f53ff}_1779597258942"
]

# List of Codebooks
CODEBOOKS = [
    "Codebook_BBC",
    "Codebook_AUDIO",
    "Codebook_SPIRO",
    "Codebook_GAIT",
    "Codebook_Socio",
    "Codebook_MRI",
    "Codebook_AFT",
    "Codebook_COGNITO",
    "Codebook_Clinical",
    "Codebook_OCT",
    "Codebook_Balance",
    "Codebook_APOE",
    "Codebook_Alamar",
    "Codebook_Simoa"
]

def extract_filename(response, fallback_name):
    """
    Extract filename from Content-Disposition header
    """
    content_disp = response.headers.get("Content-Disposition")

    if content_disp:
        match = re.search(r'filename="?([^"]+)"?', content_disp)
        if match:
            return match.group(1)

    # fallback (if header missing)
    return fallback_name

def download_assets(codebook_only: bool = False):
    """
    Download Assets from CBR Data Assets Server
    """
    os.makedirs("assets", exist_ok=True)

    assets_to_download = CODEBOOKS if codebook_only else ASSETS + CODEBOOKS
    for name in assets_to_download:
        try:
            url = f"{BASE_URL}/{name}"
            res = requests.get(url, verify=False, stream=True)

            if res.status_code == 200:
                filename = extract_filename(res, name)
                file_path = os.path.join("assets", filename)

                with open(file_path, "wb") as f:
                    for chunk in res.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                print(f"Saved: {file_path}")

            else:
                print(f"Failed {name}: {res.status_code}")

        except Exception as e:
            print(f"Error downloading {name}: {e}")


if __name__ == "__main__":
    # Setup parser
    parser = argparse.ArgumentParser(description="Download assets for centralised CBR Data Assets API server.")

    # Download only codebooks
    parser.add_argument("-c", "--codebooks", 
                        type=bool, default=False, 
                        help="If set as True, it will only download Codebooks. By default, it is set as False.")

    # Parse the arguments
    args = parser.parse_args()

    # Download
    download_assets(codebook_only=args.codebooks)