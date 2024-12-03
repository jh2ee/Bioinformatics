import os
import subprocess

def run_calcrmsds(pdb_id, ref_pdb, sequence, mapping):
    """
    calcrmsds.py 스크립트를 자동으로 실행하는 함수
    Args:
    - pdb_id: PDB ID
    - ref_pdb: 참조 PDB 경로
    - sequence: 서열 정보
    """
    complex_dir = f"./mnt/PDD_output/{pdb_id}_pep_pro_output/decoys/{sequence}_2"
    ref_pdb_path = f"./mnt/PDD_input/{ref_pdb}.pdb"
    output = f"./rnk_full_rmsds.ver2/{pdb_id}.txt"
    predict_sort = f"./mnt/PDD_output/{pdb_id}_pep_pro_output/decoys/{sequence}_2/Predict_Result/Multi_Target/Fold_1_Result/{sequence}_2/Predict_sort.txt"

    cmd = [
        'python', 'calcrmsds.py',
        '--complex_dir', complex_dir,
        '--ref_pdb', ref_pdb_path,
        '--output', output,
        '--predict_sort', predict_sort,
        '--mapping', mapping
    ]

    # subprocess로 커맨드 실행
    try:
        subprocess.run(cmd, check=True)
        print(f"Command executed successfully for {pdb_id}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command for {pdb_id}: {e}")


def process_text_file(file_path):
    """
    텍스트 파일을 읽고 각 라인의 값을 이용해 run_calcrmsds 함수를 실행
    Args:
    - file_path: 텍스트 파일 경로
    """
    with open(file_path, 'r') as file:
        for line in file:
            # 각 열의 값을 분리하여 변수에 저장
            parts = line.strip().split()
            if len(parts) < 4:
                continue

            ref_pdb = parts[0].replace(':', '')  # 1열 값에서 ':' 제거
            ref_map = ref_pdb.split('_')[1] # ex) 1dkd_EA -> EA

            pdb_id = parts[1]  # 2열 값
            pdb_map = pdb_id.split('_')[1] + 'X' # ex) 1kid_A -> AX

            sequence = parts[3]  # 4열 값
            mapping = ref_map + ':' + pdb_map

            # run_calcrmsds 함수 호출
            run_calcrmsds(pdb_id, ref_pdb, sequence, mapping)


if __name__ == "__main__":
    # 텍스트 파일 경로
    text_file_path = 'peppro-exsitunbound_seq_len_le15.list' 

    # 텍스트 파일 처리
    process_text_file(text_file_path)
