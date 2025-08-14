import rasterio
import numpy as np
import matplotlib.pyplot as plt
import os

# Dossier contenant les bandes (par ex. B2.tif, B3.tif, B4.tif)
folder = 'chemin/vers/stack/'

# Lister et charger les fichiers
band_files = sorted([os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.tif')])

# Charger toutes les bandes dans une stack (3D array : [band, height, width])
stack = []
for file in band_files:
    with rasterio.open(file) as src:
        stack.append(src.read(1))  # Lire la première (et unique) couche

stack = np.stack(stack)

print(f"Dimensions de la stack : {stack.shape} (bandes, hauteur, largeur)")

# Normalisation entre 0 et 1
stack = stack.astype(np.float32)
stack_norm = (stack - stack.min()) / (stack.max() - stack.min())

# Exemple : utiliser les bandes 4, 3, 2 de Sentinel-2 pour RGB
rgb = np.stack([stack[3], stack[2], stack[1]], axis=-1)

# Normalisation simple pour affichage
rgb_norm = (rgb - rgb.min()) / (rgb.max() - rgb.min())

plt.figure(figsize=(10, 10))
plt.imshow(rgb_norm)
plt.title("Image RGB")
plt.axis('off')
plt.show()

# Pour Sentinel-2 : B8 = infra-rouge proche, B4 = rouge
nir = stack[7].astype(float)
red = stack[3].astype(float)

ndvi = (nir - red) / (nir + red + 1e-10)

plt.imshow(ndvi, cmap='RdYlGn')
plt.colorbar(label='NDVI')
plt.title("Indice NDVI")
plt.axis('off')
plt.show()
