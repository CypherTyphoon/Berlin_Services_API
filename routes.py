from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, func
from model import Service
from controller import engine, crawl_services, save_services  # Import Engine
from typing import Generator

router = APIRouter()

# Funktion, um eine Session zu generieren
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

# Funktion, alle Dienstleistungen zu bekommen
@router.get("/all-services", response_model=list[Service])
def get_all_services(session: Session = Depends(get_session)):
    services = session.exec(select(Service)).all()
    return services

# Funktion, Dienstleistungen nach ID
@router.get("/service/{service_id}", response_model=Service)
def get_service(service_id: int, session: Session = Depends(get_session)):
    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

# Funktion, "Wieviele Services gibt es?"
@router.get("/service-count")
def get_service_count(session: Session = Depends(get_session)):
    service_count = session.exec(select(func.count()).select_from(Service)).one()
    return {"service_count": service_count}

# Filter-Funktion für Dienstleistungen
@router.get("/online-services", response_model=list[Service])
def online_services(online: bool = None, session: Session = Depends(get_session)):
    query = select(Service)
    if online is not None:
        query = query.where(Service.digital_service == online)

    services = session.exec(query).all()
    return services

# Funktion, "Let me crawl all for you"
@router.get("/crawl-services")
def crawl_services_endpoint():
    services = crawl_services()  # Funktion in controller.py definiert
    save_services(services)  # Funktion in controller.py definiert
    return {"message": "Crawling completed", "services": services}