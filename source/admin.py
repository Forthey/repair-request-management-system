from sqladmin import Admin, ModelView
from fastapi import FastAPI

from database.engine import async_engine

from database.models.application_orm import ApplicationORM
from database.models.worker_orm import WorkerORM
from database.models.client_orm import ClientORM
from database.models.address_orm import AddressORM
from database.models.contact_orm import ContactORM
from database.models.machine_orm import MachineORM
from database.models.other_orms import ActivityORM, CloseReasonORM, CompanyPositionORM


app = FastAPI()
admin = Admin(app, async_engine)


class ApplicationAdmin(ModelView, model=ApplicationORM):
    name = "Application"
    column_list = ApplicationORM.__table__.columns


admin.add_view(ApplicationAdmin)


class WorkerAdmin(ModelView, model=WorkerORM):
    name = "Worker"
    column_list = WorkerORM.__table__.columns


admin.add_view(WorkerAdmin)


class ClientAdmin(ModelView, model=ClientORM):
    name = "Client"
    column_list = ClientORM.__table__.columns


admin.add_view(ClientAdmin)


class ContactAdmin(ModelView, model=ContactORM):
    name = "Contact"
    column_list = ClientORM.__table__.columns


admin.add_view(ContactAdmin)


class AddressAdmin(ModelView, model=AddressORM):
    name = "Address"
    name_plural = "Addresses"
    column_list = AddressORM.__table__.columns


admin.add_view(AddressAdmin)


class MachineAdmin(ModelView, model=MachineORM):
    name = "Machine"
    column_list = MachineORM.__table__.columns


admin.add_view(MachineAdmin)


class ActivityAdmin(ModelView, model=ActivityORM):
    name = "Activity"
    name_plural = "Activities"
    column_list = ActivityORM.__table__.columns


admin.add_view(ActivityAdmin)


class CloseReasonAdmin(ModelView, model=CloseReasonORM):
    name = "CloseReason"
    column_list = CloseReasonORM.__table__.columns


admin.add_view(CloseReasonAdmin)


class CompanyPositionAdmin(ModelView, model=CompanyPositionORM):
    name = "CompanyPosition"
    column_list = CompanyPositionORM.__table__.columns


admin.add_view(CompanyPositionAdmin)
