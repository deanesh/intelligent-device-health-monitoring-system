import sys
import os


sys.path.append(os.path.abspath("src"))

from ingestion.load_data import load_entities

data = load_entities("data/raw")
for entity, df in data.items():
    print(entity, df.shape)

