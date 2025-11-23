import cv2
import numpy as np

def detect_led_state(frame, brightness_threshold=250):
    if frame is None or frame.size == 0:
        print("Erreur: ROI vide ou incorrect.")
        return 0

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    _, _, v = cv2.split(hsv)
    mean_brightness = np.mean(v)

    return 1 if mean_brightness > brightness_threshold else 0

def binary_to_decimal(binary_code):
    return int(binary_code, 2)

def binary_to_char(binary_code):
    decimal_value = binary_to_decimal(binary_code)
    return chr(decimal_value)

video_path = 'C:\\Users\\strabi\\Desktop\\VLC Project\\stopped.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Erreur: Impossible d'ouvrir la vidéo.")
    exit()

led_positions = [
    (106, 145, 134, 165),  # Coordonnées pour les LEDs
    (265, 156, 286, 182),
    (372, 158, 392, 186),
    (506, 168, 525, 197),
    (109, 237, 130, 257),
    (232, 255, 266, 278),
    (374, 261, 400, 279),
    (490, 251, 513, 273)
]

# Initialisation des variables pour le traitement
current_word = ""  # Chaîne pour stocker le mot reçu
frame_count = 0  # Compteur de frames

# Paramètre pour contrôler le nombre de frames entre les clignotements
frames_between_blinks = 30  # Environ une seconde à 30 FPS

while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_blink_bits = []  # Liste pour stocker les bits du clignotement actuel

    for i, (x1, y1, x2, y2) in enumerate(led_positions):
        if x2 > frame.shape[1] or y2 > frame.shape[0] or x1 < 0 or y1 < 0:
            print(f"Coordonnées non valides pour LED {i + 1}.")
            continue

        led_roi = frame[y1:y2, x1:x2]
        if led_roi.size == 0:
            print(f"Erreur: ROI vide pour LED {i + 1}.")
            continue

        led_state = detect_led_state(led_roi)
        current_blink_bits.append(str(led_state))

        # Ajouter une annotation sur l'image pour indiquer l'état de la LED
        color = (0, 255, 0) if led_state == 1 else (0, 0, 255)  # Vert pour allumée, Rouge pour éteinte
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f'LED {i + 1}: {"On" if led_state == 1 else "Off"}', (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    if frame_count >= frames_between_blinks:
        received_bits = ''.join(current_blink_bits).zfill(8)  # Capture les bits actuels en une chaîne de 8 bits

        # Vérifiez si le code binaire n'est pas égal à '00000000'
        if received_bits != "00000000":
            # Convertir le code binaire en caractère ASCII
            received_char = binary_to_char(received_bits)
            current_word += received_char  # Ajouter le caractère au mot en cours
            print(f"Caractère reçu: {received_char} (binaire: {received_bits})")

        frame_count = 0  # Réinitialiser le compteur de frames pour le prochain clignotement

    # Afficher l'image avec les LEDs et le code binaire
    cv2.imshow('Video Frame with LEDs', frame)

    # Incrémenter le compteur de frames
    frame_count += 1

    # Attendre une courte période entre chaque lecture (33 ms correspond à environ 30 FPS)
    if cv2.waitKey(33) & 0xFF == ord('q'):  # Utiliser 'q' pour quitter la boucle prématurément
        break

# Libérer les ressources
cap.release()
cv2.destroyAllWindows()

# Afficher le mot final reçu
if current_word:
    print(f"Mot reçu: {current_word}")
else:
    print("Aucun mot valide détecté.")
