import os
import cv2
import numpy as np
import pickle
from deepface import DeepFace

DATASET_PATH = "Our faces"
MODEL_NAME = "Facenet512"
known_embeddings = {}
skipped_log = open("skipped_images.txt", "w")

for person_name in os.listdir(DATASET_PATH):
    person_folder = os.path.join(DATASET_PATH, person_name)
    if not os.path.isdir(person_folder):
        continue

    embeddings = []
    for img_name in os.listdir(person_folder):
        img_path = os.path.join(person_folder, img_name)
        try:
            img = cv2.imread(img_path)
            if img is None:
                skipped_log.write(f"Unreadable: {img_path}\n")
                continue

            img = cv2.resize(img, (160, 160))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            result = DeepFace.represent(img, model_name=MODEL_NAME, enforce_detection=False)[0]
            embeddings.append(result["embedding"])
            print(f"Processed {img_name} for {person_name}")
        except Exception as e:
            skipped_log.write(f"{img_path} - {e}\n")

    if embeddings:
        avg_embedding = np.mean(np.array(embeddings), axis=0)
        known_embeddings[person_name] = avg_embedding
        print(f"Saved embedding for {person_name}")
    else:
        skipped_log.write(f"No valid images for {person_name}\n")

with open("known_embeddings.pkl", "wb") as f:
    pickle.dump(known_embeddings, f)

skipped_log.close()
print("✅ Embeddings generated and saved successfully.")