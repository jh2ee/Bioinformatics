import os
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# input: peptide sequence & receptor pdb
# get inputs by parser

def pepflow(sequence, num_models, output_dir):
    command = f'python ./pepflow/generate_peptide_samples.py -s {sequence} -o {output_dir}/models --e -fm ./pepflow/params/full_model.pth -n {num_models} -c 10'
    os.makedirs(f'{output_dir}/models', exist_ok=True)
    subprocess.run(command, shell=True, check=True)
    deconformation(sequence, output_dir)


# deconformate the pepflow's output
def deconformation(sequence, output_dir):
    pdb_path = f'{output_dir}/models/{sequence}.pdb'
    with open(pdb_path, 'r') as f:
        model_num = 0
        out_file = None

        for line in f:
            if line.startswith('MODEL'):
                model_num += 1
                if out_file:
                    out_file.close()
                output_file_path = os.path.join(output_dir, 'models', f'{sequence}_{model_num}.pdb')
                out_file = open(output_file_path, 'w')
            elif line.startswith('ENDMDL'):
                if out_file:
                    out_file.write(line)
                    out_file.close()
                    out_file = None
            if out_file:
                out_file.write(line)

        if out_file:
            out_file.close()


# docking & generate decoy
def megadock(sequence, receptor_path, num_decoys, output_dir, idx):
    ligand_path = f'{output_dir}/models/{sequence}_{idx}.pdb'
    out_file_path = f'{output_dir}/decoys/{sequence}_{idx}/{sequence}_{idx}.out'
    os.makedirs(f'{output_dir}/decoys/{sequence}_{idx}', exist_ok=True)
    os.makedirs(f'{output_dir}/decoys/{sequence}_{idx}/ligands', exist_ok=True)

    megadock_command = f'./MEGADOCK/megadock -R {receptor_path} -L {ligand_path} -o {out_file_path}'
    subprocess.run(megadock_command, shell=True, check=True)

    for i in range(1, num_decoys+1):
        idx_ligand_path = f'{output_dir}/decoys/{sequence}_{idx}/ligands/{sequence}_{idx}.{i}.pdb'
        decoy_path = f'{output_dir}/decoys/{sequence}_{idx}/{sequence}_{idx}.decoy_{i}.pdb'

        decoy_gen_command1 = f'./MEGADOCK/decoygen {idx_ligand_path} {ligand_path} {out_file_path} {i}'
        decoy_gen_command2 = f'cat {receptor_path} {idx_ligand_path} > {decoy_path}'
        subprocess.run(decoy_gen_command1, shell=True, check=True)
        subprocess.run(decoy_gen_command2, shell=True, check=True)


# multiprocessing을 위해 megadock 함수를 사용할 수 있도록 설정
def megadock_worker(args):
    sequence, receptor_path, num_decoys, output_dir, idx = args
    megadock(sequence, receptor_path, num_decoys, output_dir, idx)


def gnn_dove(sequence, num_models, num_decoys, output_dir, idx):
    subdir_path = f'{output_dir}/decoys/{sequence}_{idx}'

    dove_command = f'python ./GNN_DOVE/main.py --mode=1 -F {subdir_path} --gpu=0 --fold=1'
    subprocess.run(dove_command, shell=True, check=True)



def process(sequence, receptor_path, num_models, num_decoys, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    # pepflow(sequence, num_models, output_dir)

    # 순차 실행 코드
    # for idx in range(1, num_models+1):
        # megadock(sequence, receptor_path, num_decoys, output_dir, idx)
        # gnn_dove(sequence, num_models, num_decoys, output_dir, idx)
    gnn_dove(sequence, num_models, num_decoys, output_dir, 1)
        
    # ThreadPoolExecutor를 사용해 스레드 제한 (예: 10개의 스레드로 제한)
    # max_threads = 10
    # pool_args = [(sequence, receptor_path, num_decoys, output_dir, idx) for idx in range(1, num_models + 1)]
    
    # ThreadPoolExecutor를 사용해 각 모델에 대해 병렬로 megadock 실행
    # with ThreadPoolExecutor(max_threads) as executor:
    #     futures = [executor.submit(megadock_worker, args) for args in pool_args]
        
    #     # 각 작업이 완료될 때까지 기다림
    #     for future in as_completed(futures):
    #         try:
    #             future.result()  # 작업 결과 확인
    #         except Exception as exc:
    #             print(f"Error in thread execution: {exc}")


def main():
    parser = argparse.ArgumentParser(
        description="Predict the structure of the peptide and docking",
        usage="%(prog)s -s [peptide_sequence] -r [receptor_path] -m [num_models] -d [num_decoys] -o [output_dir]"
    )

    parser.add_argument('-s', '--sequence', required=True, help="Peptide Sequence")
    parser.add_argument('-r', '--receptor', required=True, help="Path of the Receptor PDB file")
    parser.add_argument('-m', '--models', required=False, type=int, default=1, help="Number of Models (# of PepFlow outputs)")
    parser.add_argument('-d', '--decoys', required=False, type=int, default=1000, help="Number of Decoys (# of Megadock outputs)")
    parser.add_argument('-o', '--output', required=False, default='PMD_output', help="Directory to save the output files.")
    
    args = parser.parse_args()
    process(args.sequence, args.receptor, args.models, args.decoys, args.output)


if __name__ == "__main__":
    main()
