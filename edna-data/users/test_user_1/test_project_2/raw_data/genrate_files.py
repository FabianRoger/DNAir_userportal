import pandas as pd
import random
from datetime import datetime, timedelta

# Generate random but realistic parameters
n_stations = random.randint(3, 20)  # Number of sampling stations
base_samples_per_station = random.randint(10, 30)  # Base number of samples per station

# Calculate total expected samples and appropriate species count
total_expected_samples = n_stations * base_samples_per_station
n_species = min(300, max(10, int(total_expected_samples * random.uniform(0.5, 2.0))))

print(f"Generating dataset with:")
print(f"- {n_stations} stations")
print(f"- ~{base_samples_per_station} samples per station")
print(f"- {n_species} species")

# Determine padding lengths based on maximum values
station_pad = len(str(n_stations))
day_pad = len(str(base_samples_per_station))
species_pad = len(str(n_species))

# Generate sample IDs with random "losses"
samples = []
start_date = datetime(2023, 1, 1)
for station in range(1, n_stations + 1):
    # Random number of "lost" samples for this station
    lost_samples = random.randint(0, min(5, base_samples_per_station - 5))
    n_samples = base_samples_per_station - lost_samples
    
    # Generate samples for this station
    station_samples = []
    current_date = start_date
    for day in range(n_samples):
        sample_id = f"Station{str(station).zfill(station_pad)}_Day{str(day+1).zfill(day_pad)}"
        samples.append({
            'SampleID': sample_id,
            'Station': f"Station{str(station).zfill(station_pad)}",
            'SamplingTime': current_date.strftime('%Y-%m-%d'),
            'Latitude': 46.8182 + (station-1)*0.001 + random.uniform(-0.0002, 0.0002),
            'Longitude': 8.2275 + (station-1)*0.001 + random.uniform(-0.0002, 0.0002)
        })
        current_date += timedelta(days=random.randint(1, 3))

# Convert to DataFrame for metadata
metadata_df = pd.DataFrame(samples)
metadata_df.to_csv("metadata.txt", sep="\t", index=False)

# Generate species IDs with padding
species_ids = [f"OTU{str(i+1).zfill(species_pad)}" for i in range(n_species)]

# Generate OTU table with realistic abundance patterns
otu_abundances = {}
for otu in species_ids:
    # Some species are rare, some are common
    if random.random() < 0.2:  # 20% chance of being a common species
        abundance_profile = [random.randint(50, 1000) for _ in range(len(samples))]
    elif random.random() < 0.5:  # 30% chance of being moderately common
        abundance_profile = [random.randint(10, 100) for _ in range(len(samples))]
    else:  # 50% chance of being rare
        abundance_profile = [random.randint(0, 10) for _ in range(len(samples))]
        # Add more zeros for rare species
        for i in range(len(abundance_profile)):
            if random.random() < 0.7:  # 70% chance of zero for rare species
                abundance_profile[i] = 0
    otu_abundances[otu] = abundance_profile

# Create OTU table
otu_table = pd.DataFrame(otu_abundances, index=[s['SampleID'] for s in samples])
otu_table.to_csv("otu_table.txt", sep="\t")

# Generate sequences
with open("sequences.fasta", "w") as f:
    for species_id in species_ids:
        f.write(f">{species_id}\n")
        # Generate slightly different sequences for each species
        base_seq = "CGTAGGTGAACCTGCGGAAGGATCATTGTTGAGAAACTCAAACCTTTTGTTGATGGTCTTGGC"
        mutated_seq = ''.join(random.choice(['A', 'T', 'G', 'C']) if random.random() < 0.1 else c 
                             for c in base_seq)
        f.write(f"{mutated_seq}\n")

# Generate taxonomy table with more diverse classifications
families = ['Asteraceae', 'Poaceae', 'Fabaceae', 'Rosaceae', 'Brassicaceae']
orders = ['Asterales', 'Poales', 'Fabales', 'Rosales', 'Brassicales']
classes = ['Magnoliopsida', 'Liliopsida']
phyla = ['Tracheophyta', 'Bryophyta']

# Generate genus and species names with padding
genera = [f"Genus{str(i+1).zfill(species_pad)}" for i in range(n_species)]
species_names = [f"Species{str(i+1).zfill(species_pad)}" for i in range(n_species)]

tax_table = pd.DataFrame({
    "OTU": species_ids,
    "Kingdom": ["Plantae"] * n_species,
    "Phylum": [random.choice(phyla) for _ in range(n_species)],
    "Class": [random.choice(classes) for _ in range(n_species)],
    "Order": [random.choice(orders) for _ in range(n_species)],
    "Family": [random.choice(families) for _ in range(n_species)],
    "Genus": genera,
    "Species": species_names
})
tax_table.to_csv("tax_table.txt", sep="\t", index=False)

# Calculate number of species in each category based on total species count
n_vulnerable = max(1, int(n_species * 0.05))  # 5% vulnerable
n_endangered = max(1, int(n_species * 0.03))  # 3% endangered
n_critical = max(1, int(n_species * 0.02))    # 2% critically endangered
n_invasive = max(1, int(n_species * 0.04))    # 4% invasive
n_non_native = max(1, int(n_species * 0.1))   # 10% non-native

# Create status lists
red_list_statuses = ['LC'] * (n_species - n_vulnerable - n_endangered - n_critical)
red_list_statuses.extend(['VU'] * n_vulnerable)
red_list_statuses.extend(['EN'] * n_endangered)
red_list_statuses.extend(['CR'] * n_critical)
random.shuffle(red_list_statuses)

invasion_statuses = ['Non-invasive'] * (n_species - n_invasive)
invasion_statuses.extend(['Invasive'] * n_invasive)
random.shuffle(invasion_statuses)

native_statuses = ['Native'] * (n_species - n_non_native)
native_statuses.extend(['Non-native'] * n_non_native)
random.shuffle(native_statuses)

taxa_metadata = pd.DataFrame({
    "Species": species_names,  # Using padded species names
    "RedListStatus": red_list_statuses,
    "InvasionStatus": invasion_statuses,
    "NativeStatus": native_statuses
})
taxa_metadata.to_csv("taxa_metadata.txt", sep="\t", index=False)

print("\nGenerated files:")
print("- metadata.txt")
print("- otu_table.txt")
print("- sequences.fasta")
print("- tax_table.txt")
print("- taxa_metadata.txt")
print(f"\nActual samples generated: {len(samples)}")
print(f"Species with endangered status: {len([s for s in red_list_statuses if s != 'LC'])}")
print(f"Invasive species: {len([s for s in invasion_statuses if s == 'Invasive'])}")