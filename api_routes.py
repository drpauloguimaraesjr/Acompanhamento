"""Rotas de API para o sistema médico.

O módulo implementa uma API simples para gerenciar pacientes e consultas
utilizando armazenamento em memória. O objetivo é oferecer uma base
estável para desenvolvimento local e testes automatizados sem depender
imediatamente de um banco de dados real.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["api"])


class PatientBase(BaseModel):
    """Campos compartilhados para pacientes."""

    nome: str = Field(..., min_length=3, max_length=100)
    telefone: str = Field(..., min_length=8, max_length=20)
    data_nascimento: date = Field(..., description="Data de nascimento do paciente")


class PatientCreate(PatientBase):
    """Modelo de entrada para criação de pacientes."""

    pass


class Patient(PatientBase):
    """Modelo de paciente retornado pela API."""

    id: UUID


class AppointmentBase(BaseModel):
    """Campos compartilhados para consultas médicas."""

    paciente_id: UUID
    data: datetime
    descricao: str = Field(..., min_length=3, max_length=255)


class AppointmentCreate(AppointmentBase):
    """Modelo de entrada para criação de consultas."""

    pass


class Appointment(AppointmentBase):
    """Modelo retornado pela API para consultas."""

    id: UUID


_patients: Dict[UUID, Patient] = {}
_appointments: Dict[UUID, Appointment] = {}


@router.get("/health", tags=["health"])
def healthcheck() -> Dict[str, str]:
    """Endpoint simples de verificação de disponibilidade."""

    return {"status": "ok"}


@router.get("/pacientes", response_model=List[Patient])
def listar_pacientes() -> List[Patient]:
    """Retorna todos os pacientes cadastrados."""

    return list(_patients.values())


@router.post(
    "/pacientes",
    response_model=Patient,
    status_code=status.HTTP_201_CREATED,
)
def criar_paciente(payload: PatientCreate) -> Patient:
    """Cria um novo paciente na base em memória."""

    novo_paciente = Patient(id=uuid4(), **payload.model_dump())
    _patients[novo_paciente.id] = novo_paciente
    return novo_paciente


@router.get("/pacientes/{paciente_id}", response_model=Patient)
def obter_paciente(paciente_id: UUID) -> Patient:
    """Recupera um paciente pelo identificador."""

    try:
        return _patients[paciente_id]
    except KeyError as exc:  # pragma: no cover - tratado de forma uniforme
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado") from exc


@router.put("/pacientes/{paciente_id}", response_model=Patient)
def atualizar_paciente(paciente_id: UUID, payload: PatientCreate) -> Patient:
    """Atualiza um paciente existente."""

    if paciente_id not in _patients:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")

    paciente_atualizado = Patient(id=paciente_id, **payload.model_dump())
    _patients[paciente_id] = paciente_atualizado
    return paciente_atualizado


@router.delete(
    "/pacientes/{paciente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remover_paciente(paciente_id: UUID) -> None:
    """Remove um paciente cadastrado."""

    if paciente_id not in _patients:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")

    # Também remove consultas relacionadas
    for consulta_id, consulta in list(_appointments.items()):
        if consulta.paciente_id == paciente_id:
            _appointments.pop(consulta_id)

    _patients.pop(paciente_id)


@router.get("/consultas", response_model=List[Appointment])
def listar_consultas() -> List[Appointment]:
    """Retorna todas as consultas cadastradas."""

    return list(_appointments.values())


@router.post(
    "/consultas",
    response_model=Appointment,
    status_code=status.HTTP_201_CREATED,
)
def criar_consulta(payload: AppointmentCreate) -> Appointment:
    """Cria uma consulta associada a um paciente existente."""

    if payload.paciente_id not in _patients:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado para a consulta")

    nova_consulta = Appointment(id=uuid4(), **payload.model_dump())
    _appointments[nova_consulta.id] = nova_consulta
    return nova_consulta


@router.delete(
    "/consultas/{consulta_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remover_consulta(consulta_id: UUID) -> None:
    """Remove uma consulta cadastrada."""

    if consulta_id not in _appointments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consulta não encontrada")

    _appointments.pop(consulta_id)
