from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pydantic import BaseModel
import datetime

app = FastAPI()

engine = create_engine('postgresql://root:root@localhost:5432/teste')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

Base = declarative_base()


class Patient(Base):
    __tablename__ = 'patient'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    last_name = Column(String(255))
    vaccines = relationship("Vaccine", back_populates="patient", cascade="all, delete-orphan")


class Vaccine(Base):
    __tablename__ = 'vaccine'

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patient.id', ondelete='CASCADE'))
    vaccine_name = Column(String(255))
    dose_date = Column(DateTime)
    dose_number = Column(Integer)
    vaccine_type = Column(String(255))
    doses = relationship("Dose", back_populates="vaccine", cascade="all, delete-orphan")
    patient = relationship("Patient", back_populates="vaccines")


class Dose(Base):
    __tablename__ = 'dose'

    id = Column(Integer, primary_key=True)
    vaccine_id = Column(Integer, ForeignKey('vaccine.id', ondelete='CASCADE'))
    type_dose = Column(String(255))
    dose_date = Column(DateTime)
    dose_number = Column(Integer)
    application_type = Column(String(255))
    vaccine = relationship("Vaccine", back_populates="doses")


Base.metadata.create_all(bind=engine)


class PatientCreate(BaseModel):
    name: str
    last_name: str


class VaccineCreate(BaseModel):
    patient_id: int
    vaccine_name: str
    dose_date: str
    dose_number: int
    vaccine_type: str


class DoseCreate(BaseModel):
    vaccine_id: int
    type_dose: str
    dose_date: str
    dose_number: int
    application_type: str


# Endpoints
@app.post("/api/patients")
def create_patient(patient: PatientCreate):
    new_patient = Patient(name=patient.name, last_name=patient.last_name)
    session.add(new_patient)
    session.commit()
    return JSONResponse(content={"id": new_patient.id, "name": new_patient.name, "last_name": new_patient.last_name})


@app.get("/api/patients")
def read_patients():
    patients = session.query(Patient).all()
    patient_list = [{"id": p.id, "name": p.name, "last_name": p.last_name,
                     "vaccines": [{"id": v.id, "vaccine_name": v.vaccine_name} for v in p.vaccines]} for p in patients]
    return JSONResponse(content=patient_list)


@app.get("/api/patients/{patient_id}")
def read_patient(patient_id: int):
    patient = session.query(Patient).filter_by(id=patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return JSONResponse(content={"id": patient.id, "name": patient.name, "last_name": patient.last_name,
                                 "vaccines": [{"id": v.id, "vaccine_name": v.vaccine_name} for v in patient.vaccines]})


@app.put("/api/patients/{patient_id}")
def update_patient(patient_id: int, patient: PatientCreate):
    db_patient = session.query(Patient).filter_by(id=patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db_patient.name = patient.name
    db_patient.last_name = patient.last_name
    session.commit()
    return JSONResponse(content={"id": db_patient.id, "name": db_patient.name, "last_name": db_patient.last_name})


@app.delete("/api/patients/{patient_id}")
def delete_patient(patient_id: int):
    patient = session.query(Patient).filter_by(id=patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    session.delete(patient)
    session.commit()
    return JSONResponse(content={"message": f"Patient with id {patient_id} deleted successfully"})


@app.post("/api/vaccines")
def create_vaccine(vaccine: VaccineCreate):
    new_vaccine = Vaccine(
        patient_id=vaccine.patient_id,
        vaccine_name=vaccine.vaccine_name,
        dose_date=datetime.datetime.fromisoformat(vaccine.dose_date),
        dose_number=vaccine.dose_number,
        vaccine_type=vaccine.vaccine_type
    )
    session.add(new_vaccine)
    session.commit()
    return JSONResponse(content={"id": new_vaccine.id, "vaccine_name": new_vaccine.vaccine_name,
                                 "dose_date": str(new_vaccine.dose_date), "dose_number": new_vaccine.dose_number,
                                 "vaccine_type": new_vaccine.vaccine_type})


@app.get("/api/vaccines")
def read_vaccines():
    vaccines = session.query(Vaccine).all()
    vaccine_list = [
        {"id": v.id, "vaccine_name": v.vaccine_name, "dose_date": str(v.dose_date), "dose_number": v.dose_number,
         "vaccine_type": v.vaccine_type, "doses": [{"id": d.id, "type_dose": d.type_dose} for d in v.doses]} for v in
        vaccines]
    return JSONResponse(content=vaccine_list)


@app.get("/api/vaccines/{vaccine_id}")
def read_vaccine(vaccine_id: int):
    vaccine = session.query(Vaccine).filter_by(id=vaccine_id).first()
    if not vaccine:
        raise HTTPException(status_code=404, detail="Vaccine not found")
    return JSONResponse(
        content={"id": vaccine.id, "vaccine_name": vaccine.vaccine_name, "dose_date": str(vaccine.dose_date),
                 "dose_number": vaccine.dose_number, "vaccine_type": vaccine.vaccine_type,
                 "doses": [{"id": d.id, "type_dose": d.type_dose} for d in vaccine.doses]})


@app.put("/api/vaccines/{vaccine_id}")
def update_vaccine(vaccine_id: int, vaccine: VaccineCreate):
    db_vaccine = session.query(Vaccine).filter_by(id=vaccine_id).first()
    if not db_vaccine:
        raise HTTPException(status_code=404, detail="Vaccine not found")
    db_vaccine.vaccine_name = vaccine.vaccine_name
    db_vaccine.dose_date = datetime.datetime.fromisoformat(vaccine.dose_date)
    db_vaccine.dose_number = vaccine.dose_number
    db_vaccine.vaccine_type = vaccine.vaccine_type
    session.commit()
    return JSONResponse(
        content={"id": db_vaccine.id, "vaccine_name": db_vaccine.vaccine_name, "dose_date": str(db_vaccine.dose_date),
                 "dose_number": db_vaccine.dose_number, "vaccine_type": db_vaccine.vaccine_type})


@app.delete("/api/vaccines/{vaccine_id}")
def delete_vaccine(vaccine_id: int):
    vaccine = session.query(Vaccine).filter_by(id=vaccine_id).first()
    if not vaccine:
        raise HTTPException(status_code=404, detail="Vaccine not found")
    session.delete(vaccine)
    session.commit()
    return JSONResponse(content={"message": f"Vaccine with id {vaccine_id} deleted successfully"})


@app.post("/api/doses")
def create_dose(dose: DoseCreate):
    new_dose = Dose(
        vaccine_id=dose.vaccine_id,
        type_dose=dose.type_dose,
        dose_date=datetime.datetime.fromisoformat(dose.dose_date),
        dose_number=dose.dose_number,
        application_type=dose.application_type
    )
    session.add(new_dose)
    session.commit()
    return JSONResponse(
        content={"id": new_dose.id, "type_dose": new_dose.type_dose, "dose_date": str(new_dose.dose_date),
                 "dose_number": new_dose.dose_number, "application_type": new_dose.application_type})


@app.get("/api/doses")
def read_doses():
    doses = session.query(Dose).all()
    dose_list = [{"id": d.id, "type_dose": d.type_dose, "dose_date": str(d.dose_date), "dose_number": d.dose_number,
                  "application_type": d.application_type} for d in doses]
    return JSONResponse(content=dose_list)


@app.get("/api/doses/{dose_id}")
def read_dose(dose_id: int):
    dose = session.query(Dose).filter_by(id=dose_id).first()
    if not dose:
        raise HTTPException(status_code=404, detail="Dose not found")
    return JSONResponse(content={"id": dose.id, "type_dose": dose.type_dose, "dose_date": str(dose.dose_date),
                                 "dose_number": dose.dose_number, "application_type": dose.application_type})


@app.put("/api/doses/{dose_id}")
def update_dose(dose_id: int, dose: DoseCreate):
    db_dose = session.query(Dose).filter_by(id=dose_id).first()
    if not db_dose:
        raise HTTPException(status_code=404, detail="Dose not found")
    db_dose.type_dose = dose.type_dose
    db_dose.dose_date = datetime.datetime.fromisoformat(dose.dose_date)
    db_dose.dose_number = dose.dose_number
    db_dose.application_type = dose.application_type
    session.commit()
    return JSONResponse(content={"id": db_dose.id, "type_dose": db_dose.type_dose, "dose_date": str(db_dose.dose_date),
                                 "dose_number": db_dose.dose_number, "application_type": db_dose.application_type})


@app.delete("/api/doses/{dose_id}")
def delete_dose(dose_id: int):
    dose = session.query(Dose).filter_by(id=dose_id).first()
    if not dose:
        raise HTTPException(status_code=404, detail="Dose not found")
    session.delete(dose)
    session.commit()
    return JSONResponse(content={"message": f"Dose with id {dose_id} deleted successfully"})
