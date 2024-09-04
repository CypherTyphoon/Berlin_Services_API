from fastapi import FastAPI
from routes import router
from controller import crawl_services, save_services, engine  # Import engine
from sqlmodel import SQLModel, Session, select  # Import Session und select
import logging  # Import für logger-Modul
from model import Service  # Import Service-Modell

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Erstelle die Tabellen bei App-Start
SQLModel.metadata.create_all(engine)

# Registriere die Routen
app.include_router(router)

# Optionale Datenbankbefüllung bei App-Start
if __name__ == "__main__":
    crawl_data = True
    if crawl_data:
        # Daten scrapen / crawlen
        services = crawl_services()

        # Überprüfe, ob das Scraping erfolgreich war
        if services:
            logger.info(f"Es wurden {len(services)} Services gescrapt.")
        else:
            logger.warning("Keine Services wurden gescrapt.")

        # Gescrapete Daten speichern
        save_services(services)

        # Überprüfen, ob Daten in der Datenbank vorhanden sind
        with Session(engine) as session:
            service_count = session.exec(select(Service)).count()
            logger.info(f"Es wurden {service_count} Services in der Datenbank gespeichert.")
            if service_count == 0:
                logger.warning("Es wurden keine Services in die Datenbank geschrieben.")