import os
import re
import pandas as pd
from multiprocessing import Pool, cpu_count


def runDockQ(pdb_fn_ref):
    pdb_fn, ref_fn, chain_A, chain_B, index, total_files = pdb_fn_ref
    total_dockq = None
    try:
        allowed_mismatches = 20
        # DockQ 명령에 체인 매핑 추가
        cmd = f"DockQ {pdb_fn} {ref_fn} --short --allowed_mismatches {allowed_mismatches} --mapping {chain_A}{chain_B}:{chain_A}{chain_B}"
        lines = os.popen(cmd).readlines()

        for line in lines:
            if line.startswith('Total DockQ'):
                parts = line.split()
                total_dockq = float(parts[6])  # Total DockQ score
                break  # 점수를 찾았으면 반복을 종료

        if total_dockq is None:
            print(f"Total DockQ not found for {pdb_fn}, returning None")
            return (pdb_fn, ref_fn, None)
    
    except IndexError as e:
        print(f"IndexError while processing {pdb_fn}: {e}")
        return (pdb_fn, ref_fn, None)  # IndexError Handle
    except Exception as e:
        print(f"Error while processing {pdb_fn}: {e}")
        return (pdb_fn, ref_fn, None)

    print(f"Processing file {index + 1} of {total_files}: {pdb_fn} - Result: {total_dockq}")
    return (pdb_fn, ref_fn, total_dockq)

def process_subdirectories(output_dir, input_dir):
    failed_dirs = []  # DockQ 실행 실패한 서브 디렉토리를 저장할 리스트

    try:
        subdirs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
    except Exception as e:
        print(f"Error accessing subdirectories in {output_dir}: {e}")
        return

    for subdir in subdirs:
        subdir_path = os.path.join(output_dir, subdir)

        try:
            # decoy가 포함된 pdb 파일만 선택
            pdb_files = [f for f in os.listdir(subdir_path) if f.endswith('.pdb') and 'decoy' in f]
            if not pdb_files:
                print(f"No 'decoy' PDB files found in {subdir_path}")
                failed_dirs.append(subdir)  # 실패한 서브 디렉토리 기록
                continue

        except Exception as e:
            print(f"Error accessing PDB files in {subdir_path}: {e}")
            failed_dirs.append(subdir)  # 실패한 서브 디렉토리 기록
            continue

        total_files = len(pdb_files)
        if total_files == 0:
            print(f"No 'decoy' PDB files found in {subdir_path}")
            failed_dirs.append(subdir)  # 실패한 서브 디렉토리 기록
            continue

        # PDB 이름 추출: 서브디렉토리 이름의 앞 4글자를 사용
        pdb_id = subdir[:4]
        original_pdb_path = os.path.join(input_dir, 'original_PDB', f"{pdb_id}.pdb")

        if not os.path.isfile(original_pdb_path):
            print(f"Original PDB file {original_pdb_path} not found")
            failed_dirs.append(subdir)  # 실패한 서브 디렉토리 기록
            continue

        # 서브디렉토리 이름에서 체인 정보를 추출 (_로 분할)
        try:
            _, chain_A, _, chain_B = subdir.split('_')
        except ValueError:
            print(f"Error extracting chains from {subdir}")
            failed_dirs.append(subdir)  # 실패한 서브 디렉토리 기록
            continue

        pdb_ref_pairs = []
        for index, pdb_file in enumerate(pdb_files):
            pdb_file_path = os.path.join(subdir_path, pdb_file)
            pdb_ref_pairs.append((pdb_file_path, original_pdb_path, chain_A, chain_B, index, total_files))

        results = []
        # 멀티프로세싱을 이용해 DockQ 계산
        try:
            num_processes = max(1, cpu_count() // 2)
            with Pool(num_processes) as pool:
                results = pool.map(runDockQ, pdb_ref_pairs)

        except Exception as e:
            print(f"Error processing DockQ for {subdir}: {e}")
            failed_dirs.append(subdir)  # 실패한 서브 디렉토리 기록
            continue

        # 서브 디렉토리의 결과를 DataFrame으로 변환
        df = pd.DataFrame(results, columns=['DockQ_PDB', 'Native_PDB', 'best_dockQ'])
        df = df.sort_values(by='best_dockQ', ascending=False)  # DockQ 점수에 따라 정렬

        # 결과를 CSV 파일로 저장
        output_csv = os.path.join(subdir_path, 'dockQ_results_sorted.csv')
        try:
            df.to_csv(output_csv, index=False)
            print(f"DockQ results for {subdir} have been saved and sorted in {output_csv}")
        except Exception as e:
            print(f"Error while saving CSV file for {subdir}: {e}")
            failed_dirs.append(subdir)  # 실패한 서브 디렉토리 기록

    # 실패한 서브 디렉토리 정보를 로그 파일로 저장
    if failed_dirs:
        log_file_path = os.path.join(output_dir, 'dockq_failed_dirs.log')
        try:
            with open(log_file_path, 'w') as log_file:
                for failed_dir in failed_dirs:
                    log_file.write(f"{failed_dir}\n")
            print(f"Failed directories have been logged in {log_file_path}")
        except Exception as e:
            print(f"Error while writing log file: {e}")


if __name__ == "__main__":
    output_dir = 'MEGADOCK_output'
    input_dir = 'MEGADOCK_input'
    os.environ["OMP_NUM_THREADS"] = '10'
    os.environ['TMPDIR'] = '/workspace/tmp'
    process_subdirectories(output_dir, input_dir)
