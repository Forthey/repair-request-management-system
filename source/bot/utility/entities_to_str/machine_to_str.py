from schemas.machines import Machine


def machine_to_str(machine: Machine) -> str:
    return f"Название: {machine.name}"
