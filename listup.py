import os

def save_directories_in_path(directory_path, output_file):
    # 지정된 경로의 바로 하위 디렉토리만 가져옴
    with open(output_file, 'w', encoding='utf-8') as f:  # UTF-8 인코딩 적용
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path):  # 디렉토리인지 확인
                f.write(item + '\n')  # 디렉토리 이름을 기록

# 경로와 출력 파일명 설정
directory_path = "MEGADOCK_output"  # 디렉토리 이름을 검색할 상위 디렉토리 경로
output_file = "megadock_list.txt"  # 디렉토리 이름을 저장할 텍스트 파일 이름

# 함수 호출
save_directories_in_path(directory_path, output_file)

print(f"디렉토리 이름이 '{output_file}'에 저장되었습니다.")

