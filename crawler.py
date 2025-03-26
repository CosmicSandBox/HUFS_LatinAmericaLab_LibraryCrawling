import re
import time
import requests
from bs4 import BeautifulSoup
from googlesearch import search  # 구글 검색 모듈

def find_biblioteca_page(university_name):
    try:
        query = f"{university_name} biblioteca central site:.br"
        print(f"[검색 시작] {query}")
        for url in search(query, num_results=5):
            print(f"[결과 URL] {url}")
            if "biblioteca" in url:
                print(f"[도서관 URL 확정] {url}")
                return url
        print("[도서관 관련 URL 없음]")
        return None
    except Exception as e:
        print(f"[에러] 구글 검색 중 문제 발생: {e}")
        return None

def extract_info_from_page(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ')
        
        # 이메일 추출
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)

        # 전화번호 추출
        phones = re.findall(r"\(?\d{2,3}\)?[\s.-]?\d{4,5}[\s.-]?\d{4}", text)

        # 주소 추정 (간단 키워드 기반)
        address_lines = [line.strip() for line in text.split("\n") if "Rua" in line or "Av" in line or "Endereço" in line]

        return {
            "url": url,
            "email": list(set(emails)),
            "telefone": list(set(phones)),
            "endereco": address_lines[:3]  # 상위 3개 추정 주소
        }
    except Exception as e:
        print(f"에러 발생: {e}")
        return None

# 테스트용 대학 리스트
universidades = [
    "Universidade de Brasília",
    "Universidade Federal do Acre",
    "Universidade Federal de Alagoas",
    "Universidade Federal do Amapá",
    "Universidade Federal do Amazonas",
    "Universidade Federal do Cariri",
    "Universidade Federal do Ceará",
    "Universidade Federal do Espírito Santo",
    "Universidade Federal do Maranhão",
    "Universidade Federal de Mato Grosso",
    "Universidade Federal de Mato Grosso do Sul",
    "Universidade Federal de Goiás",
    "Universidade Federal de Catalão",
    "Universidade Federal de Jataí",
    "Universidade Federal de Roraima",
    "Universidade Federal do Pará",
    "Universidade Federal do Sul e Sudeste do Pará",
    "Universidade Federal do Oeste do Pará",
    "Universidade Federal do Tocantins",
    "Universidade Federal do Norte do Tocantins",
    "Universidade Federal da Bahia",
    "Universidade Federal do Oeste da Bahia",
    "Universidade Federal do Sul da Bahia",
    "Universidade Federal do Recôncavo da Bahia",
    "Universidade Federal do Vale do São Francisco",
    "Universidade Federal do Piauí",
    "Universidade Federal da Paraíba",
    "Universidade Federal de Campina Grande",
    "Universidade Federal de Pernambuco",
    "Universidade Federal do Agreste de Pernambuco",
    "Universidade Federal Rural de Pernambuco",
    "Universidade Federal do Rio Grande do Norte",
    "Universidade Federal Rural do Semi-Árido",
    "Universidade Federal de Sergipe",
    "Universidade Federal do Rio de Janeiro",
    "Universidade Federal Fluminense",
    "Universidade Federal Rural do Rio de Janeiro",
    "Universidade Federal do Estado do Rio de Janeiro",
    "Universidade Federal de São Paulo",
    "Universidade Federal do ABC",
    "Universidade Federal de São Carlos",
    "Universidade Federal de Itajubá",
    "Universidade Federal de Lavras",
    "Universidade Federal de Minas Gerais",
    "Universidade Federal de Juiz de Fora",
    "Universidade Federal de São João del-Rei",
    "Universidade Federal de Alfenas",
    "Universidade Federal de Ouro Preto",
    "Universidade Federal dos Vales do Jequitinhonha e Mucuri",
    "Universidade Federal do Triângulo Mineiro",
    "Universidade Federal de Uberlândia",
    "Universidade Federal de Viçosa",
    "Universidade Federal do Paraná",
    "Universidade Tecnológica Federal do Paraná",
    "Universidade Federal da Integração Latino-Americana",
    "Universidade Federal do Rio Grande do Sul",
    "Universidade Federal de Ciências da Saúde de Porto Alegre",
    "Universidade Federal de Santa Maria",
    "Universidade Federal de Pelotas",
    "Universidade Federal da Fronteira Sul",
    "Universidade Federal de Santa Catarina",
    "Universidade Federal do Pampa",
    "Universidade Federal do Delta do Parnaíba",
    "Universidade Federal do Norte do Paraná",
    "Universidade Federal de Itajubá - Campus Itabira",
    "Universidade Federal de Itajubá - Campus Itajubá",
    "Universidade Federal do Oeste da Bahia - Campus Barreiras",
    "Universidade Federal do Oeste da Bahia - Campus Barra",
    "Universidade Federal do Oeste da Bahia - Campus Bom Jesus da Lapa",
    "Universidade Federal do Recôncavo da Bahia - Campus Cruz das Almas",
    "Universidade Federal do Sul e Sudeste do Pará - Campus Marabá",
    "Universidade Federal do Sul e Sudeste do Pará - Campus Xinguara",
    "Universidade Federal do Amazonas - Campus Itacoatiara",
    "Universidade Federal do Amazonas - Campus Humaitá",
    "Universidade Federal do Amazonas - Campus Parintins",
    "Universidade Federal de Rondonópolis",
    "Universidade Federal do Agreste de Pernambuco - Campus Garanhuns",
    "Universidade Federal do Semiárido - Campus Mossoró",
    "Universidade Federal de Campina Grande - Campus Cajazeiras",
    "Universidade Federal do Cariri - Campus Juazeiro do Norte",
    "Universidade Federal de Lavras - Campus São Sebastião do Paraíso",
    "Universidade Federal de São João del-Rei - Campus Alto Paraopeba",
    "Universidade Federal de São João del-Rei - Campus Dom Bosco",
    "Universidade Federal do Triângulo Mineiro - Campus Uberaba",
    "Universidade Federal do Triângulo Mineiro - Campus Iturama",
    "Universidade Federal de São Paulo - Campus Guarulhos",
    "Universidade Federal de São Paulo - Campus Diadema",
    "Universidade Federal de São Paulo - Campus Santos",
    "Universidade Federal do ABC - Campus Santo André",
    "Universidade Federal do ABC - Campus São Bernardo do Campo"
]

for uni in universidades:
    print(f"\n🔎 {uni}")
    page = find_biblioteca_page(uni)
    if page:
        info = extract_info_from_page(page)
        print_info(uni, info)
    else:
        print("도서관 페이지를 찾을 수 없습니다.")

def print_info(uni, info):
    print(f"\n● {uni}")
    print(f"🔗 URL: {info.get('url', '없음')}")
    
    emails = info.get('email', [])
    if emails:
        print("📧 Email(s):")
        for email in emails:
            print(f"- {email}")
    else:
        print("📧 Email(s): (정보 없음)")
        
    phones = info.get('telefone', [])
    if phones:
        print("📞 Telefone(s):")
        for phone in phones:
            print(f"- {phone}")
    else:
        print("📞 Telefone(s): (정보 없음)")

    enderecos = info.get('endereco', [])
    if enderecos:
        print("🏠 Endereço:")
        for line in enderecos:
            print(f"- {line}")
    else:
        print("🏠 Endereço: (정보 없음)")

    print("\n" + "-" * 40)