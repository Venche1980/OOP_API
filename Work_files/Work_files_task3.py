import os

def combine_files(file_list, output_file):

    file_contents = {}

    for file_name in file_list:
        with open(file_name, 'r', encoding='utf-8') as f:
            content = f.readlines()
            file_contents[file_name] = content

    sorted_files = sorted(file_contents.items(), key=lambda item: len(item[1]))

    with open(output_file, 'w', encoding='utf-8') as output:
        for file_name, content in sorted_files:
            output.write(f"{file_name}\n")
            output.write(f"{len(content)}\n")
            output.writelines(content)
            output.write("\n")

file_list = ['1.txt', '2.txt', '3.txt']
output_file = 'result.txt'
combine_files(file_list, output_file)
