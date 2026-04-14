import io
import textwrap
from datetime import datetime

import streamlit as st
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Image as RLImage, PageBreak, KeepTogether, HRFlowable,
)

st.set_page_config(page_title="Laporan Generator", layout="wide", page_icon="📄")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@300;400;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
    font-family: 'Source Sans 3', sans-serif !important;
    background: #FAF6EE !important;
    color: #2C1810 !important;
}
h1 { font-family: 'Playfair Display', serif !important; color: #3B2410 !important; font-size: 2rem !important; margin-bottom: 0 !important; }
h2, h3 { font-family: 'Playfair Display', serif !important; color: #5C3A1E !important; }

.stTextInput > label, .stTextArea > label, .stSelectbox > label,
.stFileUploader > label, .stCheckbox > label, .stRadio > label {
    font-size: 0.82rem !important; font-weight: 700 !important;
    color: #7A4A20 !important; text-transform: uppercase !important; letter-spacing: 0.5px !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #FFFDF5 !important; border: 1.5px solid #D4A855 !important;
    border-radius: 6px !important; color: #2C1810 !important; font-size: 0.95rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #A0722A !important; box-shadow: 0 0 0 3px rgba(160,114,42,0.15) !important; outline: none !important;
}
.stSelectbox > div > div {
    background: #FFFDF5 !important; border: 1.5px solid #D4A855 !important;
    border-radius: 6px !important; color: #2C1810 !important;
}
.stButton > button {
    background: #FFFDF5 !important; color: #5C3A1E !important;
    border: 1.5px solid #C89B3C !important; border-radius: 6px !important;
    font-weight: 600 !important; font-size: 0.85rem !important;
    padding: 0.35rem 0.8rem !important; transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #F5E8C0 !important; border-color: #A0722A !important; color: #3B2410 !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #5C3A1E 0%, #3B2410 100%) !important;
    color: #F5E2A0 !important; border: 2px solid #C89B3C !important;
    border-radius: 8px !important; font-family: 'Playfair Display', serif !important;
    font-size: 1.1rem !important; font-weight: 700 !important;
    padding: 0.65rem 1.5rem !important; transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #7A4A20 0%, #5C3A1E 100%) !important;
    box-shadow: 0 4px 16px rgba(59,36,16,0.3) !important; transform: translateY(-1px) !important;
}
.streamlit-expanderHeader {
    background: #F5E8C0 !important; color: #3B2410 !important;
    font-weight: 700 !important; border-radius: 8px !important; border: 1px solid #D4A855 !important;
}
.streamlit-expanderContent {
    background: #FFFDF8 !important; border: 1px solid #E8D5A0 !important;
    border-top: none !important; border-radius: 0 0 8px 8px !important;
}
.stFileUploader > div {
    background: #FFFDF8 !important; border: 2px dashed #C89B3C !important; border-radius: 8px !important;
}
hr { border-color: #D4A855 !important; opacity: 0.4 !important; }
.stAlert {
    background: #FFFBEE !important; border-left: 4px solid #C89B3C !important;
    color: #5C3A1E !important; border-radius: 0 8px 8px 0 !important;
}
.stRadio div[role="radiogroup"] label {
    background: #FFFDF5 !important; border: 1.5px solid #D4A855 !important;
    border-radius: 6px !important; padding: 0.3rem 0.7rem !important;
    margin-right: 6px !important; color: #5C3A1E !important; transition: all 0.15s !important;
}
.stRadio div[role="radiogroup"] label:has(input:checked) {
    background: #C89B3C !important; color: #FFFDF5 !important; border-color: #A0722A !important;
}
.preview-page {
    background: white; border: 1px solid #D4A855; border-radius: 4px;
    padding: 32px 28px; box-shadow: 0 4px 20px rgba(59,36,16,0.12);
    font-family: 'Times New Roman', Times, serif; color: #1a1a1a;
}
</style>
""", unsafe_allow_html=True)

# ── PDF colors ──────────────────────────────────────────────────────────────
C_DARK   = colors.HexColor("#3B2410")
C_MED    = colors.HexColor("#5C3A1E")
C_GOLD   = colors.HexColor("#C89B3C")
C_TEXT   = colors.HexColor("#1f2937")
C_MUTED  = colors.HexColor("#6B5B45")
C_CODEBG = colors.HexColor("#1E0F05")
C_CODEFG = colors.HexColor("#F5DFA0")


def build_styles():
    base = getSampleStyleSheet()
    specs = [
        ("CoverTop",    "Times-Bold",       24, 30, C_DARK,  TA_CENTER, 6,  0,  {}),
        ("CoverTitle",  "Times-Bold",       20, 26, C_MED,   TA_CENTER, 8,  0,  {}),
        ("CoverSub",    "Times-BoldItalic", 14, 20, C_GOLD,  TA_CENTER, 14, 0,  {}),
        ("Meta",        "Times-Roman",      12, 18, C_TEXT,  TA_CENTER, 2,  0,  {}),
        ("SecTitle",    "Times-Bold",       14, 18, C_DARK,  TA_LEFT,   6,  10, {}),
        ("SubSecTitle", "Times-BoldItalic", 12, 17, C_MED,   TA_LEFT,   4,  6,  {}),
        ("Body",        "Times-Roman",      12, 18, C_TEXT,  TA_JUSTIFY,8,  0,  {}),
        ("Caption",     "Times-Italic",     10, 13, C_MUTED, TA_CENTER, 8,  3,  {}),
        ("Identity",    "Times-Roman",      13, 22, C_TEXT,  TA_LEFT,   3,  0,  {"leftIndent": 3.0*cm}),
        ("QNumber",     "Times-Bold",       12, 17, C_MED,   TA_LEFT,   4,  4,  {}),
        ("Answer",      "Times-Roman",      12, 18, C_TEXT,  TA_JUSTIFY,6,  2,  {}),
        ("BulletBody",  "Times-Roman",      12, 18, C_TEXT,  TA_LEFT,   4,  0,  {"leftIndent": 0.5*cm, "firstLineIndent": -0.4*cm}),
    ]
    for name, font, size, lead, color, align, after, before, extra in specs:
        base.add(ParagraphStyle(name=name, parent=base["Normal"],
            fontName=font, fontSize=size, leading=lead,
            textColor=color, alignment=align,
            spaceAfter=after, spaceBefore=before, **extra))

    base.add(ParagraphStyle(name="CodeLabel", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=9, leading=11,
        textColor=C_CODEFG, backColor=colors.HexColor("#3B2410"),
        borderPadding=(4, 8, 4, 8), spaceBefore=8, spaceAfter=0))
    base.add(ParagraphStyle(name="CodeBody", parent=base["Normal"],
        fontName="Courier", fontSize=9, leading=13,
        textColor=C_CODEFG, backColor=C_CODEBG,
        borderPadding=(8, 10, 8, 10), spaceBefore=0, spaceAfter=10))
    return base


def header_footer(canvas, doc, title):
    # cover is page 1 — skip header/footer there
    if doc.page < 2:
        return
    canvas.saveState()
    w, h = A4
    canvas.setStrokeColor(C_MED)
    canvas.setLineWidth(1.5)
    canvas.line(1.8*cm, h - 1.3*cm, w - 1.8*cm, h - 1.3*cm)
    canvas.setStrokeColor(C_GOLD)
    canvas.setLineWidth(0.8)
    canvas.line(2.4*cm, h - 1.58*cm, w - 2.4*cm, h - 1.58*cm)
    canvas.setFillColor(C_MUTED)
    canvas.setFont("Times-Roman", 8.5)
    canvas.drawString(1.8*cm, 0.9*cm, title[:70])
    canvas.drawRightString(w - 1.8*cm, 0.9*cm, f"Hal. {doc.page}")
    canvas.restoreState()


def fit_img(f, mw=14, mh=9):
    img = PILImage.open(f)
    iw, ih = img.size
    r = min((mw*cm)/iw, (mh*cm)/ih)
    f.seek(0)
    return RLImage(f, width=iw*r, height=ih*r)


def code_flowables(code_text, label, styles):
    clean = textwrap.dedent(code_text).strip()
    if not clean:
        return []
    escaped = (clean
        .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        .replace(" ", "&nbsp;").replace("\t", "&nbsp;"*4).replace("\n", "<br/>"))
    return [
        Paragraph(label.strip() or "Kode Program", styles["CodeLabel"]),
        Paragraph(f"<font name='Courier'>{escaped}</font>", styles["CodeBody"]),
    ]


def add_images_to(story, images, styles, prefix):
    for j, img in enumerate(images, 1):
        if not img.get("file"):
            continue
        cap = img.get("caption", "").strip() or f"{prefix}.{j}"
        story.append(KeepTogether([fit_img(img["file"], 13, 8),
                                   Paragraph(cap, styles["Caption"])]))


def build_pdf(data):
    buf = io.BytesIO()
    styles = build_styles()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.4*cm, bottomMargin=2*cm,
        title=data["title"], author=data["author"])
    story = []

    # ── COVER (page 1, no header/footer) ────────────────────────────────────
    story.append(Spacer(1, 0.6*cm))
    story.append(Paragraph("LAPORAN PRAKTIKUM", styles["CoverTop"]))
    story.append(Paragraph(data["title"],    styles["CoverTitle"]))
    story.append(Paragraph(data["subtitle"], styles["CoverSub"]))
    story.append(HRFlowable(width="85%", thickness=1.5, color=C_MED,  spaceAfter=4, spaceBefore=4))
    story.append(HRFlowable(width="60%", thickness=0.8, color=C_GOLD, spaceAfter=18))
    if data.get("cover_image"):
        story.append(fit_img(data["cover_image"], 9, 9))
        story.append(Spacer(1, 0.8*cm))
    story.append(Spacer(1, 0.4*cm))
    for lbl, val in [("Nama", data["author"]), ("Kelas", data["class_name"]),
                     ("Mata Pelajaran", data["subject"]), ("Tanggal", data["date"])]:
        story.append(Paragraph(f"{lbl} : {val}", styles["Identity"]))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(data["school_year"], styles["Meta"]))
    story.append(PageBreak())  # → page 2

    # ── SECTIONS ────────────────────────────────────────────────────────────
    for idx, sec in enumerate(data["sections"], 1):
        stype = sec.get("type", "biasa")
        story.append(Paragraph(f"{idx}. {sec['heading']}", styles["SecTitle"]))

        if stype == "biasa":
            if sec.get("content"):
                story.append(Paragraph(sec["content"].replace("\n", "<br/>"), styles["Body"]))
            add_images_to(story, sec.get("images", []), styles, f"Gambar {idx}")
            if sec.get("code"):
                story.extend(code_flowables(sec["code"], sec.get("code_label", "Kode Program"), styles))

        elif stype == "tugas":
            if sec.get("intro"):
                story.append(Paragraph(sec["intro"].replace("\n", "<br/>"), styles["Body"]))
            for ti, task in enumerate(sec.get("tasks", []), 1):
                if task.get("subtitle"):
                    story.append(Paragraph(f"{idx}.{ti} {task['subtitle']}", styles["SubSecTitle"]))
                if task.get("content"):
                    story.append(Paragraph(task["content"].replace("\n", "<br/>"), styles["Body"]))
                add_images_to(story, task.get("images", []), styles, f"Gambar {idx}.{ti}")
                if task.get("code"):
                    story.extend(code_flowables(task["code"], task.get("code_label", f"Listing {idx}.{ti}"), styles))
                story.append(Spacer(1, 0.2*cm))

        elif stype == "formatif":
            for qi, q in enumerate(sec.get("questions", []), 1):
                story.append(Paragraph(f"{qi}. {q['question']}", styles["QNumber"]))
                add_images_to(story, q.get("images", []), styles, f"Gambar Soal {qi}")
                if q.get("answer"):
                    story.append(Paragraph(
                        f"Jawab: {q['answer'].replace(chr(10), '<br/>')}",
                        styles["Answer"]))
                story.append(Spacer(1, 0.15*cm))

        story.append(Spacer(1, 0.3*cm))

    if data.get("conclusion"):
        story.append(Paragraph("Kesimpulan", styles["SecTitle"]))
        story.append(Paragraph(data["conclusion"].replace("\n", "<br/>"), styles["Body"]))

    if data.get("references"):
        story.append(Paragraph("Daftar Pustaka", styles["SecTitle"]))
        for ref in data["references"].split("\n"):
            r = ref.strip()
            if r:
                story.append(Paragraph(f"• {r}", styles["BulletBody"]))

    doc.build(story,
        onFirstPage=lambda c, d: header_footer(c, d, data["title"]),
        onLaterPages=lambda c, d: header_footer(c, d, data["title"]))
    buf.seek(0)
    return buf


# ── SESSION STATE ────────────────────────────────────────────────────────────
def _sec(heading, stype, **kw):
    return {"heading": heading, "type": stype,
            "image_count": 0, "task_count": 1, "q_count": 3, **kw}

if "sections" not in st.session_state:
    st.session_state.sections = [
        _sec("Tujuan Praktikum",   "biasa"),
        _sec("Alat dan Bahan",     "biasa"),
        _sec("Langkah-Langkah",    "biasa"),
        _sec("Tugas",              "tugas", task_count=2),
        _sec("Test Formatif",      "formatif", q_count=3),
    ]

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("<h1>📄 Laporan Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#A0722A;margin-top:0;font-size:0.95rem;'>Laporan praktikum RPL · by Ay 🌻</p>", unsafe_allow_html=True)
st.divider()

left, right = st.columns([1.15, 0.85], gap="large")

# ══════════════════════════════════ LEFT ════════════════════════════════════
with left:

    with st.expander("📋 Data Cover", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            title       = st.text_input("Judul laporan",       value="Database MySQL")
            author      = st.text_input("Nama",                value="Ayyin Niswah Inayah")
            subject     = st.text_input("Mata pelajaran",      value="Basis Data")
        with c2:
            subtitle    = st.text_input("Subjudul / kegiatan", value="Praktikum MySQL via CMD")
            class_name  = st.text_input("Kelas",               value="XI-PPLG")
            report_date = st.text_input("Tanggal",             value=datetime.now().strftime("%d %B %Y"))
        cy, ci = st.columns(2)
        with cy:
            school_year = st.text_input("Tahun ajaran", value="2025 / 2026")
        with ci:
            cover_image = st.file_uploader("Logo / gambar cover", type=["png","jpg","jpeg"], key="cover")

    st.divider()
    st.subheader("📝 Isi Laporan")

    b1, b2 = st.columns(2)
    with b1:
        if st.button("➕ Tambah section"):
            st.session_state.sections.append(_sec("Section Baru", "biasa"))
            st.rerun()
    with b2:
        if st.button("➖ Hapus section terakhir") and len(st.session_state.sections) > 1:
            st.session_state.sections.pop()
            st.rerun()

    st.markdown("")
    sections_data = []

    for i, smeta in enumerate(st.session_state.sections):
        stype = smeta.get("type", "biasa")
        icon  = {"biasa": "📄", "tugas": "💻", "formatif": "📝"}.get(stype, "📄")

        with st.expander(f"{icon} Section {i+1} — {smeta['heading']}", expanded=(i == 0)):

            heading = st.text_input("Judul section", value=smeta["heading"], key=f"h_{i}")
            st.session_state.sections[i]["heading"] = heading

            new_type = st.radio("Tipe section", ["biasa", "tugas", "formatif"],
                index=["biasa","tugas","formatif"].index(stype),
                horizontal=True, key=f"type_{i}",
                help="biasa = teks+gambar+kode · tugas = sub-tugas berkode · formatif = soal-jawab")
            st.session_state.sections[i]["type"] = new_type

            # ── BIASA ────────────────────────────────────────────────────────
            if new_type == "biasa":
                content = st.text_area("Isi / penjelasan", value="-", height=130, key=f"content_{i}")

                col_lbl, col_lang = st.columns([2, 1])
                with col_lbl:
                    code_label = st.text_input("Label kode (kosong = skip kode)", value="",
                                               key=f"cl_{i}", placeholder="cth: Listing 1.1 – Main.java")
                with col_lang:
                    lang = st.selectbox("Bahasa", ["java","python","sql","cmd/bash","javascript","html","css","text", "cpp"], key=f"lang_{i}")
                code = st.text_area("Kode program", value="", height=110, key=f"code_{i}",
                                    placeholder="opsional, tempel kode di sini...")

                ic = smeta.get("image_count", 0)
                ia, ib_ = st.columns(2)
                with ia:
                    if st.button("🖼️ + Gambar", key=f"ai_{i}"):
                        st.session_state.sections[i]["image_count"] = ic + 1; st.rerun()
                with ib_:
                    if st.button("🗑️ - Gambar", key=f"ri_{i}") and ic > 0:
                        st.session_state.sections[i]["image_count"] = ic - 1; st.rerun()

                images = []
                for j in range(st.session_state.sections[i].get("image_count", 0)):
                    cf, cc = st.columns([1.2, 1])
                    with cf:
                        f = st.file_uploader(f"Gambar {i+1}.{j+1}", type=["png","jpg","jpeg"], key=f"img_{i}_{j}")
                    with cc:
                        cap = st.text_input("Caption", key=f"cap_{i}_{j}", placeholder=f"Gambar {i+1}.{j+1} – ...")
                    images.append({"file": f, "caption": cap})

                sections_data.append({"type": "biasa", "heading": heading, "content": content,
                                       "code": code, "code_label": code_label, "images": images})

            # ── TUGAS ────────────────────────────────────────────────────────
            elif new_type == "tugas":
                intro = st.text_area("Pengantar (opsional)", value="", height=70, key=f"intro_{i}")

                tc = smeta.get("task_count", 1)
                ta, tb_ = st.columns(2)
                with ta:
                    if st.button("➕ Sub-tugas", key=f"at_{i}"):
                        st.session_state.sections[i]["task_count"] = tc + 1; st.rerun()
                with tb_:
                    if st.button("➖ Sub-tugas", key=f"rt_{i}") and tc > 1:
                        st.session_state.sections[i]["task_count"] = tc - 1; st.rerun()

                tasks = []
                for t in range(st.session_state.sections[i].get("task_count", 1)):
                    st.markdown(f"**Sub-tugas {i+1}.{t+1}**")
                    stitle   = st.text_input("Judul sub-tugas", value=f"Tugas {t+1}", key=f"st_{i}_{t}")
                    scontent = st.text_area("Keterangan / soal", value="", height=70, key=f"ct_{i}_{t}",
                                            placeholder="Buat program yang...")
                    sl_c, sc_c = st.columns([2, 1])
                    with sl_c:
                        slabel = st.text_input("Label kode", value=f"Listing {i+1}.{t+1}", key=f"clt_{i}_{t}")
                    with sc_c:
                        slang = st.selectbox("Bahasa", ["java","python","sql","cmd/bash","javascript","html","css","text", "cpp"], key=f"lt_{i}_{t}")
                    scode = st.text_area("Kode program", value="", height=120, key=f"scode_{i}_{t}",
                                         placeholder="tempel kode...")

                    tic = smeta.get(f"tic_{t}", 0)
                    tia, tib_ = st.columns(2)
                    with tia:
                        if st.button(f"🖼️ + Gambar output {t+1}", key=f"ait_{i}_{t}"):
                            st.session_state.sections[i][f"tic_{t}"] = tic + 1; st.rerun()
                    with tib_:
                        if st.button(f"🗑️ - Gambar", key=f"rit_{i}_{t}") and tic > 0:
                            st.session_state.sections[i][f"tic_{t}"] = tic - 1; st.rerun()

                    timgs = []
                    for j in range(st.session_state.sections[i].get(f"tic_{t}", 0)):
                        tf_c, tc_c = st.columns([1.2, 1])
                        with tf_c:
                            tf_ = st.file_uploader(f"Output {t+1}.{j+1}", type=["png","jpg","jpeg"], key=f"timg_{i}_{t}_{j}")
                        with tc_c:
                            tcap = st.text_input("Caption", key=f"tcap_{i}_{t}_{j}", placeholder=f"Output Tugas {t+1}")
                        timgs.append({"file": tf_, "caption": tcap})

                    tasks.append({"subtitle": stitle, "content": scontent,
                                   "code": scode, "code_label": slabel, "images": timgs})

                sections_data.append({"type": "tugas", "heading": heading, "intro": intro, "tasks": tasks})

            # ── FORMATIF ─────────────────────────────────────────────────────
            elif new_type == "formatif":
                qc = smeta.get("q_count", 3)
                qa, qb_ = st.columns(2)
                with qa:
                    if st.button("➕ Soal", key=f"aq_{i}"):
                        st.session_state.sections[i]["q_count"] = qc + 1; st.rerun()
                with qb_:
                    if st.button("➖ Soal", key=f"rq_{i}") and qc > 1:
                        st.session_state.sections[i]["q_count"] = qc - 1; st.rerun()

                questions = []
                for q in range(st.session_state.sections[i].get("q_count", 3)):
                    st.markdown(f"**Soal {q+1}**")
                    qtext = st.text_area("Pertanyaan", value="", height=70, key=f"q_{i}_{q}",
                                         placeholder="Tulis soal di sini...")
                    atext = st.text_area("Jawaban", value="", height=90, key=f"a_{i}_{q}",
                                         placeholder="Tulis jawaban...")
                    has_img = st.checkbox(f"Ada gambar di soal {q+1}?", key=f"qchk_{i}_{q}")
                    qimgs = []
                    if has_img:
                        nqi = smeta.get(f"qic_{q}", 1)
                        qi1, qi2 = st.columns(2)
                        with qi1:
                            if st.button(f"🖼️ + Gambar soal {q+1}", key=f"aqi_{i}_{q}"):
                                st.session_state.sections[i][f"qic_{q}"] = nqi + 1; st.rerun()
                        with qi2:
                            if st.button(f"🗑️ - Gambar", key=f"rqi_{i}_{q}") and nqi > 0:
                                st.session_state.sections[i][f"qic_{q}"] = nqi - 1; st.rerun()
                        for j in range(st.session_state.sections[i].get(f"qic_{q}", 1)):
                            qf_c, qc_c = st.columns([1.2, 1])
                            with qf_c:
                                qf_ = st.file_uploader(f"Gambar soal {q+1}.{j+1}", type=["png","jpg","jpeg"], key=f"qimg_{i}_{q}_{j}")
                            with qc_c:
                                qcap = st.text_input("Caption", key=f"qcap_{i}_{q}_{j}", placeholder=f"Gambar Soal {q+1}")
                            qimgs.append({"file": qf_, "caption": qcap})

                    questions.append({"question": qtext, "answer": atext, "images": qimgs})

                sections_data.append({"type": "formatif", "heading": heading, "questions": questions})

    st.divider()
    conclusion = st.text_area("✏️ Kesimpulan", value="Tulis kesimpulan di sini...", height=130)
    references = st.text_area("📚 Daftar Pustaka", height=90,
                               value="Modul Praktikum Sekolah\nDokumentasi MySQL\nYouTube")
    st.divider()

    payload = {
        "title": title, "subtitle": subtitle,
        "author": author, "class_name": class_name,
        "subject": subject, "date": report_date,
        "school_year": school_year, "cover_image": cover_image,
        "sections": sections_data,
        "conclusion": conclusion, "references": references,
    }

    try:
        pdf_bytes = build_pdf(payload)
        safe_t = title.replace(" ", "_")[:35]
        safe_d = report_date.replace(" ", "-")
        fname  = f"Laporan_{safe_t}_{safe_d}.pdf"
        st.download_button(label="⬇️  Export PDF", data=pdf_bytes,
                           file_name=fname, mime="application/pdf",
                           use_container_width=True)
        st.success(f"✅ Siap diunduh → **{fname}**")
    except Exception as e:
        st.error(f"❌ Error: {e}")
        import traceback; st.code(traceback.format_exc())


# ══════════════════════════════════ RIGHT ═══════════════════════════════════
with right:
    st.subheader("👁️ Preview")

    st.markdown(f"""
    <div class="preview-page">
        <div style="text-align:center;font-size:11px;font-weight:700;letter-spacing:2px;color:#7A4A20;margin-bottom:4px;">LAPORAN PRAKTIKUM</div>
        <div style="text-align:center;font-size:20px;font-weight:700;color:#3B2410;margin-bottom:2px;">{title}</div>
        <div style="text-align:center;font-size:12px;font-style:italic;color:#C89B3C;margin-bottom:12px;">{subtitle}</div>
        <div style="height:2px;width:80%;background:linear-gradient(90deg,#5C3A1E,#C89B3C);margin:0 auto 4px;border-radius:2px;"></div>
        <div style="height:1px;width:55%;background:#C89B3C;margin:0 auto 16px;opacity:0.5;"></div>
        <table style="margin-left:18%;font-size:12px;color:#2C1810;border:none;background:transparent;border-collapse:collapse;">
            <tr><td>Nama</td><td style="padding-left:8px;">: {author}</td></tr>
            <tr><td>Kelas</td><td style="padding-left:8px;">: {class_name}</td></tr>
            <tr><td>Mapel</td><td style="padding-left:8px;">: {subject}</td></tr>
            <tr><td>Tanggal</td><td style="padding-left:8px;">: {report_date}</td></tr>
        </table>
        <div style="text-align:center;margin-top:16px;font-size:11px;color:#7A4A20;">{school_year}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    for i, sec in enumerate(sections_data, 1):
        stype = sec.get("type", "biasa")
        icon  = {"biasa":"📄","tugas":"💻","formatif":"📝"}.get(stype,"📄")
        st.markdown(f"**{icon} {i}. {sec['heading']}** `{stype}`")

        if stype == "biasa":
            txt = sec.get("content","")
            if txt and txt != "-":
                st.write(txt[:250] + ("..." if len(txt) > 250 else ""))
            for img in sec.get("images",[]):
                if img.get("file"):
                    st.image(img["file"], caption=img.get("caption") or None, use_container_width=True)
            if sec.get("code"):
                st.code(sec["code"][:300], language="text")

        elif stype == "tugas":
            for ti, task in enumerate(sec.get("tasks",[]), 1):
                st.markdown(f"&nbsp;&nbsp;↳ **{i}.{ti} {task.get('subtitle','')}**")
                if task.get("code"):
                    st.code(task["code"][:200], language="text")
                for img in task.get("images",[]):
                    if img.get("file"):
                        st.image(img["file"], caption=img.get("caption") or None, use_container_width=True)

        elif stype == "formatif":
            for qi, q in enumerate(sec.get("questions",[]), 1):
                qtext = q.get("question","")
                st.markdown(f"&nbsp;&nbsp;**{qi}.** {qtext[:100]}{'...' if len(qtext)>100 else ''}")

        st.markdown("---")

    if conclusion.strip() and conclusion != "Tulis kesimpulan di sini...":
        st.markdown("**✏️ Kesimpulan**")
        st.write(conclusion[:200])

st.info("💡 **biasa** = teks+gambar+kode · **tugas** = sub-tugas berkode masing-masing · **formatif** = soal+jawab±gambar · Cover tidak dihitung sebagai halaman (Hal. mulai dari hal. 2)")