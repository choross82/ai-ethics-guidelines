#!/usr/bin/env python3
"""
AI 윤리 가이드라인 모음 — 데이터 빌드 스크립트

각 폴더의 요약.md + 원본 파일을 스캔하여 data.js를 생성한다.
data.js는 index.html이 로드하는 단일 자산이다.
"""
from __future__ import annotations
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).parent
NATIONAL_DIR = ROOT / "국가기관별 AI 윤리 가이드라인"
RELIGIOUS_DIR = ROOT / "교단별 AI 가이드라인"

# ──────────────────────────────────────────────────────────────────────────────
# 메타데이터 매니페스트 — 폴더 번호별 외부 URL/카테고리/태그/짧은 설명
# 폴더명·파일 스캔으로 알 수 없는 정보들을 여기서 보충한다.
# ──────────────────────────────────────────────────────────────────────────────

NATIONAL_META = {
    "01": {
        "group": "국제기구", "country": "국제", "year": 2021,
        "officialUrl": "https://www.unesco.de/assets/dokumente/Deutsche_UNESCO-Kommission/02_Publikationen/Publikation_UNESCO_Recommendation_on_the_Ethics_of_Artificial_Intelligence.pdf",
        "tags": ["인권", "거버넌스", "포용성", "글로벌"],
        "shortDesc": "193개 UNESCO 회원국이 채택한 최초의 글로벌 AI 윤리 국제규범."
    },
    "02": {
        "group": "국제기구", "country": "국제", "year": 2019,
        "officialUrl": "https://oecd.ai/en/assets/files/OECD-LEGAL-0449-en.pdf",
        "tags": ["원칙", "신뢰가능한AI", "정부간"],
        "shortDesc": "정부 간 최초의 AI 원칙. G20·EU 정책의 기반이 됨."
    },
    "03": {
        "group": "유럽연합", "country": "EU", "year": 2024,
        "officialUrl": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689",
        "tags": ["법률", "위험기반", "규제"],
        "shortDesc": "세계 최초의 포괄적 AI 규제 법률, 위험기반 4단계 분류."
    },
    "04": {
        "group": "미국", "country": "미국", "year": 2023,
        "officialUrl": "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf",
        "tags": ["위험관리", "프레임워크", "Govern-Map-Measure-Manage"],
        "shortDesc": "AI 위험 거버넌스의 사실상 표준이 된 미국 NIST 프레임워크."
    },
    "05": {
        "group": "미국", "country": "미국", "year": 2022,
        "officialUrl": "https://web.archive.org/web/2024/https://www.whitehouse.gov/wp-content/uploads/2022/10/Blueprint-for-an-AI-Bill-of-Rights.pdf",
        "tags": ["권리", "차별금지", "프라이버시"],
        "shortDesc": "미국형 AI 시민권 원칙 5개를 제시한 백악관 OSTP 청사진."
    },
    "06": {
        "group": "미국", "country": "미국", "year": 2023,
        "officialUrl": "https://www.govinfo.gov/content/pkg/FR-2023-11-01/pdf/2023-24283.pdf",
        "tags": ["행정명령", "안전성", "프론티어AI"],
        "shortDesc": "미국 역사상 가장 포괄적인 AI 행정명령(2025년 폐지됨)."
    },
    "07": {
        "group": "영국", "country": "영국", "year": 2023,
        "officialUrl": "https://www.gov.uk/government/publications/ai-safety-summit-2023-the-bletchley-declaration/the-bletchley-declaration-by-countries-attending-the-ai-safety-summit-1-2-november-2023",
        "tags": ["프론티어AI", "안전성", "국제선언"],
        "shortDesc": "프런티어 AI 안전성에 관한 최초의 국제 정치 선언(28개국+EU)."
    },
    "08": {
        "group": "G7", "country": "다자", "year": 2023,
        "officialUrl": "https://ec.europa.eu/newsroom/dae/redirection/document/99641",
        "tags": ["행동강령", "기업자율", "첨단AI"],
        "shortDesc": "첨단 AI 개발자를 위한 G7 자발적 행동 강령."
    },
    "09": {
        "group": "한국", "country": "한국", "year": 2020,
        "officialUrl": "https://ai.kisdi.re.kr/aieth/cmmn/file/fileDown.do?menuNo=400&atchFileId=3fd9baa666514803b5e6132a96783ec3&fileSn=2&bbsId=",
        "tags": ["인간중심", "원칙", "한국"],
        "shortDesc": "한국 정부의 첫 AI 윤리기준, 3대 원칙 10대 핵심요건."
    },
    "10": {
        "group": "한국", "country": "한국", "year": 2025,
        "officialUrl": "https://www.privacy.go.kr/cmm/fms/FileDown.do?atchFileId=ATCH_000000000919989&fileSn=1",
        "tags": ["생성형AI", "개인정보", "한국"],
        "shortDesc": "생성형 AI 개발·활용 단계별 개인정보 처리 기준."
    },
    "11": {
        "group": "중국", "country": "중국", "year": 2021,
        "officialUrl": "https://www.most.gov.cn/kjbgz/202109/t20210926_177063.html",
        "tags": ["윤리규범", "신세대AI", "중국"],
        "shortDesc": "중국 과기부의 6대 기본 윤리 요구를 담은 신세대 AI 윤리규범."
    },
    "12": {
        "group": "싱가포르", "country": "싱가포르", "year": 2024,
        "officialUrl": "https://aiverifyfoundation.sg/wp-content/uploads/2024/05/Model-AI-Governance-Framework-for-Generative-AI-May-2024-1-1.pdf",
        "tags": ["생성형AI", "거버넌스", "프레임워크"],
        "shortDesc": "세계 최초의 GenAI 전용 정부 거버넌스 프레임워크."
    },
    "13": {
        "group": "비정부", "country": "다자", "year": 2017,
        "officialUrl": "https://futureoflife.org/open-letter/ai-principles/",
        "tags": ["원칙", "장기리스크", "FLI"],
        "shortDesc": "AI 연구·윤리·장기 이슈를 망라한 23개 원칙. 후속 가이드라인의 원형."
    },
    "14": {
        "group": "비정부", "country": "캐나다", "year": 2018,
        "officialUrl": "https://declarationmontreal-iaresponsable.com/wp-content/uploads/2023/04/UdeM_Decl_IA-Resp_LA-Declaration-ENG_WEB_09-07-19.pdf",
        "tags": ["선언", "10대원칙", "시민참여"],
        "shortDesc": "시민 참여형 숙의를 통한 책임 있는 AI 10대 원칙."
    },
    "15": {
        "group": "국제기구", "country": "국제", "year": 2021,
        "officialUrl": "https://iris.who.int/server/api/core/bitstreams/f780d926-4ae3-42ce-a6d6-e898a5562621/content",
        "tags": ["보건", "디지털헬스", "6원칙"],
        "shortDesc": "WHO 6대 보건 AI 윤리 원칙."
    },
    "16": {
        "group": "국제기구", "country": "유럽", "year": 2024,
        "officialUrl": "https://rm.coe.int/1680afae3c",
        "tags": ["조약", "인권", "법적구속력"],
        "shortDesc": "세계 최초의 법적 구속력 있는 국제 AI 조약."
    },
    "17": {
        "group": "일본", "country": "일본", "year": 2024,
        "officialUrl": "https://www.soumu.go.jp/main_content/000943079.pdf",
        "tags": ["사업자", "가이드라인", "통합"],
        "shortDesc": "일본 AI 사업자 대상 통합 가이드라인 v1.0."
    },
    "18": {
        "group": "다자", "country": "다자", "year": 2019,
        "officialUrl": "https://wp.oecd.ai/app/uploads/2021/06/G20-AI-Principles.pdf",
        "tags": ["원칙", "G20", "OECD확장"],
        "shortDesc": "OECD 원칙을 G20 차원으로 확장한 첫 합의."
    },
    "19": {
        "group": "비정부", "country": "다자", "year": 2019,
        "officialUrl": "https://algorithmwatch.org/de/wp-content/uploads/2019/03/IEEE-EAD1e.pdf",
        "tags": ["엔지니어링", "설계지침", "표준화"],
        "shortDesc": "엔지니어링 표준화 단체의 가장 방대한 AI 윤리 설계 지침(294페이지)."
    },
}

RELIGIOUS_META = {
    "01": {
        "group": "가톨릭", "tradition": "가톨릭", "year": 2020,
        "officialUrl": "https://www.romecall.org/wp-content/uploads/2022/03/RomeCall_Paper_web.pdf",
        "tags": ["6원칙", "범종교", "Algor-Ethics"],
        "shortDesc": "가톨릭의 첫 글로벌 AI 윤리 호소(MS·IBM·FAO 공동 서명)."
    },
    "02": {
        "group": "가톨릭", "tradition": "가톨릭", "year": 2024,
        "officialUrl": "https://www.vatican.va/content/francesco/en/messages/peace/documents/20231208-messaggio-57giornatamondiale-pace2024.html",
        "tags": ["교황메시지", "평화", "프란치스코"],
        "shortDesc": "교황의 첫 본격 AI 평화 메시지(2024년 1월 1일)."
    },
    "03": {
        "group": "가톨릭", "tradition": "가톨릭", "year": 2024,
        "officialUrl": "https://www.vatican.va/content/francesco/en/messages/communications/documents/20240124-messaggio-comunicazioni-sociali.html",
        "tags": ["교황메시지", "미디어", "프란치스코"],
        "shortDesc": "미디어·커뮤니케이션 영역의 AI 사용에 대한 교황 메시지."
    },
    "04": {
        "group": "가톨릭", "tradition": "가톨릭", "year": 2024,
        "officialUrl": "https://www.vatican.va/content/francesco/en/speeches/2024/june/documents/20240614-g7-intelligenza-artificiale.html",
        "tags": ["교황연설", "G7", "자율살상무기"],
        "shortDesc": "교황 사상 최초의 G7 정상회의 연설. 자율살상무기 금지 촉구."
    },
    "05": {
        "group": "가톨릭", "tradition": "가톨릭", "year": 2025,
        "officialUrl": "https://www.vatican.va/roman_curia/congregations/cfaith/documents/rc_ddf_doc_20250128_antiqua-et-nova_en.html",
        "tags": ["바티칸문서", "인간학", "교리청"],
        "shortDesc": "AI와 인간 지능의 관계에 관한 바티칸의 권위 있는 노트."
    },
    "06": {
        "group": "가톨릭", "tradition": "가톨릭", "year": 2025,
        "officialUrl": "https://www.vatican.va/content/francesco/en/messages/pont-messages/2025/documents/20250207-messaggio-summit-parigi-ia.html",
        "tags": ["교황메시지", "파리정상회의", "프란치스코"],
        "shortDesc": "프란치스코 교황의 마지막 공식 AI 메시지(서거 전)."
    },
    "07": {
        "group": "가톨릭", "tradition": "가톨릭", "year": 2025,
        "officialUrl": "https://www.usccb.org/resources/joint-letter-artificial-intelligence-principles-and-priorities",
        "tags": ["미국주교", "공동서한", "정책"],
        "shortDesc": "미국 주교들이 의회에 제출한 첫 공식 AI 정책 서한."
    },
    "08": {
        "group": "가톨릭", "tradition": "가톨릭", "year": 2025,
        "officialUrl": "https://www.vatican.va/content/leo-xiv/en/speeches/2025/december/documents/20251205-conferenza.html",
        "tags": ["교황연설", "레오14세", "공동의집"],
        "shortDesc": "레오 14세의 첫 본격 AI 연설."
    },
    "09": {
        "group": "에큐메니컬", "tradition": "에큐메니컬", "year": 2023,
        "officialUrl": "https://www.oikoumene.org/resources/documents/statement-on-the-unregulated-development-of-artificial-intelligence",
        "tags": ["WCC", "성명", "거버넌스촉구"],
        "shortDesc": "WCC의 첫 공식 AI 성명, 인권 기반 거버넌스 촉구."
    },
    "10": {
        "group": "에큐메니컬", "tradition": "에큐메니컬", "year": 2025,
        "officialUrl": "https://www.oikoumene.org/sites/default/files/2025-09/COM%2006%20Use%20of%20Artificial%20Intelligence%20in%20WCC%20Communications.pdf",
        "tags": ["WCC", "운영정책", "후속"],
        "shortDesc": "WCC 자체 커뮤니케이션의 AI 사용 정책."
    },
    "11": {
        "group": "에큐메니컬", "tradition": "에큐메니컬", "year": 2025,
        "officialUrl": "https://www.oikoumene.org/news/faith-communities-issue-urgent-call-to-transform-ai-from-profit-to-life",
        "tags": ["6개교단", "생명경제", "다자공동"],
        "shortDesc": "6개 글로벌 교회 협의체가 공동 발표한 AI·생명경제 신학 선언."
    },
    "12": {
        "group": "장로교", "tradition": "장로교", "year": 2023,
        "officialUrl": "https://pcusa.org/about-pcusa/agencies-entities/life-witness/ministry-areas/innovation/ai-and-church",
        "tags": ["PCUSA", "가이드라인", "미국장로교"],
        "shortDesc": "미국 주류 장로교의 첫 AI 가이드라인 문서."
    },
    "13": {
        "group": "장로교", "tradition": "장로교", "year": 2025,
        "officialUrl": "https://pcusa.org/news-storytelling/news/2025/9/2/charting-faithful-future-artificial-intelligence",
        "tags": ["PCUSA", "총회결의후속", "보고"],
        "shortDesc": "2024 PCUSA 총회 결의에 따른 공식 후속 작업 보고."
    },
    "14": {
        "group": "장로교", "tradition": "장로교", "year": 2023,
        "officialUrl": "",
        "tags": ["예장통합", "한국", "목회자윤리"],
        "shortDesc": "한국 주요 교단 차원의 첫 AI 목회 윤리 선언(제108회기 정책기획및기구개혁위원회)."
    },
    "15": {
        "group": "성공회", "tradition": "성공회", "year": 2024,
        "officialUrl": "https://www.churchofengland.org/sites/default/files/2025-01/eiag-artificial-intelligence-advice-2024.pdf",
        "tags": ["영국성공회", "EIAG", "투자윤리"],
        "shortDesc": "교회 자산의 AI 기업 투자 윤리 기준."
    },
    "16": {
        "group": "성공회", "tradition": "성공회", "year": 2024,
        "officialUrl": "https://www.churchofengland.org/media/press-releases/synod-affirms-work-key-human-dignity-and-purpose-face-ai-revolution",
        "tags": ["영국성공회", "총회결의", "인간존엄"],
        "shortDesc": "영국성공회 총회의 AI·인간 존엄 결의(Rome Call 지지)."
    },
    "17": {
        "group": "성공회", "tradition": "성공회", "year": 2024,
        "officialUrl": "https://www.episcopalarchives.org/files/gc_resolutions/2024-D020.pdf",
        "tags": ["미국성공회", "결의안", "태스크포스"],
        "shortDesc": "미국성공회 차원의 AI 태스크포스 신설 결의."
    },
    "18": {
        "group": "성공회", "tradition": "성공회", "year": 2025,
        "officialUrl": "https://gs2025.anglican.ca/resolutions/c005/",
        "tags": ["캐나다성공회", "결의안", "태스크포스"],
        "shortDesc": "캐나다 교단 차원의 첫 AI 결의안, 전국 AI 윤리 태스크포스 설치."
    },
    "19": {
        "group": "복음주의", "tradition": "개신교(복음주의)", "year": 2019,
        "officialUrl": "https://erlc.com/policy-content/artificial-intelligence-an-evangelical-statement-of-principles/",
        "tags": ["남침례교", "ERLC", "원칙성명"],
        "shortDesc": "미국 복음주의권의 첫 본격 AI 윤리 원칙 성명."
    },
    "20": {
        "group": "복음주의", "tradition": "개신교(복음주의)", "year": 2023,
        "officialUrl": "https://www.sbc.net/resource-library/resolutions/on-artificial-intelligence-and-emerging-technologies/",
        "tags": ["남침례교", "SBC", "결의안"],
        "shortDesc": "미국 최대 개신교 교단의 공식 AI 결의안."
    },
    "21": {
        "group": "복음주의", "tradition": "개신교(복음주의)", "year": 2025,
        "officialUrl": "https://erlc.com/research/the-work-of-our-hands-christian-ministry-in-the-age-of-artificial-intelligence/",
        "tags": ["남침례교", "ERLC", "목회현장"],
        "shortDesc": "복음주의 목회 현장의 AI 활용에 관한 본격 가이드."
    },
    "22": {
        "group": "복음주의", "tradition": "개신교(복음주의)", "year": 2024,
        "officialUrl": "https://lausanne.org/statement/the-seoul-statement",
        "tags": ["로잔운동", "서울선언", "글로벌"],
        "shortDesc": "글로벌 복음주의 대회의 통합 선언(VII장 기술·AI 챕터 포함)."
    },
    "23": {
        "group": "복음주의", "tradition": "개신교(복음주의)", "year": 2024,
        "officialUrl": "https://lausanne.org/report/human/artificial-intelligence",
        "tags": ["로잔운동", "선교", "AI보고서"],
        "shortDesc": "복음주의 선교적 관점의 AI 분석 공식 보고서."
    },
    "24": {
        "group": "장로교", "tradition": "장로교", "year": 2022,
        "officialUrl": "https://www.churchofscotland.org.uk/__data/assets/pdf_file/0011/79760/Artificial-Intelligence-SRT-report-22.2.21WEB.pdf",
        "tags": ["스코틀랜드교회", "SRT", "과학종교"],
        "shortDesc": "스코틀랜드교회 과학종교 위원회의 공식 AI 보고서."
    },
    "25": {
        "group": "유대교", "tradition": "유대교", "year": 2019,
        "officialUrl": "https://www.rabbinicalassembly.org/sites/default/files/nevins_ai_moral_machines_and_halakha-final_1.pdf",
        "tags": ["유대교", "할라카", "보수파"],
        "shortDesc": "보수파 유대교의 유일한 공식 AI 할라카 교시문."
    },
    "26": {
        "group": "초종교", "tradition": "초종교", "year": 2023,
        "officialUrl": "https://www.romecall.org/ai-ethics-an-abrahamic-commitment-to-the-rome-call-2/",
        "tags": ["로마콜", "아브라함", "3종교"],
        "shortDesc": "세 아브라함 종교(가톨릭·유대교·이슬람)의 첫 공식 AI 윤리 공동 채택."
    },
    "27": {
        "group": "초종교", "tradition": "초종교", "year": 2024,
        "officialUrl": "https://www.romecall.org/ai-ethics-for-peace-world-religions-commit-to-the-rome-call/",
        "tags": ["로마콜", "히로시마", "다종교"],
        "shortDesc": "불교·힌두교·조로아스터교·바하이교까지 합류한 세계 종교 다종교 AI 윤리 합의."
    },
    "28": {
        "group": "초종교", "tradition": "초종교", "year": 2024,
        "officialUrl": "https://www.romecall.org/wp-content/uploads/2024/07/Hiroshima-Addendum-2.pdf",
        "tags": ["로마콜", "생성형AI", "다종교"],
        "shortDesc": "Rome Call을 생성형 AI 시대에 맞춰 업데이트한 다종교 부속서."
    },
}


def parse_summary(md_path: Path) -> dict:
    """요약.md에서 제목 + 기본정보 + 본문 분리."""
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # 첫 # 헤더를 제목으로
    title = ""
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    # 기본 정보 섹션 파싱 (## 기본 정보 ~ 다음 ## 까지)
    basic = {}
    in_basic = False
    for line in lines:
        if line.startswith("## 기본 정보"):
            in_basic = True
            continue
        if in_basic and line.startswith("## "):
            break
        if in_basic:
            m = re.match(r"^- \*\*(.+?)\*\*[:：]\s*(.+)$", line.strip())
            if m:
                basic[m.group(1).strip()] = m.group(2).strip()

    return {"title": title, "basic": basic, "raw": text}


def find_doc_file(folder: Path) -> tuple[str, str, int]:
    """폴더 내에서 PDF/HTML 원본 파일을 찾아 (파일명, 형식, 크기) 반환."""
    candidates = []
    for f in folder.iterdir():
        if f.is_file() and f.name != "요약.md" and not f.name.startswith("."):
            candidates.append(f)
    if not candidates:
        return ("", "", 0)
    # PDF 우선
    pdfs = [f for f in candidates if f.suffix.lower() == ".pdf"]
    htmls = [f for f in candidates if f.suffix.lower() == ".html"]
    chosen = pdfs[0] if pdfs else (htmls[0] if htmls else candidates[0])
    fmt = chosen.suffix[1:].upper()
    return (chosen.name, fmt, chosen.stat().st_size)


def build_entry(folder: Path, category: str, meta_map: dict) -> dict | None:
    """단일 폴더 → 데이터 엔트리."""
    name = folder.name
    m = re.match(r"^(\d+)_", name)
    if not m:
        return None
    num = m.group(1)
    if num not in meta_map:
        return None
    meta = meta_map[num]

    summary_path = folder / "요약.md"
    if not summary_path.exists():
        return None
    parsed = parse_summary(summary_path)

    doc_file, fmt, size = find_doc_file(folder)
    rel_folder = folder.relative_to(ROOT).as_posix()
    local_path = f"{rel_folder}/{doc_file}" if doc_file else ""

    prefix = "n" if category == "national" else "r"
    return {
        "id": f"{prefix}{num}",
        "category": category,
        "number": num,
        "title": parsed["title"] or name,
        "issuer": parsed["basic"].get("발행 주체") or parsed["basic"].get("발행 기관", ""),
        "publishDate": parsed["basic"].get("발행일") or parsed["basic"].get("발행 연도", ""),
        "docType": parsed["basic"].get("문서 유형", ""),
        "language": parsed["basic"].get("원본 언어", ""),
        "year": meta.get("year"),
        "group": meta["group"],
        "country": meta.get("country", ""),
        "tradition": meta.get("tradition", ""),
        "tags": meta["tags"],
        "shortDesc": meta["shortDesc"],
        "format": fmt,
        "fileSize": size,
        "folderPath": rel_folder,
        "documentFile": doc_file,
        "localPath": local_path,
        "officialUrl": meta.get("officialUrl", ""),
        "summary": parsed["raw"],
    }


def main():
    entries = []
    # 국가기관별
    for folder in sorted(NATIONAL_DIR.iterdir()):
        if folder.is_dir():
            e = build_entry(folder, "national", NATIONAL_META)
            if e:
                entries.append(e)
    # 교단별
    for folder in sorted(RELIGIOUS_DIR.iterdir()):
        if folder.is_dir():
            e = build_entry(folder, "religious", RELIGIOUS_META)
            if e:
                entries.append(e)

    # data.js 출력
    out = ROOT / "data.js"
    payload = json.dumps(entries, ensure_ascii=False, indent=2)
    out.write_text(f"// AUTO-GENERATED by build_data.py — do not edit by hand.\nwindow.GUIDELINES = {payload};\n", encoding="utf-8")

    print(f"✅ {len(entries)} entries → {out}")
    nat = sum(1 for e in entries if e["category"] == "national")
    rel = sum(1 for e in entries if e["category"] == "religious")
    print(f"   국가기관별: {nat}, 교단별: {rel}")


if __name__ == "__main__":
    main()
