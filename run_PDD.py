import os
import argparse
import subprocess
import requests

# 다운로드 함수
def download_pdb(pdb_id, download_path):
    # 다운로드할 PDB 파일 경로 설정
    pdb_file_path = os.path.join(download_path, f'{pdb_id}.pdb')

    # 파일이 이미 존재하는지 확인
    if os.path.exists(pdb_file_path):
        print(f"File {pdb_file_path} already exists. Skipping download.")
        return pdb_file_path  # 파일 경로만 반환

    # 파일이 없을 경우 다운로드 진행
    url = f'https://files.rcsb.org/download/{pdb_id}.pdb'
    response = requests.get(url)
    if response.status_code == 200:
        with open(pdb_file_path, 'w') as file:
            file.write(response.text)
        print(f"Downloaded {pdb_file_path}")
        return pdb_file_path
    else:
        raise Exception(f"Failed to download PDB file: {pdb_id}")

# 체인 추출 함수
def extract_chain(pdb_file_path, chains, output_path):
    # PDB 파일의 기본 이름 추출
    base_name = os.path.basename(pdb_file_path).split(".")[0]

    # 출력 파일 경로 설정 (모든 체인을 포함하는 하나의 파일)
    output_pdb_file = os.path.join(output_path, f'{base_name}_{chains}.pdb')

    # 파일이 이미 존재하는지 확인
    if os.path.exists(output_pdb_file):
        print(f"File {output_pdb_file} already exists. Skipping chain extraction.")
        return output_pdb_file  # 파일 경로만 반환

    # 각 체인을 순차적으로 처리하여 파일에 기록
    with open(output_pdb_file, 'w') as out_file:
        for chain in chains:  # 각 체인(A, B 등)을 처리
            command = ['pdb_selchain', f'-{chain}', pdb_file_path]
            # subprocess를 실행하여 해당 체인을 추출하고, 결과를 파일에 추가
            subprocess.run(command, stdout=out_file, check=True)
    
    print(f"Extracted chains {chains} into {output_pdb_file}")
    # 최종적으로 생성된 파일 경로 반환
    return output_pdb_file


def parse_input_file(input_file_path):
    data = []
    with open(input_file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            pdb_chain = parts[1].split('_')
            pdb_id = pdb_chain[0].lower()
            chain = pdb_chain[1]
            sequence = parts[3]
            data.append((pdb_id, chain, sequence))
    return data

def main():
    parser = argparse.ArgumentParser(description="Process PDB files and run PepDockDove")
    parser.add_argument('-i', '--input', required=True, help="Input text file path")
    parser.add_argument('-d', '--download', required=True, help="PDB download directory")
    parser.add_argument('-o', '--output', required=True, help="Output directory for processed PDBs and results")
    args = parser.parse_args()

    # os.makedirs(args.download, exist_ok=True)
    os.makedirs(args.output, exist_ok=True)

    data = parse_input_file(args.input)

    for pdb_id, chain, sequence in data:
        try:
            print(f"Processing PDB ID: {pdb_id}, Chain: {chain}, Sequence: {sequence}")
            pdb_file_path = download_pdb(pdb_id, args.download)
            extracted_chain_pdb = extract_chain(pdb_file_path, chain, args.output)
            output_file = os.path.join(args.output, f"{pdb_id}_{chain}_pep_pro_output")
            subprocess.run(['python', 'pepdockdove.py', '-s', sequence, '-r', extracted_chain_pdb, '-o', output_file], check=True)
        except Exception as e:
            print(f"An error occurred while processing {pdb_id}_{chain}: {str(e)}")

if __name__ == "__main__":
    main()
