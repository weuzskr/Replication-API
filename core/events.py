from typing import Callable
from fastapi import FastAPI


def create_start_app_handler(app: FastAPI) -> Callable:
    def start_app() -> None:
        # Le chargement du modèle est désactivé pour l’instant.
        pass

    return start_app
