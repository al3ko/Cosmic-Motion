import os
import urllib.request

# Verified high-resolution texture map URLs
TEXTURE_URLS = {
    "sun.jpg": "https://raw.githubusercontent.com/stemkoski/stemkoski.github.io/master/Three.js/images/sun.jpg",
    "mercury.jpg": "https://raw.githubusercontent.com/stemkoski/stemkoski.github.io/master/Three.js/images/mercury.jpg",
    "venus.jpg": "https://raw.githubusercontent.com/stemkoski/stemkoski.github.io/master/Three.js/images/venus.jpg",
    "earth.jpg": "https://raw.githubusercontent.com/stemkoski/stemkoski.github.io/master/Three.js/images/earth-sphere.jpg",
    "mars.jpg": "https://raw.githubusercontent.com/stemkoski/stemkoski.github.io/master/Three.js/images/mars.jpg",
    "jupiter.jpg": "https://raw.githubusercontent.com/stemkoski/stemkoski.github.io/master/Three.js/images/jupiter.jpg",
    "saturn.jpg": "https://raw.githubusercontent.com/stemkoski/stemkoski.github.io/master/Three.js/images/saturn.jpg",
    "uranus.jpg": "https://raw.githubusercontent.com/stemkoski/stemkoski.github.io/master/Three.js/images/uranus.jpg",
    "neptune.jpg": "https://raw.githubusercontent.com/stemkoski/stemkoski.github.io/master/Three.js/images/neptune.jpg",
    "moon.jpg": "https://raw.githubusercontent.com/stemkoski/stemkoski.github.io/master/Three.js/images/moon.jpg"
}

os.makedirs("assets/textures", exist_ok=True)
print("Downloading high-resolution planetary textures...")

# Headers to prevent HTTP 403 Forbidden errors
req_headers = {'User-Agent': 'Mozilla/5.0'}

for filename, url in TEXTURE_URLS.items():
    dest_path = os.path.join("assets/textures", filename)
    print(f"Downloading {filename}...", end=" ", flush=True)
    try:
        req = urllib.request.Request(url, headers=req_headers)
        with urllib.request.urlopen(req) as response, open(dest_path, 'wb') as out_file:
            out_file.write(response.read())
        print("Done!")
    except Exception as e:
        print(f"Failed ({e})")

print("\nFinished downloading textures to assets/textures/")