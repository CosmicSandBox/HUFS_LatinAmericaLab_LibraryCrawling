
import undetected_chromedriver as uc
import time
import re
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from urllib.parse import urljoin

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_browser():
    options = uc.ChromeOptions()
#    options.add_argument('--headless=new')  # 💨 headless 모드
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options)
    return driver

def wait_for_body(driver, timeout=5):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except:
        print("[⏰ 경고] 페이지 로딩 지연")

def extract_info_from_url(driver, url):
    try:
        driver.get(url)
        wait_for_body(driver)

        # 전체 HTML 소스 가져오기
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        emails = set()
        phones = set()
        addresses = set()

        # ✅ 전체 텍스트에서 추출
        text = soup.get_text(separator="\n")
        emails.update(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))
        phones.update(re.findall(r"\(?\d{2,3}\)?[\s.-]?\d{4,5}[\s.-]?\d{4}", text))
        for line in text.split("\n"):
            if any(k in line for k in ["Rua", "Av", "Endereço"]):
                addresses.add(line.strip())

        # ✅ <table> 내부 td 내용도 분석
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cols = row.find_all("td")
                for col in cols:
                    col_text = col.get_text(strip=True)
                    if "@" in col_text:
                        emails.add(col_text)
                    if re.match(r"\d{4,5}-\d{4}", col_text):
                        phones.add(col_text)
                    if any(k in col_text for k in ["Rua", "Av", "Endereço"]):
                        addresses.add(col_text)

        return {
            "url": url,
            "email": list(emails),
            "telefone": list(phones),
            "endereco": list(addresses)[:3]
        }

    except Exception as e:
        print(f"[에러] {e}")
        return {"url": url, "email": [], "telefone": [], "endereco": []}

def extract_info_deep(driver, url):
    base_info = extract_info_from_url(driver, url)

    try:
        driver.get(url)
        wait_for_body(driver)

        # 'telefones'라는 링크를 body에서 강제 수집
        all_links = driver.find_elements(By.TAG_NAME, "a")
        sub_links = []

        for link in all_links:
            href = link.get_attribute("href") or ""
            text = link.text.strip().lower()
            if "telefones" in text or "telefones" in href:
                full_url = urljoin(url, href)
                sub_links.append(full_url)

        # 중복 제거 + 최대 2개까지
        sub_links = list(dict.fromkeys(sub_links))[:2]

        for sub_url in sub_links:
            print(f"↪️ 서브 페이지: {sub_url}")
            try:
                driver.get(sub_url)
                wait_for_body(driver)

                # ✅ body + table 모두 긁기
                body_text = driver.find_element(By.TAG_NAME, "body").text
                tables = driver.find_elements(By.TAG_NAME, "table")

                combined_text = body_text + "\n".join([table.text for table in tables])

                emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", combined_text)
                phones = re.findall(r"\(?\d{2,3}\)?[\s.-]?\d{4,5}[\s.-]?\d{4}", combined_text)
                addresses = [line.strip() for line in combined_text.split("\n") if any(k in line for k in ["Rua", "Av", "Endereço"])]

                base_info["email"] += emails
                base_info["telefone"] += phones
                base_info["endereco"] += addresses[:3]

            except Exception as e:
                print(f"[서브페이지 접속 실패] {sub_url} - {e}")

        # 중복 제거
        base_info["email"] = list(set(base_info["email"]))
        base_info["telefone"] = list(set(base_info["telefone"]))
        base_info["endereco"] = list(dict.fromkeys(base_info["endereco"]))

        return base_info

    except Exception as e:
        print(f"[서브페이지 에러] {e}")
        return base_info


def print_info(university, info):
    print(f"\n● {university}")
    print(f"🔗 URL: {info.get('url', '없음')}")

    if info.get("email"):
        print("📧 Email(s):")
        for email in info["email"]:
            print(f"- {email}")
    else:
        print("📧 Email(s): (정보 없음)")

    if info.get("telefone"):
        print("📞 Telefone(s):")
        for tel in info["telefone"]:
            print(f"- {tel}")
    else:
        print("📞 Telefone(s): (정보 없음)")

    if info.get("endereco"):
        print("🏠 Endereço:")
        for end in info["endereco"]:
            print(f"- {end}")
    else:
        print("🏠 Endereço: (정보 없음)")

    print("\n" + "-" * 40)

# ✅ 실행 파트
if __name__ == "__main__":
    bibliotecas = {
    "UFBA": "https://sibi.ufba.br/",
    "UFC": "https://www.biblioteca.ufc.br/",
    "UFPB": "https://www.biblioteca.ufpb.br/",
    "UFPE": "https://www.ufpe.br/sib/",
    "UFRN": "https://sisbi.ufrn.br/",
    "UFRJ": "https://www.sibi.ufrj.br/",
    "UFF": "https://bibliotecas.uff.br/",
    "UFRGS": "https://www.ufrgs.br/bibliotecas/",
    "UFSC": "https://biblioteca.ufsc.br/",
    "UFMG": "https://www.bu.ufmg.br/",
    "UFPR": "https://www.portal.ufpr.br/biblioteca/",
    "UFES": "https://biblioteca.ufes.br/",
    "UFOP": "https://www.biblioteca.ufop.br/",
    "UFV": "https://www.ufv.br/biblioteca/",
    "UFU": "https://www.biblioteca.ufu.br/",
    "UFSCar": "https://www.biblioteca.ufscar.br/",
    "UFSM": "https://biblioteca.ufsm.br/",
    "UFMA": "https://biblioteca.ufma.br/",
    "UFPel": "https://biblioteca.ufpel.edu.br/",
    "UFPI": "https://www.ufpi.br/biblioteca",
    "UFAL": "https://www.ufal.edu.br/unidadeacademica/biblioteca",
    "UFPA": "https://www.biblioteca.ufpa.br/",
    "UFRPE": "https://www.ufrpe.br/br/biblioteca",
    "UFMT": "https://www.ufmt.br/biblioteca/",
    "UFMS": "https://biblioteca.ufms.br/",
    "UFSCAR": "https://www.biblioteca.ufscar.br/",
    "UFABC": "https://biblioteca.ufabc.edu.br/",
    "UFS": "https://bibliotecas.ufs.br/",
    "UFCA": "https://biblioteca.ufca.edu.br/",
    "UFT": "https://ww2.uft.edu.br/biblioteca",
    "UFAM": "https://biblioteca.ufam.edu.br/",
    "UFRR": "https://biblioteca.ufrr.br/",
    "UFTM": "https://www.uftm.edu.br/biblioteca",
    "UFJF": "https://www.ufjf.br/biblioteca/",
    "UFRA": "https://www.ufra.edu.br/biblioteca",
    "UFG": "https://www.bc.ufg.br/",
    "UFGD": "https://biblioteca.ufgd.edu.br/",
    "UFERSA": "https://biblioteca.ufersa.edu.br/",
    "UFOPA": "https://www.ufopa.edu.br/biblioteca/",
    "UFRB": "https://www.ufrb.edu.br/biblioteca/",
    "UFRRJ": "https://institucional.ufrrj.br/biblioteca/",
    "UFSB": "https://ufsb.edu.br/biblioteca",
    "UFVJM": "https://www.ufvjm.edu.br/biblioteca/",
    "UNIFAL": "https://www.unifal-mg.edu.br/biblioteca/",
    "UNIFEI": "https://www.unifei.edu.br/biblioteca/",
    "UNILAB": "https://biblioteca.unilab.edu.br/",
    "UNILA": "https://portal.unila.edu.br/biblioteca",
    "UNIR": "https://www.unir.br/pagina/exibir/159",
    "UNIRIO": "https://www.unirio.br/biblioteca",
    "UNIVASF": "https://portais.univasf.edu.br/sibi",
    "UTFPR": "https://biblioteca.utfpr.edu.br/",
    "UEM": "https://www.bce.uem.br/",
    "UEL": "https://www.uel.br/bc/",
    "UEPG": "https://www.uepg.br/biblioteca/",
    "UNESP": "https://www.biblioteca.unesp.br/",
    "UNICAMP": "https://www.sbu.unicamp.br/",
    "USP": "https://www.bibliotecas.usp.br/",
    "UFABC": "https://biblioteca.ufabc.edu.br/",
    "UFTPR": "https://biblioteca.uftpr.edu.br/",
    "UFMS": "https://biblioteca.ufms.br/",
    "UFMT": "https://www.ufmt.br/biblioteca/",
    "UFOPA": "https://www.ufopa.edu.br/biblioteca/",
    "UFRR": "https://biblioteca.ufrr.br/",
    "UFT": "https://ww2.uft.edu.br/biblioteca",
    "UFCA": "https://biblioteca.ufca.edu.br/",
    "UFSB": "https://ufsb.edu.br/biblioteca",
    "UFVJM": "https://www.ufvjm.edu.br/biblioteca/",
    "UNILAB": "https://biblioteca.unilab.edu.br/",
    "UNILA": "https://portal.unila.edu.br/biblioteca",
    "UNIR": "https://www.unir.br/pagina/exibir/159",
    "UNIRIO": "https://www.unirio.br/biblioteca",
    "UNIVASF": "https://portais.univasf.edu.br/sibi",
    "UTFPR": "https://biblioteca.utfpr.edu.br/",
    "UEM": "https://www.bce.uem.br/",
    "UEL": "https://www.uel.br/bc/",
    "UEPG": "https://www.uepg.br/biblioteca/",
    "UNESP": "https://www.biblioteca.unesp.br/",
    "UNICAMP": "https://www.sbu.unicamp.br/",
    "USP": "https://www.bibliotecas.usp.br/"
}
 

    driver = setup_browser()

    for sigla, url in bibliotecas.items():
        print(f"\n🔎 {sigla}")
        info = extract_info_deep(driver, url)
        if info:
            print_info(sigla, {"url": url, **info})
        else:
            print("도서관 정보를 가져올 수 없습니다.")

    driver.quit()