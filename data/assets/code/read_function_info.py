import csv

function_names = []

with open('./tools_document.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        if line.startswith('def '):
            function_name = line[4:].split('(')[0]
            function_names.append(function_name)

with open('./render/function_names.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for function_name in function_names:
        writer.writerow([function_name])


sentences = []

with open('./tools_document.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        if line.startswith('    """'):
            end_pos = line.find('.')
            sentence = line[7:end_pos+1].strip()
            sentences.append(sentence)

with open('./render/function_des.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for sentence in sentences:
        writer.writerow([sentence])