# TRANSFORMAKER AULA — MVP

Aplicação web responsiva para transformar um tema em uma aula completa.

## O que já está incluído

- Tema, série, disciplina, duração e objetivo
- Nível da turma
- Escolha de metodologia
- DUA
- PEI/PAEE
- Apostila/resumo
- Mapa conceitual
- Infográfico
- Atividades
- Avaliação com gabarito
- Alinhamento curricular com aviso de validação
- Roteiro do professor
- Exportação para PDF
- Histórico de aulas na sessão
- Modo demonstração quando não existe chave de IA

## Tecnologia

- Python
- Streamlit
- OpenAI Responses API
- ReportLab
- PWA-ready/responsivo via navegador

## Publicação no Streamlit Community Cloud

1. Crie um repositório no GitHub.
2. Envie todos os arquivos desta pasta para o repositório.
3. Entre em https://share.streamlit.io/ e conecte o GitHub.
4. Clique em Create app.
5. Selecione o repositório, branch `main` e o arquivo `app.py`.
6. Em Advanced settings > Secrets, informe:

OPENAI_API_KEY = "sua-chave-aqui"
OPENAI_MODEL = "gpt-5.2"

7. Publique.

O Streamlit Community Cloud instala as dependências a partir do `requirements.txt`.

## Rodar no computador

Windows:

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:OPENAI_API_KEY="sua-chave-aqui"
streamlit run app.py
```

Mac/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="sua-chave-aqui"
streamlit run app.py
```

## Segurança

Nunca coloque a chave da API dentro do código ou do GitHub.
Use os Secrets do Streamlit Cloud.

## Próxima evolução recomendada

Este MVP foi feito para validar a experiência pedagógica. Para uma versão comercial, evolua para:

- login Google
- contas de professores
- banco PostgreSQL
- créditos/assinaturas
- biblioteca persistente
- painel de escola
- painel de secretaria
- base curricular estruturada
- geração real de imagens
- domínio próprio
- métricas e controle de custos de IA
