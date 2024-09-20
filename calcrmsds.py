import os
import subprocess
from optparse import OptionParser

# DockQ를 실행해 lrmsd, irmsd, fnat 값을 반환하는 함수
# def runDockQ(pdb_fn, ref_fn):
#     lrmsd, irmsd, fnat = 9999, 9999, 0
#     cmd = f'DockQ --short --allowed_mismatches 20 {pdb_fn} {ref_fn}'
#     result = os.popen(cmd).readlines()
    
#     for line in result:
#         if line.startswith('iRMS'):
#             irmsd = float(line.split()[1])
#         elif line.startswith('LRMS'):
#             lrmsd = float(line.split()[1])
#         elif line.startswith('Fnat'):
#             fnat = float(line.split()[1])
    
#     return lrmsd, irmsd, fnat
# def runDockQ(pdb_fn, ref_fn, log_file='./rmsds/log.log'):
#     lrmsd, irmsd, fnat = 9999, 9999, 0
#     cmd = f'DockQ --allowed_mismatches 20 {pdb_fn} {ref_fn}'
    
#     # 로그를 저장할 파일을 연다
#     with open(log_file, 'w') as log:
#         # subprocess를 이용해 명령어를 실행하고, stdout과 stderr를 로그 파일에 기록
#         result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
#         # 명령 실행 결과를 로그 파일에 기록
#         log.write(result.stdout)

#         # 결과를 다시 라인별로 나누어 처리
#         for line in result.stdout.splitlines():
#             if line.startswith('iRMS'):
#                 irmsd = float(line.split()[1])
#             elif line.startswith('LRMS'):
#                 lrmsd = float(line.split()[1])
#             elif line.startswith('Fnat'):
#                 fnat = float(line.split()[1])
    
#     return lrmsd, irmsd, fnat

def runDockQ(pdb_fn, ref_fn, log_file='./rmsds/log.log'):
    lrmsd, irmsd, fnat, dockq = 9999, 9999, 0, 0
    cmd = f'DockQ --allowed_mismatches 20 {pdb_fn} {ref_fn}'
    
    # 로그를 저장할 파일을 연다
    with open(log_file, 'w') as log:
        # subprocess를 이용해 명령어를 실행하고, stdout과 stderr를 로그 파일에 기록
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # 명령 실행 결과를 로그 파일에 기록
        log.write(result.stdout)

        # 결과를 다시 라인별로 나누어 처리
        for line in result.stdout.splitlines():
            # iRMSD 추출
            if 'iRMSD' in line:
                try:
                    irmsd = float(line.split()[1])
                except (ValueError, IndexError):
                    print(f"Error parsing iRMSD from line: {line}")
            
            # LRMSD 추출
            elif 'LRMSD' in line:
                try:
                    lrmsd = float(line.split()[1])
                except (ValueError, IndexError):
                    print(f"Error parsing LRMSD from line: {line}")
            
            # Fnat 추출
            elif 'fnat' in line:
                try:
                    fnat = float(line.split()[1])
                except (ValueError, IndexError):
                    print(f"Error parsing Fnat from line: {line}")
            
            # DockQ 값 추출
            elif 'DockQ:' in line:
                try:
                    dockq = float(line.split()[1])
                except (ValueError, IndexError):
                    print(f"Error parsing DockQ from line: {line}")
    
    return lrmsd, irmsd, fnat, dockq

# 체인을 수정하는 함수 (TER 이후 등장하는 리간드 체인을 'X'로 변경하고 중간에 등장하는 END 제거)
# def modify_chain(pdb_path):
#     temp_pdb_path = os.path.join(os.path.dirname(pdb_path), 'temp.pdb')
#     ligand_chain_started = False

#     with open(pdb_path, 'r') as f_in, open(temp_pdb_path, 'w') as f_out:
#         for line in f_in:
#             if line.startswith("END"):
#                 continue

#             if line.startswith("TER"):
#                 ligand_chain_started = True
#                 f_out.write(line)
#                 continue

#             if ligand_chain_started and (line.startswith("ATOM") or line.startswith("HETATM")):
#                 modified_line = line[:21] + 'X' + line[22:]  # 체인을 'X'로 수정
#                 f_out.write(modified_line)
#             else:
#                 f_out.write(line)

#         # 마지막에 END 추가
#         f_out.write("END\n")

#     print(f"Generated temp file with modified chain: {temp_pdb_path}")
#     return temp_pdb_path

# 로그 확인코드
def modify_chain(pdb_path):
    temp_pdb_path = os.path.join(os.path.dirname(pdb_path), 'temp.pdb')
    ligand_chain_started = False
    end_encountered = False

    with open(pdb_path, 'r') as f_in, open(temp_pdb_path, 'w') as f_out:
        for line in f_in:
            # 중간에 등장하는 'END' 줄은 제거하고 리간드 시작을 알림
            if line.startswith("END") and not end_encountered:
                end_encountered = True
                continue

            # 첫 번째 END 이후부터는 리간드로 간주하고 체인을 'X'로 수정
            if end_encountered and (line.startswith("ATOM") or line.startswith("HETATM") or line.startswith("ANISOU")):
                modified_line = line[:21] + 'X' + line[22:]  # 체인을 'X'로 수정
                f_out.write(modified_line)
            else:
                f_out.write(line)

        # 마지막에 END 추가
        f_out.write("END\n")

    print(f"Generated temp file with modified chain: {temp_pdb_path}")
    return temp_pdb_path



# PDB 파일 검증 및 체인 검증 후 저장
def validate_pdb(pdb_path):
    temp_tidy_path = os.path.join(os.path.dirname(pdb_path), 'temp_tidy.pdb')
    temp_fix_path = os.path.join(os.path.dirname(pdb_path), 'temp_fix.pdb')
    temp_reatom_path = os.path.join(os.path.dirname(pdb_path), 'temp_reatom.pdb')
    
    try:
        # 1. pdb_tidy 실행
        subprocess.run(f'pdb_tidy {pdb_path} > {temp_tidy_path}', shell=True, check=True)
        
        # 2. pdb_fixinsert 실행
        subprocess.run(f'pdb_fixinsert {temp_tidy_path} > {temp_fix_path}', shell=True, check=True)
        
        # 3. pdb_reatom 실행
        subprocess.run(f'pdb_reatom {temp_fix_path} > {temp_reatom_path}', shell=True, check=True)
        
        # 검증
        with open(temp_reatom_path, 'r') as pdb_file:
            chains = set()
            for line in pdb_file:
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    chain_id = line[21]  # 체인 ID 위치
                    chains.add(chain_id)

        if len(chains) < 2:
            raise ValueError(f"PDB file {pdb_path} contains fewer than 2 chains, which is required for DockQ.")
    
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error in pdb-tools: {e}")
    
    return temp_reatom_path



# 상위 10개의 complex PDB에 대해 lrmsd, irmsd, fnat 계산
def calculate_top_10_ranking_results(predict_sort_file, complex_dir, ref_pdb, output_file):
    top_10_pdbs = []
    with open(predict_sort_file, 'r') as file:
        for i, line in enumerate(file):
            # 상위 n개 사용
            # if i >= 10:
            #     break
            pdb_name = line.split()[0] + '.pdb'
            top_10_pdbs.append(pdb_name)

    with open(output_file, 'w') as out_file:
        out_file.write("pdb_name\tlrmsd\tirmsd\tfnat\tdockq\n")
        for pdb_name in top_10_pdbs:
            complex_pdb_path = os.path.join(complex_dir, pdb_name)

            # 먼저 체인을 수정한 temp 파일 생성
            # 이상 없음
            temp_pdb_path = modify_chain(complex_pdb_path)

            # 체인이 수정된 temp 파일에 대해 유효성 검증
            fixed_pdb_path = validate_pdb(temp_pdb_path)

            # DockQ 계산
            lrmsd, irmsd, fnat, dockq = runDockQ(fixed_pdb_path, ref_pdb)
            out_file.write(f"{pdb_name}\t{lrmsd}\t{irmsd}\t{fnat}\t{dockq}\n")
            print(f"Processed: {pdb_name} -> lrmsd: {lrmsd}, irmsd: {irmsd}, fnat: {fnat}, dockq: {dockq}")

            # temp 파일 삭제
            # os.remove(temp_pdb_path)


# 옵션 처리
usage = "USAGE: python calcrmsdsdockq_from_dove.py --complex_dir <complex_pdb_directory> --ref_pdb <reference_pdb> --output <output_txt_file>"
parser = OptionParser(usage=usage)
parser.add_option("--complex_dir", help="Directory containing complex PDB files", dest="complex_dir")
parser.add_option("--ref_pdb", help="Path to reference (original) PDB file", dest="ref_pdb")
parser.add_option("--output", help="Output file to store the results", dest="output")
parser.add_option("--predict_sort", help="Path to the GNN_DOVE sorted Predict_sort.txt file", dest="predict_sort")

(options, args) = parser.parse_args()

if not options.complex_dir or not options.ref_pdb or not options.output or not options.predict_sort:
    print("Missing required arguments. Please refer to the usage instructions.")
    exit()

calculate_top_10_ranking_results(options.predict_sort, options.complex_dir, options.ref_pdb, options.output)
