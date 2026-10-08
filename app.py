
import json
import os
import re
from io import BytesIO
from datetime import datetime

import streamlit as st
from openai import OpenAI
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)

st.set_page_config(
    page_title="Transformaker Aula",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------
# Visual identity
# ----------------------------
NAVY = "#0F2D52"
BLUE = "#1F5E7A"
GOLD = "#D4AF37"
LIGHT = "#EAEAEA"

st.markdown(f"""
<style>
    .stApp {{ background: #f7f9fb; }}
    .main-title {{ color:{NAVY}; font-size:2.45rem; font-weight:800; margin-bottom:0; }}
    .subtitle {{ color:{BLUE}; font-size:1.05rem; margin-top:0.15rem; }}
    .hero {{
        background: linear-gradient(135deg, {NAVY}, {BLUE});
        color:white; padding:1.7rem 2rem; border-radius:18px;
        margin-bottom:1.2rem;
    }}
    .hero h1 {{ color:white; margin:0; font-size:2.2rem; }}
    .hero p {{ margin:0.4rem 0 0; opacity:.92; }}
    .card {{
        background:white; border:1px solid #e5e9ee; border-radius:14px;
        padding:1.1rem 1.2rem; margin-bottom:0.8rem;
        box-shadow:0 2px 10px rgba(15,45,82,.05);
    }}
    .section-title {{ color:{NAVY}; font-weight:800; font-size:1.25rem; }}
    .badge {{
        display:inline-block; background:#eef4f7; color:{NAVY};
        border-radius:999px; padding:.25rem .65rem; margin:.15rem;
        font-size:.82rem; font-weight:700;
    }}
    .gold-line {{ height:4px; background:{GOLD}; border-radius:10px; margin:.7rem 0 1rem; }}
    .small {{ color:#667085; font-size:.86rem; }}
    div.stButton > button[kind="primary"] {{
        background:{NAVY}; border-color:{NAVY}; font-weight:800;
    }}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Helpers
# ----------------------------
def get_secret(name, default=""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)

def demo_lesson(data):
    tema = data["tema"]
    ano = data["ano"]
    disciplina = data["disciplina"]
    duracao = data["duracao"]
    return {
        "titulo": tema,
        "subtitulo": f"{ano} | {disciplina} | {duracao} minutos",
        "objetivos": [
            f"Compreender os conceitos fundamentais relacionados a {tema}.",
            "Relacionar o conteúdo com situações históricas, sociais ou cotidianas.",
            "Demonstrar a aprendizagem por meio de atividades e questões de avaliação."
        ],
        "apostila": {
            "introducao": f"Esta aula apresenta uma introdução clara e contextualizada ao tema {tema}, considerando o nível do {ano}.",
            "conteudo": [
                f"O que é {tema}?",
                f"Contexto e conceitos fundamentais de {tema}.",
                f"Principais características e consequências relacionadas a {tema}.",
                "Relações com a realidade e conhecimentos prévios dos estudantes."
            ],
            "resumo": f"Em síntese, {tema} deve ser compreendido a partir de seus conceitos centrais, contexto, consequências e relações com a realidade."
        },
        "mapa_conceitual": {
            "centro": tema,
            "ramos": ["Contexto", "Conceitos principais", "Características", "Consequências", "Relação com a realidade"]
        },
        "infografico": {
            "titulo": tema,
            "blocos": [
                {"titulo": "1. Contexto", "texto": "Apresente o cenário e os conhecimentos prévios."},
                {"titulo": "2. Conceito", "texto": f"Defina {tema} com linguagem adequada à turma."},
                {"titulo": "3. Elementos", "texto": "Organize os principais elementos em palavras-chave."},
                {"titulo": "4. Consequências", "texto": "Mostre impactos e relações de causa e consequência."},
                {"titulo": "5. Conexão", "texto": "Relacione o conteúdo à vida do estudante."}
            ]
        },
        "atividades": [
            {"tipo": "Compreensão", "questao": f"Explique, com suas palavras, o que você entendeu sobre {tema}."},
            {"tipo": "Relação", "questao": f"Qual relação você consegue estabelecer entre {tema} e situações do cotidiano?"},
            {"tipo": "Desafio", "questao": f"Imagine que você precisa ensinar {tema} a um colega. Quais seriam os três pontos mais importantes?"}
        ],
        "avaliacao": [
            {"tipo": "Objetiva", "questao": f"Qual alternativa apresenta melhor uma característica central de {tema}?", "alternativas": ["A) Uma característica sem relação com o tema.", "B) Uma característica diretamente relacionada ao tema.", "C) Uma afirmação contraditória.", "D) Uma informação aleatória."], "resposta": "B"},
            {"tipo": "Discursiva", "questao": f"Explique a importância de compreender {tema}.", "resposta": "Resposta esperada: apresentar conceito, contexto e uma relação coerente com o conteúdo estudado."},
        ],
        "dua": {
            "representacao": ["Usar texto + palavras-chave + recurso visual.", "Destacar conceitos essenciais.", "Ler ou explicar oralmente instruções importantes."],
            "acao_expressao": ["Permitir resposta escrita, oral, desenho ou esquema.", "Dividir tarefas longas em etapas menores."],
            "engajamento": ["Usar pergunta-problema.", "Relacionar o tema aos interesses e experiências dos estudantes."]
        },
        "pei_paee": [
            "Definir um objetivo individual observável e compatível com as possibilidades do estudante.",
            "Oferecer instruções curtas, exemplos e apoio visual.",
            "Permitir forma alternativa de resposta quando necessário.",
            "Registrar evidências de participação e aprendizagem."
        ],
        "curriculo": {
            "componente": disciplina,
            "ano": ano,
            "alinhamento": "O alinhamento curricular deve ser validado pelo professor ou pela rede de ensino antes do uso oficial. O protótipo não inventa códigos de habilidades."
        },
        "roteiro": [
            {"tempo": "0–5 min", "etapa": "Abertura", "fala": f"Comece perguntando o que a turma já sabe sobre {tema}."},
            {"tempo": "5–15 min", "etapa": "Contextualização", "fala": "Apresente o contexto e os conceitos fundamentais."},
            {"tempo": "15–30 min", "etapa": "Desenvolvimento", "fala": "Explique os pontos centrais usando o mapa e o infográfico."},
            {"tempo": "30–43 min", "etapa": "Atividade", "fala": "Aplique as atividades e acompanhe as dificuldades."},
            {"tempo": "43–50 min", "etapa": "Fechamento", "fala": "Retome as ideias principais e faça uma pergunta de síntese."}
        ]
    }

def build_prompt(data):
    inclusion = []
    if data["dua"]:
        inclusion.append("DUA")
    if data["pei_paee"]:
        inclusion.append("PEI/PAEE")
    inclusion_text = ", ".join(inclusion) if inclusion else "não solicitada"

    return f"""
Você é o motor pedagógico do TRANSFORMAKER AULA, uma plataforma brasileira para professores.
Sua missão é transformar um tema em um pacote completo para UMA aula real, útil, claro, imprimível e adequado à faixa etária.

REGRAS IMPORTANTES:
1. Não invente códigos, habilidades ou referências curriculares específicas. Se não houver uma base curricular fornecida, descreva o alinhamento de forma geral e sinalize que deve ser validado.
2. Escreva em português do Brasil.
3. Evite linguagem acadêmica desnecessária. O professor precisa conseguir usar o material.
4. O conteúdo deve ser adequado ao ano/série informado.
5. Não produza texto genérico: conecte todas as partes ao tema.
6. O roteiro deve caber na duração indicada.
7. As atividades devem ter propósito pedagógico.
8. A avaliação deve conter gabarito.
9. Se DUA ou PEI/PAEE forem solicitados, produza adaptações práticas, não apenas definições.
10. Retorne SOMENTE JSON válido, sem markdown e sem comentários.

DADOS DA AULA:
Tema: {data["tema"]}
Ano/Série: {data["ano"]}
Disciplina: {data["disciplina"]}
Duração: {data["duracao"]} minutos
Objetivo informado pelo professor: {data["objetivo"] or "não informado; defina objetivos adequados"}
Nível da turma: {data["nivel"]}
Metodologia: {data["metodologia"]}
Inclusão solicitada: {inclusion_text}

FORMATO JSON OBRIGATÓRIO:
{{
  "titulo": "string",
  "subtitulo": "string",
  "objetivos": ["string", "string", "string"],
  "apostila": {{
    "introducao": "string",
    "conteudo": ["string", "string", "string", "string"],
    "resumo": "string"
  }},
  "mapa_conceitual": {{
    "centro": "string",
    "ramos": ["string", "string", "string", "string", "string"]
  }},
  "infografico": {{
    "titulo": "string",
    "blocos": [
      {{"titulo":"string","texto":"string"}},
      {{"titulo":"string","texto":"string"}},
      {{"titulo":"string","texto":"string"}},
      {{"titulo":"string","texto":"string"}},
      {{"titulo":"string","texto":"string"}}
    ]
  }},
  "atividades": [
    {{"tipo":"string","questao":"string"}},
    {{"tipo":"string","questao":"string"}},
    {{"tipo":"string","questao":"string"}},
    {{"tipo":"string","questao":"string"}}
  ],
  "avaliacao": [
    {{"tipo":"Objetiva","questao":"string","alternativas":["A) ...","B) ...","C) ...","D) ..."],"resposta":"A"}},
    {{"tipo":"Objetiva","questao":"string","alternativas":["A) ...","B) ...","C) ...","D) ..."],"resposta":"B"}},
    {{"tipo":"Discursiva","questao":"string","resposta":"string"}}
  ],
  "dua": {{
    "representacao":["string","string","string"],
    "acao_expressao":["string","string","string"],
    "engajamento":["string","string","string"]
  }},
  "pei_paee":["string","string","string","string"],
  "curriculo": {{
    "componente":"string",
    "ano":"string",
    "alinhamento":"string"
  }},
  "roteiro": [
    {{"tempo":"string","etapa":"string","fala":"string"}},
    {{"tempo":"string","etapa":"string","fala":"string"}},
    {{"tempo":"string","etapa":"string","fala":"string"}},
    {{"tempo":"string","etapa":"string","fala":"string"}},
    {{"tempo":"string","etapa":"string","fala":"string"}}
  ]
}}
"""

def call_ai(data):
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        return demo_lesson(data), True

    model = get_secret("OPENAI_MODEL", "gpt-5.2")
    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model,
        input=build_prompt(data),
        max_output_tokens=9000,
    )
    raw = response.output_text.strip()

    # Remove accidental fenced JSON.
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.I)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw), False
    except json.JSONDecodeError:
        # Second pass asks the model to repair only JSON.
        repair = client.responses.create(
            model=model,
            input=(
                "Converta o texto abaixo em JSON válido, preservando o conteúdo. "
                "Retorne somente JSON.\n\n" + raw
            ),
            max_output_tokens=9000,
        )
        return json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", repair.output_text.strip())), False

def safe(v):
    return str(v) if v is not None else ""

def generate_pdf(lesson):
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle("TitleCustom", parent=styles["Title"], fontName="Helvetica-Bold",
                           fontSize=20, leading=24, alignment=TA_CENTER, textColor=colors.HexColor(NAVY))
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold",
                        fontSize=14, leading=18, textColor=colors.HexColor(NAVY), spaceBefore=10)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold",
                        fontSize=11, leading=14, textColor=colors.HexColor(BLUE), spaceBefore=7)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica",
                          fontSize=9.5, leading=13, spaceAfter=5)
    small = ParagraphStyle("Small", parent=body, fontSize=8.5, leading=11)

    story = [
        Paragraph("TRANSFORMAKER AULA", title),
        Spacer(1, 0.2*cm),
        Paragraph(safe(lesson.get("titulo")), h1),
        Paragraph(safe(lesson.get("subtitulo")), body),
        Spacer(1, 0.2*cm),
        Paragraph("OBJETIVOS DE APRENDIZAGEM", h1),
    ]
    for x in lesson.get("objetivos", []):
        story.append(Paragraph("• " + safe(x), body))

    ap = lesson.get("apostila", {})
    story += [Paragraph("MATERIAL DO ALUNO", h1),
              Paragraph("Introdução", h2),
              Paragraph(safe(ap.get("introducao")), body)]
    for x in ap.get("conteudo", []):
        story.append(Paragraph("• " + safe(x), body))
    story += [Paragraph("Resumo", h2), Paragraph(safe(ap.get("resumo")), body)]

    mapa = lesson.get("mapa_conceitual", {})
    story += [Paragraph("MAPA CONCEITUAL", h1)]
    center = safe(mapa.get("centro"))
    rows = [[Paragraph(f"<b>{center}</b>", body)]]
    for r in mapa.get("ramos", []):
        rows.append([Paragraph("→ " + safe(r), body)])
    t = Table(rows, colWidths=[16*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor(NAVY)),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("BOX", (0,0), (-1,-1), 0.7, colors.HexColor(BLUE)),
        ("INNERGRID", (0,0), (-1,-1), 0.3, colors.HexColor(LIGHT)),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [t, Paragraph("INFOGRÁFICO", h1)]
    blocks = lesson.get("infografico", {}).get("blocos", [])
    data_rows = []
    for b in blocks:
        data_rows.append([
            Paragraph("<b>" + safe(b.get("titulo")) + "</b>", small),
            Paragraph(safe(b.get("texto")), small)
        ])
    if data_rows:
        it = Table(data_rows, colWidths=[4.2*cm, 11.8*cm])
        it.setStyle(TableStyle([
            ("BOX", (0,0), (-1,-1), .5, colors.HexColor(BLUE)),
            ("INNERGRID", (0,0), (-1,-1), .3, colors.HexColor(LIGHT)),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#eef4f7")),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(it)

    story += [PageBreak(), Paragraph("ATIVIDADES", h1)]
    for i, a in enumerate(lesson.get("atividades", []), 1):
        story.append(Paragraph(f"<b>{i}. {safe(a.get('tipo'))}</b> — {safe(a.get('questao'))}", body))

    story += [Paragraph("AVALIAÇÃO", h1)]
    for i, q in enumerate(lesson.get("avaliacao", []), 1):
        story.append(Paragraph(f"<b>{i}. {safe(q.get('tipo'))}</b> — {safe(q.get('questao'))}", body))
        for alt in q.get("alternativas", []):
            story.append(Paragraph(safe(alt), small))
        if q.get("resposta"):
            story.append(Paragraph("<b>Gabarito:</b> " + safe(q.get("resposta")), small))

    story += [Paragraph("DUA — DESENHO UNIVERSAL PARA APRENDIZAGEM", h1)]
    for key, label in [("representacao","Representação"),("acao_expressao","Ação e expressão"),("engajamento","Engajamento")]:
        story.append(Paragraph(label, h2))
        for x in lesson.get("dua", {}).get(key, []):
            story.append(Paragraph("• " + safe(x), body))

    story += [Paragraph("SUGESTÕES PARA PEI/PAEE", h1)]
    for x in lesson.get("pei_paee", []):
        story.append(Paragraph("• " + safe(x), body))

    cur = lesson.get("curriculo", {})
    story += [Paragraph("ALINHAMENTO CURRICULAR", h1),
              Paragraph(f"<b>Componente:</b> {safe(cur.get('componente'))}", body),
              Paragraph(f"<b>Ano:</b> {safe(cur.get('ano'))}", body),
              Paragraph(safe(cur.get("alinhamento")), body)]

    story += [PageBreak(), Paragraph("ROTEIRO DO PROFESSOR", h1)]
    route_rows = [[Paragraph("<b>Tempo</b>", small), Paragraph("<b>Etapa</b>", small), Paragraph("<b>Orientação</b>", small)]]
    for r in lesson.get("roteiro", []):
        route_rows.append([Paragraph(safe(r.get("tempo")), small),
                           Paragraph(safe(r.get("etapa")), small),
                           Paragraph(safe(r.get("fala")), small)])
    rt = Table(route_rows, colWidths=[2.2*cm, 3.2*cm, 10.6*cm], repeatRows=1)
    rt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor(NAVY)),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), .4, colors.HexColor(LIGHT)),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(rt)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Material gerado pelo Transformaker Aula. O professor é responsável pela revisão e adequação final ao contexto da turma.", small))

    doc.build(story)
    return buf.getvalue()

def render_bullets(items):
    for x in items or []:
        st.markdown(f"- {x}")

# ----------------------------
# Session state
# ----------------------------
if "lesson" not in st.session_state:
    st.session_state.lesson = None
if "history" not in st.session_state:
    st.session_state.history = []

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    st.markdown(f"<div class='section-title'>🎓 Transformaker Aula</div>", unsafe_allow_html=True)
    st.markdown("**Do tema à aula completa.**")
    st.markdown("---")
    st.markdown("### Recursos")
    st.markdown("📘 Apostila\n\n🧠 Mapa conceitual\n\n🎨 Infográfico\n\n📝 Atividades\n\n❓ Avaliação\n\n♿ DUA\n\n📋 PEI/PAEE\n\n🎤 Roteiro docente")
    st.markdown("---")
    key_ok = bool(get_secret("OPENAI_API_KEY"))
    if key_ok:
        st.success("IA conectada")
    else:
        st.info("Modo demonstração ativo")
        st.caption("Para geração real, configure OPENAI_API_KEY nos Secrets do Streamlit.")
    st.markdown("---")
    st.caption("Transformaker — tecnologia transformada em soluções reais.")

# ----------------------------
# Header
# ----------------------------
st.markdown("""
<div class="hero">
<h1>Transformaker Aula</h1>
<p>Transforme um tema em uma aula completa, pronta para ensinar, adaptar e imprimir.</p>
</div>
""", unsafe_allow_html=True)

tab_new, tab_library = st.tabs(["🚀 Criar aula", "📚 Minhas aulas"])

with tab_new:
    st.markdown("<div class='section-title'>1. Defina a aula</div>", unsafe_allow_html=True)
    st.markdown("<div class='gold-line'></div>", unsafe_allow_html=True)

    with st.form("lesson_form"):
        c1, c2 = st.columns(2)
        with c1:
            tema = st.text_input("Tema da aula *", placeholder="Ex.: Revolução Industrial")
            ano = st.selectbox("Série / Ano", [
                "1º ano", "2º ano", "3º ano", "4º ano", "5º ano",
                "6º ano", "7º ano", "8º ano", "9º ano",
                "1ª série EM", "2ª série EM", "3ª série EM"
            ], index=7)
            disciplina = st.selectbox("Disciplina", [
                "História", "Geografia", "Matemática", "Ciências",
                "Língua Portuguesa", "Inglês", "Artes", "Educação Física",
                "Ensino Religioso", "Tecnologia / Computação", "Outra"
            ])
        with c2:
            duracao = st.selectbox("Tempo de aula", [30, 40, 45, 50, 60, 90, 100], index=3)
            nivel = st.selectbox("Nível da turma", ["Iniciante", "Intermediário", "Avançado"])
            metodologia = st.selectbox("Metodologia", [
                "Escolha por mim",
                "Aula expositiva dialogada",
                "Aprendizagem baseada em problemas",
                "Aprendizagem baseada em projetos",
                "Sala de aula invertida",
                "Gamificação",
                "Investigação / descoberta"
            ])

        objetivo = st.text_area(
            "Objetivo da aula (opcional)",
            placeholder="Ex.: compreender as principais transformações provocadas pela Revolução Industrial."
        )

        st.markdown("### ♿ Inclusão")
        ci1, ci2 = st.columns(2)
        with ci1:
            dua = st.checkbox("Gerar estratégias DUA", value=True)
        with ci2:
            pei_paee = st.checkbox("Gerar sugestões PEI/PAEE", value=False)

        submitted = st.form_submit_button("🚀 GERAR AULA COMPLETA", type="primary", use_container_width=True)

    if submitted:
        if not tema.strip():
            st.error("Digite o tema da aula.")
        else:
            data = {
                "tema": tema.strip(),
                "ano": ano,
                "disciplina": disciplina,
                "duracao": duracao,
                "objetivo": objetivo.strip(),
                "nivel": nivel,
                "metodologia": metodologia,
                "dua": dua,
                "pei_paee": pei_paee,
            }
            with st.spinner("Transformaker está construindo a aula completa..."):
                try:
                    lesson, demo = call_ai(data)
                    lesson["_meta"] = data
                    lesson["_demo"] = demo
                    lesson["_created"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    st.session_state.lesson = lesson
                    st.session_state.history.insert(0, lesson)
                except Exception as e:
                    st.error("Não foi possível gerar a aula.")
                    st.exception(e)

    lesson = st.session_state.lesson

    if lesson:
        if lesson.get("_demo"):
            st.warning("Você está vendo uma aula de demonstração. Configure sua chave da OpenAI para gerar conteúdos reais.")

        st.markdown("---")
        st.markdown(f"# {lesson.get('titulo', 'Aula')}")
        st.caption(lesson.get("subtitulo", ""))

        pdf_bytes = generate_pdf(lesson)
        d1, d2 = st.columns([1, 1])
        with d1:
            st.download_button(
                "📥 Baixar aula completa em PDF",
                data=pdf_bytes,
                file_name="transformaker_aula.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with d2:
            if st.button("🧹 Limpar aula", use_container_width=True):
                st.session_state.lesson = None
                st.rerun()

        r1, r2, r3 = st.columns(3)
        r1.metric("Objetivos", len(lesson.get("objetivos", [])))
        r2.metric("Atividades", len(lesson.get("atividades", [])))
        r3.metric("Questões", len(lesson.get("avaliacao", [])))

        tabs = st.tabs([
            "📘 Apostila", "🧠 Mapa", "🎨 Infográfico", "📝 Atividades",
            "❓ Avaliação", "♿ DUA", "📋 PEI/PAEE", "📚 Currículo", "🎤 Professor"
        ])

        with tabs[0]:
            st.subheader("Objetivos de aprendizagem")
            render_bullets(lesson.get("objetivos"))
            ap = lesson.get("apostila", {})
            st.subheader("Introdução")
            st.write(ap.get("introducao", ""))
            st.subheader("Conteúdo")
            render_bullets(ap.get("conteudo"))
            st.subheader("Resumo")
            st.write(ap.get("resumo", ""))

        with tabs[1]:
            mapa = lesson.get("mapa_conceitual", {})
            st.markdown(f"<div class='card'><h3>{mapa.get('centro','')}</h3></div>", unsafe_allow_html=True)
            for r in mapa.get("ramos", []):
                st.markdown(f"**↓ {r}**")
                st.markdown("---")

        with tabs[2]:
            info = lesson.get("infografico", {})
            st.subheader(info.get("titulo", "Infográfico"))
            cols = st.columns(2)
            for i, b in enumerate(info.get("blocos", [])):
                with cols[i % 2]:
                    st.markdown(f"<div class='card'><b>{b.get('titulo','')}</b><br>{b.get('texto','')}</div>", unsafe_allow_html=True)

        with tabs[3]:
            for i, a in enumerate(lesson.get("atividades", []), 1):
                st.markdown(f"### {i}. {a.get('tipo','Atividade')}")
                st.write(a.get("questao", ""))

        with tabs[4]:
            for i, q in enumerate(lesson.get("avaliacao", []), 1):
                st.markdown(f"### {i}. {q.get('tipo','Questão')}")
                st.write(q.get("questao", ""))
                for alt in q.get("alternativas", []):
                    st.write(alt)
                if q.get("resposta"):
                    st.success(f"Gabarito: {q.get('resposta')}")

        with tabs[5]:
            dua_data = lesson.get("dua", {})
            for key, title in [("representacao","Múltiplas formas de representação"),
                               ("acao_expressao","Múltiplas formas de ação e expressão"),
                               ("engajamento","Múltiplas formas de engajamento")]:
                st.subheader(title)
                render_bullets(dua_data.get(key))

        with tabs[6]:
            render_bullets(lesson.get("pei_paee"))

        with tabs[7]:
            cur = lesson.get("curriculo", {})
            st.write(f"**Componente:** {cur.get('componente','')}")
            st.write(f"**Ano:** {cur.get('ano','')}")
            st.info(cur.get("alinhamento", ""))

        with tabs[8]:
            for r in lesson.get("roteiro", []):
                st.markdown(f"**{r.get('tempo','')} — {r.get('etapa','')}**")
                st.write(r.get("fala", ""))
                st.markdown("---")

with tab_library:
    st.markdown("<div class='section-title'>📚 Aulas desta sessão</div>", unsafe_allow_html=True)
    if not st.session_state.history:
        st.info("As aulas criadas aparecerão aqui durante esta sessão.")
    else:
        for i, item in enumerate(st.session_state.history):
            meta = item.get("_meta", {})
            label = f"{item.get('titulo','Aula')} — {meta.get('ano','')} — {item.get('_created','')}"
            if st.button(label, key=f"history_{i}", use_container_width=True):
                st.session_state.lesson = item
                st.rerun()
