import cv2
import numpy as np

# Charger la vidéo
video_path = 'C:\\Users\\strabi\\Desktop\\VLC Project\\VIDEO.mp4'
cap = cv2.VideoCapture(video_path)

# Vérifier si la vidéo s'est bien ouverte
if not cap.isOpened():
    print("Erreur lors de l'ouverture de la vidéo")
    exit()

# Tableau pour stocker les valeurs binaires des clignotements
binary_values = []

# Variable pour suivre l'état précédent des LEDs
previous_states = None

# Facteur d'échelle pour réduire la taille des fenêtres
scale_factor = 0.5

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convertir l'image en niveaux de gris
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Appliquer un flou pour réduire le bruit
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)

    # Appliquer un seuil pour détecter les zones lumineuses
    _, thresh = cv2.threshold(blurred, 220, 255, cv2.THRESH_BINARY)

    # Détecter les cercles dans l'image
    circles = cv2.HoughCircles(thresh, cv2.HOUGH_GRADIENT, dp=1.0, minDist=30,
                               param1=50, param2=30, minRadius=10, maxRadius=20)

    # Mapper les cercles détectés en valeurs binaires
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        led_states = [0, 0, 0, 0]
        
        for (x, y, r) in circles:
            # Déterminer quel LED le cercle correspond
            if x < 100 and y < 100:
                led_states[0] = 1
            elif x >= 100 and y < 100:
                led_states[1] = 1
            elif x < 100 and y >= 100:
                led_states[2] = 1
            elif x >= 100 and y >= 100:
                led_states[3] = 1
        
        # Détecter un changement d'état (clignotement)
        binary_value = (led_states[0] << 3) | (led_states[1] << 2) | (led_states[2] << 1) | led_states[3]
        
        if previous_states != led_states:
            binary_values.append(binary_value)
            previous_states = led_states
            print(f'Clignotement détecté - Valeur binaire : {bin(binary_value)[2:].zfill(4)}')

    # Redimensionner les images pour réduire la taille des fenêtres
    resized_frame = cv2.resize(frame, None, fx=scale_factor, fy=scale_factor)
    resized_thresh = cv2.resize(thresh, None, fx=scale_factor, fy=scale_factor)

    # Afficher les résultats
    cv2.imshow("Clignotement des LED", resized_thresh)
    cv2.imshow("Vidéo Originale", resized_frame)

    # Quitter la boucle si l'utilisateur appuie sur 'q'
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# Libérer les ressources
cap.release()
cv2.destroyAllWindows()

# Afficher les valeurs binaires capturées
print("\nValeurs binaires capturées :")
for value in binary_values:
    print(f'Valeur binaire : {bin(value)[2:].zfill(4)}')
