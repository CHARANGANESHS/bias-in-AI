import os
import json
import openai
from tqdm import tqdm
import requests
from pathlib import Path

OPEN_API_KEY: str = "" # ! Need to fill this, Refer to the OPENAI docs

folder_path: str = "./data/synthetic_data_generation"

prompt_file_path: str = f"{folder_path}/gender_neutral_prompts.json"
url_file_path: str = f"{folder_path}/gender_neutral_url.json"


def get_url(prompt_file_path: str, url_file_path: str):
    with open(prompt_file_path, "r") as f:
        data = json.load(f)["data"]
    
    url_data = []
    
    for idx, prompt in tqdm(enumerate(data), total=len(data), desc="Generating images"):
        try: 
            response = openai.Images.generate(
                prompt = prompt,
                model = "dall-e-3",
                size = "1024x1024",
                quality = "hd",
                n = 1
            )

            image_url = response['data'][0]['url']
            url_data.append(image_url)
            
        
            with open(url_file_path, "w") as f:
                json.dump({"data": url_data}, f, indent=4)
        except Exception as e: 
            print(f"Problem generating the image {idx} : Exception : {e}")
        
        
    print("JSON file created successfully")
    
def download_url(folder_path: str):
    image_folder = "synthetic_images"
    upload_folder = f"{folder_path}/{image_folder}"
    
    Path(upload_folder).mkdir(parents=True, exist_ok=True)
    
    url_file_path = f"{folder_path}/gender_neutral_url.json"
    with open(url_file_path, "r") as f:
        url_data = json.load(f)["data"]
    
    for idx, url in tqdm(enumerate(url_data), total=len(url_data), desc="Downloading images"):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if 'png' in content_type:
                ext = '.png'
            elif 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            else:
                ext = '.jpg' 
            
            image_path = f"{upload_folder}/image_{idx}{ext}"
            with open(image_path, 'wb') as img_file:
                for chunk in response.iter_content(chunk_size=8192):
                    img_file.write(chunk)
                    
        except Exception as e:
            print(f"Error downloading image {idx} from {url}: {e}")
    
    print(f"Downloaded {len(url_data)} images to {upload_folder}")


"""
    ! These prompts are not working
    ! "A Russian ballet dancer rehearsing for a performance.",  
"""

if __name__ == "__main__":

    download_url(folder_path)
    pass