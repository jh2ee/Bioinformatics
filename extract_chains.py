# import os
# import subprocess

# def extract_chain(pdb_file_path, chains, output_path):
#     # PDB 파일의 기본 이름 추출
#     base_name = os.path.basename(pdb_file_path).split(".")[0]

#     # 출력 파일 경로 설정 (모든 체인을 포함하는 하나의 파일)
#     output_pdb_file = os.path.join(output_path, f'{base_name}_{chains}.pdb')

#     # 파일이 이미 존재하는지 확인
#     if os.path.exists(output_pdb_file):
#         print(f"File {output_pdb_file} already exists. Skipping chain extraction.")
#         return output_pdb_file  # 파일 경로만 반환

#     # 각 체인을 순차적으로 처리하여 파일에 기록
#     with open(output_pdb_file, 'w') as out_file:
#         for chain in chains:  # 각 체인(A, B 등)을 처리
#             command = ['pdb_selchain', f'-{chain}', pdb_file_path]
#             # subprocess를 실행하여 해당 체인을 추출하고, 결과를 파일에 추가
#             subprocess.run(command, stdout=out_file, check=True)
    
#     print(f"Extracted chains {chains} into {output_pdb_file}")
#     # 최종적으로 생성된 파일 경로 반환

#     temp_pdb_path = os.path.join(os.path.dirname(output_pdb_file), 'temp_fixed.pdb')

#     # 'pdb_fixinsert'와 'pdb_tidy'를 사용하여 PDB 파일을 정리
#     subprocess.run(f'pdb_fixinsert {output_pdb_file} > {temp_pdb_path}', shell=True, check=True)
#     subprocess.run(f'pdb_tidy {temp_pdb_path} > {output_pdb_file}', shell=True, check=True)

#     return output_pdb_file

# # extract_chain('./mnt/PDD_input/5epp.pdb', 'BA', './mnt/PDD_input')


# def process_text_file(file_path, pdb_input_dir, output_dir):
#     """
#     텍스트 파일을 읽고 각 라인의 PDB ID와 체인을 추출하여 `extract_chain` 함수를 실행.

#     Args:
#     - file_path: 입력 텍스트 파일 경로
#     - pdb_input_dir: PDB 파일이 저장된 디렉토리 경로
#     - output_dir: 결과 PDB 파일을 저장할 디렉토리 경로
#     """
#     with open(file_path, 'r') as file:
#         for line in file:
#             # 탭으로 구분된 첫 번째 항목에서 PDB ID와 체인 추출
#             pdb_chain_info = line.split()[0]
#             pdb_id, chains = pdb_chain_info.split('_')
            
#             # 체인 정보에서 ':' 제거
#             chains = chains.replace(':', '')

#             # PDB 파일 경로 생성
#             pdb_file_path = os.path.join(pdb_input_dir, f'{pdb_id}.pdb')

#             # extract_chain 함수를 호출하여 PDB 파일에서 체인 추출 및 수정
#             extract_chain(pdb_file_path, chains, output_dir)


import os
import subprocess
import requests

def download_pdb(pdb_id, download_path):
    """
    PDB ID에 해당하는 파일을 다운로드합니다. 파일이 이미 존재하면 다운로드를 건너뜁니다.

    Args:
    - pdb_id: 다운로드할 PDB ID
    - download_path: PDB 파일을 저장할 디렉토리 경로

    Returns:
    - pdb_file_path: 다운로드한 PDB 파일 경로
    """
    # 다운로드할 PDB 파일 경로
    pdb_file_path = os.path.join(download_path, f'{pdb_id}.pdb')

    # 파일이 이미 존재하는지 확인
    if os.path.exists(pdb_file_path):
        print(f"File {pdb_file_path} already exists. Skipping download.")
        return pdb_file_path  # 파일 경로만 반환

    # PDB 파일 다운로드
    url = f'https://files.rcsb.org/download/{pdb_id}.pdb'
    response = requests.get(url)
    if response.status_code == 200:
        with open(pdb_file_path, 'w') as file:
            file.write(response.text)
        print(f"Downloaded {pdb_file_path}")
        return pdb_file_path
    else:
        raise Exception(f"Failed to download PDB file: {pdb_id}")

def extract_chain(pdb_file_path, chains, output_path):
    """
    PDB 파일에서 특정 체인들을 추출하고, 파일을 정리합니다.

    Args:
    - pdb_file_path: 입력 PDB 파일 경로
    - chains: 추출할 체인 리스트
    - output_path: 결과 PDB 파일을 저장할 경로

    Returns:
    - output_pdb_file: 처리된 PDB 파일 경로
    """
    base_name = os.path.basename(pdb_file_path).split(".")[0]
    output_pdb_file = os.path.join(output_path, f'{base_name}_{chains}.pdb')

    if os.path.exists(output_pdb_file):
        print(f"File {output_pdb_file} already exists. Skipping chain extraction.")
        return output_pdb_file  # 파일 경로만 반환

    with open(output_pdb_file, 'w') as out_file:
        for chain in chains:
            command = ['pdb_selchain', f'-{chain}', pdb_file_path]
            subprocess.run(command, stdout=out_file, check=True)

    print(f"Extracted chains {chains} into {output_pdb_file}")
    
    temp_pdb_path = os.path.join(os.path.dirname(output_pdb_file), 'temp_fixed.pdb')

    subprocess.run(f'pdb_fixinsert {output_pdb_file} > {temp_pdb_path}', shell=True, check=True)
    subprocess.run(f'pdb_tidy {temp_pdb_path} > {output_pdb_file}', shell=True, check=True)

    return output_pdb_file

def process_text_file(file_path, pdb_input_dir, output_dir):
    """
    텍스트 파일을 읽고 각 라인의 PDB ID와 체인을 추출하여 PDB 파일을 다운로드하고, 체인 추출 작업을 진행합니다.

    Args:
    - file_path: 입력 텍스트 파일 경로
    - pdb_input_dir: PDB 파일이 저장된 디렉토리 경로
    - output_dir: 결과 PDB 파일을 저장할 디렉토리 경로
    """
    with open(file_path, 'r') as file:
        for line in file:
            # 탭으로 구분된 첫 번째 항목에서 PDB ID와 체인 추출
            pdb_chain_info = line.split()[0]
            pdb_id, chains = pdb_chain_info.split('_')
            
            # 체인 정보에서 ':' 제거
            chains = chains.replace(':', '')

            # PDB 파일이 없으면 다운로드
            pdb_file_path = download_pdb(pdb_id, pdb_input_dir)

            # PDB 파일에서 체인 추출 및 수정
            extract_chain(pdb_file_path, chains, output_dir)

process_text_file('./peppro-exsitunbound_seq_len_le15.list', './mnt/PDD_input', './mnt/PDD_input')
