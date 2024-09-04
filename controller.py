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

# Scrapper / Crawl (Crawl me in the dark)
def crawl_services():
    response = requests.get(f"{BASE_URL}/dienstleistungen/")
    soup = BeautifulSoup(response.content, "html.parser")

    services = []

    for service in soup.select("div > div:nth-of-type(3) > div:first-of-type a.your-service-link-class"):
        title = service.text.strip()
        link = service["href"]
        service_id = link.split("/")[-2]  # Extrahiere die ID aus dem Link

        service_response = requests.get(f"{BASE_URL}{link}")
        service_soup = BeautifulSoup(service_response.content, "html.parser")

        responsible_office = service_soup.select_one("a.your-office-link-class").text.strip() if service_soup.select_one("a.your-office-link-class") else None
        digital_service = "Ja" in service_soup.select_one("span.your-digital-service-class").text.strip()

        # Erstellen des Service-Datensatzes
        services.append({
            "id": service_id,
            "name": title,
            "responsible_office": responsible_office,
            "digital_service": digital_service,
        })

    logger.info(f"Service gefunden: {title} mit ID: {service_id}")

    return services