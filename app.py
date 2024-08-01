import streamlit as st
import requests
import json
import time
import base64
from PIL import Image
import io

class FalAIImageGenerator:
    BASE_URL = "https://rest.alpha.fal.ai/playground/proxy/"
    HEADERS = {
        'authority': 'rest.alpha.fal.ai',
        'accept': 'application/json',
        'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
        'authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Inp1OTNQd2lxX3JHa0xqQzlua2tjaCJ9.eyJmYWwuYWkvcm9sZXMiOltdLCJpc3MiOiJodHRwczovL2F1dGguZmFsLmFpLyIsInN1YiI6ImdpdGh1YnwxMzM1NTEyNDciLCJhdWQiOlsiZmFsLWNsb3VkIiwiaHR0cHM6Ly9kZXYtbjJ0MWtqdW84dWgwZGRmZy51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzIyNTIwMTYzLCJleHAiOjE3MjI2MDY1NjMsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgb2ZmbGluZV9hY2Nlc3MiLCJhenAiOiJ2amZGd21LWWVXUW5PREhram5Cekh5Rk1wMmk4bHNrNSIsInBlcm1pc3Npb25zIjpbXX0.Zsx6Zt50e5TosOe56l7twIGUCqyIdYWesXqLiN7pHjJ01gVIdFfQgDr3lpP5qnzx2-KhSDRjaneo1S3eyCL3V3BS_aDr8zQuaU7OlL-Ph2Q8hoKOyHgj48oAYkCgTx64v3gm9qX9OJIIIBlkbdsZvIka3Ozgp54OFLRwPYHO26UZsxIt9GgOoadWm3lUwZSnIf_3TsSRz6ronLctoNuNMj0CPlkf-8VlOW7EXaqGOk5bIt07IGQwya6hQBz5GFEFv2k04R5B0njWGGrwLAwCD5A6LMBbhFa7ddrHj4PUVGQbEsixGs1vP5XortJGZynp56E7QcICfWwYs3WonHseXw',
        'content-type': 'application/json',
        'origin': 'https://fal.ai',
        'referer': 'https://fal.ai/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'x-fal-user-id': 'github|5c6na2onelw04sc0vpxr87z6'
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def generate_image(self, prompt, image_size="landscape_4_3", num_inference_steps=28,
                       guidance_scale=3.5, num_images=1, enable_safety_checker=True):
        payload = {
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "num_images": num_images,
            "enable_safety_checker": enable_safety_checker
        }

        # Initial request to start image generation
        self.session.headers['x-fal-target-url'] = 'https://queue.fal.run/fal-ai/flux/dev'
        response = self.session.post(self.BASE_URL, json=payload)
        response.raise_for_status()
        request_data = response.json()

        # Poll for status until completion
        status_url = request_data["status_url"]
        progress_bar = st.progress(0)
        status_text = st.empty()
        while True:
            self.session.headers['x-fal-target-url'] = f"{status_url}?logs=1"
            status_response = self.session.get(self.BASE_URL)
            status_response.raise_for_status()
            status_data = status_response.json()

            if status_data["status"] == "COMPLETED":
                progress_bar.progress(100)
                status_text.text("Image generation completed!")
                break
            elif status_data["status"] == "FAILED":
                raise Exception("Image generation failed")
            
            progress = status_data.get("progress", 0)
            progress_bar.progress(int(progress * 100))
            status_text.text(f"Generating image... {int(progress * 100)}% complete")
            time.sleep(0.5)  # Wait before polling again

        # Retrieve the generated image
        result_url = request_data["response_url"]
        self.session.headers['x-fal-target-url'] = result_url
        result_response = self.session.get(self.BASE_URL)
        result_response.raise_for_status()
        result_data = result_response.json()

        return result_data

def main():
    st.set_page_config(page_title="StreamAI Image Generator", page_icon="🎨", layout="wide")

    st.title("🎨 StreamAI Image Generator")
    st.write("Generate stunning AI images with ease!")

    # Sidebar for advanced options
    st.sidebar.header("Advanced Options")
    image_size = st.sidebar.selectbox("Image Size", ["landscape_4_3", "portrait_3_4", "square_1_1"])
    num_inference_steps = st.sidebar.slider("Inference Steps", 10, 50, 28)
    guidance_scale = st.sidebar.slider("Guidance Scale", 1.0, 10.0, 3.5)
    enable_safety_checker = st.sidebar.checkbox("Enable Safety Checker", value=True)

    # Main content
    prompt = st.text_input("Enter your image prompt:", "A beautiful sunset over a serene lake")
    
    if st.button("Generate Image"):
        generator = FalAIImageGenerator()
        
        try:
            with st.spinner("Generating image..."):
                result = generator.generate_image(
                    prompt,
                    image_size=image_size,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    enable_safety_checker=enable_safety_checker
                )
            
            image_url = result["images"][0]["url"]
            st.success("Image generated successfully!")
            
            # Display the generated image
            st.image(image_url, caption="Generated Image", use_column_width=True)
            
            # Provide download link
            response = requests.get(image_url)
            image = Image.open(io.BytesIO(response.content))
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            href = f'<a href="data:file/png;base64,{img_str}" download="generated_image.png">Download Image</a>'
            st.markdown(href, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    st.markdown("---")
    st.write("Created with ❤️ using Streamlit and FalAI")

if __name__ == "__main__":
    main()
