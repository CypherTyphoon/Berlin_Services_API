# Importe, wir brauchen mehr Importe
import logging
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session, create_engine
from model import Service

# Anfang "In the beginning, it was nothing"
BASE_URL = "https://service.berlin.de"

DATABASE_URL = "sqlite:///./database.db"  # Beispiel für SQLite-Datenbank
engine = create_engine(DATABASE_URL)

# Logging einrichten
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Speichern (Save the world, to get higher level)
def save_services(services):
    with Session(engine) as session:
        try:
            for service_data in services:
                service = Service(**service_data)
                session.add(service)
            session.commit()
            logger.info(f"{len(services)} Services erfolgreich gespeichert.")
        except Exception as e:
            session.rollback()  # Rollback bei Fehlern
            logger.error(f"Fehler beim Speichern der Services: {e}")
        finally:
            session.close()

# Prüfung von Online-Abwicklung
def check_online_abwicklung(service_link):
    check_online_url = f"{service_link}"
    response = requests.get(check_online_url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    digital_service = bool(soup.find('h2', id='Online-Abwicklung'))
    return digital_service

# Scrapper / Crawl (Crawl me in the dark)
def crawl_services():
    response = requests.get(f"{BASE_URL}/dienstleistungen/")
    soup = BeautifulSoup(response.content, "html.parser")

    services = []

    for service in soup.select("#layout-grid__area--maincontent .azlist-letter + ul li a"):
        title = service.text.strip()
        service_link = service["href"]
        service_id = service_link.split("/")[-2]  # Extract the ID from the link
        
        # Verwenden der Funktion zur Überprüfung der Online-Abwicklung
        digital_service = check_online_abwicklung(service_link)
        
        services.append({
            "id": service_id,
            "name": title,
            "link": service_link,
            "digital_service": digital_service,
        })

        logger.info(f"Service gefunden: {title} mit ID: {service_id}, Online-Abwicklung: {digital_service}") #

    return services
