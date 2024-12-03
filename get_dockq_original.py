import os
import subprocess
import argparse
import requests

def download_pdb(pdb_id, output_dir):
    url = f'https://files.rcsb.org/download/{pdb_id}.pdb'
    response = requests.get(url)
    if response.status_code == 200:
        output_path = os.path.join(output_dir, f'{pdb_id}.pdb')
        with open(output_path, 'w') as file:
            file.write(response.text)
        print(f'Downloaded PDB file: {pdb_id}.pdb')
        return output_path
    else:
        print(f"Error: Could not download PDB file for {pdb_id}.")
        return None

def extract_chain_with_pdbtools(pdb_file, output_pdb_file, chain_ids):
    chains_str = ','.join(chain_ids)
    cmd = f"pdb_selchain -{chains_str} {pdb_file} > {output_pdb_file}"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f'Successfully created {output_pdb_file}')
    except subprocess.CalledProcessError as e:
        print(f"Error during pdb-tools execution: {e}")

def process_file(input_filename, output_dir):
    # 디렉토리 구조 생성
    original_pdb_dir = os.path.join(output_dir, 'original_PDB')
    for_dockq_dir = os.path.join(output_dir, 'for_dockq')
    os.makedirs(original_pdb_dir, exist_ok=True)
    os.makedirs(for_dockq_dir, exist_ok=True)
    
    # 입력 파일 처리
    with open(input_filename, 'r') as file:
        lines = file.readlines()
    
    for line in lines:
        columns = line.split()
        pdb_id = columns[0]
        chain_ids = columns[1:3]  # 2번째와 3번째 열에서 체인 ID 가져오기

        # PDB 파일 경로 설정
        pdb_file = os.path.join(original_pdb_dir, f'{pdb_id}.pdb')
        
        # PDB 파일이 없으면 다운로드
        if not os.path.exists(pdb_file):
            pdb_file = download_pdb(pdb_id, original_pdb_dir)
            if pdb_file is None:
                continue  # 다운로드 실패 시 다음 PDB로 넘어감

        # 두 체인을 포함한 PDB 파일 생성
        output_pdb_file = os.path.join(for_dockq_dir, f'{pdb_id}_{chain_ids[0]}_{chain_ids[1]}.pdb')

        # pdb-tools를 사용하여 체인 추출 및 새로운 PDB 파일 생성
        extract_chain_with_pdbtools(pdb_file, output_pdb_file, chain_ids)

def main():
    parser = argparse.ArgumentParser(
        description="Extract chains from PDB files and create a merged PDB file for docking.",
        usage="%(prog)s -l [list_txt_file] -o [output_dir]"
    )
    parser.add_argument('-l', '--list', required=True, help="Path to the list of PDB IDs and chain IDs.")
    parser.add_argument('-o', '--output', required=True, help="Directory to save the output files.")
    
    args = parser.parse_args()
    
    process_file(args.list, args.output)

if __name__ == "__main__":
    main()
