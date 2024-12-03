import os
import csv
from Bio.PDB import PDBParser, NeighborSearch

def find_contacts(pdb_file, chainA, chainB, distance_cutoff=5.0):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(os.path.basename(pdb_file), pdb_file)
    chain_a_residues = []
    chain_b_atoms = []

    for model in structure:
        for chain in model:
            if chain.id == chainA:
                chain_a_residues.extend(list(chain))
            elif chain.id == chainB:
                chain_b_atoms.extend([atom for residue in chain for atom in residue])

    # Create a NeighborSearch object for chain B atoms
    neighbor_search = NeighborSearch(chain_b_atoms)

    contacts = set()
    # Check if any residue in chain A has atoms within the distance_cutoff from any atom in chain B
    for residue in chain_a_residues:
        if any(neighbor_search.search(atom.coord, distance_cutoff, level='R') for atom in residue):
            contacts.add(residue.get_id())

    return sorted(contacts)

def process_pdb_files(directory, chainA, chainB, distance_cutoff=5.0, output_csv='binding_sites.csv'):
    # List only .pdb files in the directory
    pdb_files = [f for f in os.listdir(directory) if f.endswith('.pdb')]
    results = []

    for pdb_file in pdb_files:
        pdb_path = os.path.join(directory, pdb_file)
        contacts = find_contacts(pdb_path, chainA, chainB, distance_cutoff)
        results.append([pdb_file, ' '.join(map(str, contacts))])

    # Write results to CSV
    with open(output_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['PDB File', 'Binding Site Residues'])
        csvwriter.writerows(results)

# Example usage
chainA = 'A'  # Change to your chain identifier for antigen
chainB = 'H'  # Change to your chain identifier for antibody
distance_cutoff = 5.0  # Distance cutoff in angstroms

# Loop through different directories
for n in [16, 49, 51]:
    for i in range(1, 6):
        directory = f'Nb{n}_{i}-HER2-CDR-NMR-CSP-full/3_emref/'
        output_csv = f'binding_sites_Nb{n}_{i}.csv'
        process_pdb_files(directory, chainA, chainB, distance_cutoff, output_csv)
