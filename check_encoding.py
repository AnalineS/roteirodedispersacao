import os

root = 'roteiro-de-dispersacao-v4'
problemas = []

for subdir, _, files in os.walk(root):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(subdir, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    f.read()
            except Exception as e:
                problemas.append((path, str(e)))

if problemas:
    print('Arquivos com encoding inválido (não UTF-8):')
    for path, err in problemas:
        print(f'{path} -> {err}')
else:
    print('Todos os arquivos .py estão em UTF-8.') 