import os
import re
import pandas as pd

def runDockQ(pdb_fn_ref):
    pdb_fn, ref_fn, index, total_files = pdb_fn_ref
    best_dockq = None
    try:
        allowed_mismatches = 20
        cmd = f"DockQ {pdb_fn} {ref_fn} --short --allowed_mismatches {allowed_mismatches}"
        lines = os.popen(cmd).readlines()

        if len(lines) == 0:
            print(f"Processing file {index + 1} of {total_files}: {pdb_fn} - Result: {best_dockq}")
            return (pdb_fn, ref_fn, None)

        for line in lines:
            if line.startswith('DockQ'):
                parts = line.split()
                dockq_score = float(parts[1])  # DockQ 점수
                if best_dockq is None or dockq_score > best_dockq:
                    best_dockq = dockq_score  # 가장 높은 DockQ 점수 업데이트

    except IndexError as e:
        print(f"IndexError while processing {pdb_fn}: {e}")
        return (pdb_fn, ref_fn, None)  # IndexError 발생 시 결과를 None으로 반환
    except Exception as e:
        print(f"Error while processing {pdb_fn}: {e}")
        return (pdb_fn, ref_fn, None)

    print(f"Processing file {index + 1} of {total_files}: {pdb_fn} - Result: {best_dockq}")
    return (pdb_fn, ref_fn, best_dockq)  # 가장 높은 DockQ 점수 반환


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
            # 'decoy'가 포함된 .pdb 파일만 선택
            pdb_files = [f for f in os.listdir(subdir_path) if f.endswith('.pdb') and 'decoy' in f]
            print(pdb_files)
            
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
        
        # 원본 PDB 파일 경로 생성
        for_dockq_dir = os.path.join(input_dir, 'for_dockq')
        
        # 정수 값을 모두 제거하여 원본 PDB 이름 생성
        native_pdb_name = re.sub(r'_\d+_', '_', subdir) + ".pdb"
        native_pdb_path = os.path.join(for_dockq_dir, native_pdb_name)

        if not os.path.isfile(native_pdb_path):
            print(f"Native PDB file {native_pdb_name} not found in {for_dockq_dir}")
            failed_dirs.append(subdir)  # 실패한 서브 디렉토리 기록
            continue
        
        # PDB 파일과 원본 PDB 파일 경로 쌍 생성
        pdb_ref_pairs = []
        for index, pdb_file in enumerate(pdb_files):
            pdb_file_path = os.path.join(subdir_path, pdb_file)
            pdb_ref_pairs.append((pdb_file_path, native_pdb_path, index, total_files))
        
        # 순차적으로 DockQ 계산
        results = []
        for pdb_ref_pair in pdb_ref_pairs:
            result = runDockQ(pdb_ref_pair)
            results.append(result)

        # 서브 디렉토리의 결과를 DataFrame으로 변환
        df = pd.DataFrame(results, columns=['DockQ_PDB', 'Native_PDB', 'best_dockQ'])
        
        # DockQ 점수에 따라 정렬
        df = df.sort_values(by='best_dockQ', ascending=False)
        
        # 각 서브 디렉토리에 결과를 CSV 파일로 저장
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


# 실행부
if __name__ == "__main__":
    output_dir = 'MEGADOCK_output'
    input_dir = 'MEGADOCK_input'
    process_subdirectories(output_dir, input_dir)
