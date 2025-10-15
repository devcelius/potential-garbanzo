a = [[['\\ngreenhouse effect\\nelectrical conductivity\\nAluminum alloy\\nCopper\\ncapacitor\\ncapacity\\ntotal mass\\n\\t5.65 kg\\n\\t25 mmHg\\ngas mixture\\nelectric field\\nelectric charge\\nelectron\\tnegative charge'], 16], [['No data provided'], 16], [['\\nelements ', '\\ncritical ', '\\nto ', '\\nstandards ', '\\ndimensions ', '\\ncalculations ', '\\ncalculations ', '\\ndeleted ', '\\nto ', '\\note ', '\\MONKEY'], 16], [['\\npHysical quantities\\n', '\\nStandard units for length:\\n', '\\ngallon\\n', '\\nton\\n', '\\ntrope unit (old standard)\\n', '\\ncentimetre-gallon (old imperial standard)\\n', '\\ntrope (old British standard)\\n', '\\ncubit (old biblical standard)', '', '\\nStandards and Units\\n', '\\nLength:\\n', '\\ngallon\\n', '\\nton\\n', '\\ntrope unit\\n'], 16], [['mass', 'length', 'time', 'force', 'speed', 'density', 'resistance', 'temperature', 'luminous intensity', 'magnetic field strength'], 16], [['\\ntimes 4.3', 'standard length: one meter', 'accessibility to calibration standards', 'invariability to environmental changes', 'Na-tional Institute of Standards and Technology (NIST)', 'General Conference on Weights and Measures'], 16], [[], 16], [['\\nQuantum Mechanics', '\\nWave-Particle Duality', '', '\\nElectromagnetic Spectrum', '\\nRadio waves', '\\nMicrowaves', '\\nInfrared radiation', '\\nVisible light', '\\nUltraviolet radiation', '\\nX-rays', '\\nGamma rays', '', '\\nThermodynamics', '\\nZeroth Law of Thermodynamics', '\\nFirst Law of Thermodynamics', '\\nSecond Law of Thermodynamics', '\\nHeat Transfer', '\\nTemperature', '', '\\nElectromagnetism', '\\nElectric Fields', '\\nMagnetic Fields', '\\nLorentz Force'], 16], [['\\nmeter', '\\nspeed of light', '\\ntime (second)', '\\ncurrent standard unit for time improved by a factor of 1000 since publication', '\\nfundamental physical quantity', '\\ngenerated in terms of speed of light and second'], 17], [['\\#Monkeys'], 17], [[], 17], [['\\npower plant output\\nSI units\\nnuclear event time interval\\nTable 1-2\\n\\pregular conference on weights and measures\\n\\preﬁxes\\n\\nMONKEY'], 17], [['\\ng = 9.81 m/s^2'], 17], [['\\ngigawatts\\nnanoseconds\\nkg\\nMg\\nns\\nGaussian system\\nBritish system\\nfoot\\npound\\nsecond\\nMONKEY'], 17], [["\\Newton's Law of Cooling", '', '', '\\nFirst law ( heat flows from hotter body to cooler one \\n)'], 17], [['\\SI', 'U.S.', 'National Institute of Standards and Technology', 'SI System', 'American Association of Physics Teachers', 'Robert A. Nelson', 'Special Publication 811', 'Na-'], 17], [['\\n', 'Newton', 'Unit of force', '2.00 m/s² ', 'kg', 'm', 'kg·s⁻¹', 'N', 'J', 'W', 's ', '', '\\n', 'Celsius', 'Unit of temperature'], 17], [['\\#Physics', 'Monkey', '', '\\#Chemistry', 'Monkey', '', '\\#Mathematics', 'Monkey'], 17], [['\\nmeter', '\\nkelvin', '\\namperes', '\\ncandela', '\\nda', '\\ng', '\\kmol'], 17], [['\\ntemperature Kelvin (K)\\n', '', '\\nelectric charge Coulomb (C)\\n', '', '\\nelectric current Ampere (A)\\n', '', '\\ngeneral time Second (s)\\n'], 17], [[], 17], [['\\nGiga', '\\nPico', '\\nFemto', '\\nNano', '\\nMicro', '\\nPeta', '\\nExa', '\\nZetta', '\\nYotta', '\\nMega', '\\nKilo', '\\nHecto', '\\nDeka', '\\nCenti', '\\nMilli', '\\nTera', '\\nGiga'], 17], [[], 17], [[], 17]]
import torch
from transformers import AutoTokenizer, AutoModel
import chromadb
from tqdm import tqdm
import random

chromadb.api.client.SharedSystemClient.clear_system_cache()
client = chromadb.PersistentClient(path=r"C:\Users\Manit\chroma")
collection_name = "Maine2.0_DEV1"
collection = client.get_or_create_collection(collection_name)
tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
model = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')
ids = []
vectors = []
metadatas = []
documents = []

for index, (doc, page_number) in tqdm(enumerate(a)):
    for index2, i in enumerate(doc):
        if not i.strip():
            continue
        tokenized = tokenizer(
            i,
            padding=True,
            truncation=True,
            add_special_tokens=True,
            return_attention_mask=True,
            return_tensors="pt"
        )

        with torch.no_grad():
            embedding = model(**tokenized)

        vector = embedding.last_hidden_state[:, 0].squeeze().numpy()  # Use CLS token


        # Save all data for batch add
        vectors.append(vector)
        documents.append(i)
        metadatas.append({"page": page_number})
        
        ids.append(str(random.random()))

collection.add(
    ids=ids,
    embeddings=vectors,
    documents=documents,
    metadatas=metadatas
)

print(f"✅ Added {len(vectors)} text chunks to ChromaDB.")
query = "What is the acceleration due to gravity(g)?"
tokenized = tokenizer(
    query,
    padding=True,
    truncation=True,
    add_special_tokens=True,
    return_attention_mask=True,
    return_tensors="pt"
)

with torch.no_grad():
    query_embedding = model(**tokenized).last_hidden_state.mean(dim=1).squeeze().numpy()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5
)

for doc, meta, dist in zip(
    results["documents"][0],
    results["metadatas"][0],
    results["distances"][0]
):
    print(f"- {doc.strip()}  (page={meta['page']}, distance={dist:.4f})")