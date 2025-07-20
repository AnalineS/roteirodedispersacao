# test_md.py
# Teste simples para ler o arquivo Markdown e exibir o conteúdo

def ler_markdown():
    caminho = "PDFs/Roteiro de Dsispensação - Hanseníase.md"
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()
        print("Arquivo lido com sucesso!")
        print(f"Primeiros 500 caracteres:\n{conteudo[:500]}")
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")

if __name__ == "__main__":
    ler_markdown() 