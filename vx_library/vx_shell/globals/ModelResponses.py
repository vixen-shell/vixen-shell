from fastapi import Response
from pydantic import BaseModel
from typing import Dict


class ModelResponses:
    def __init__(self, models: Dict[int, BaseModel]):
        self._models = models

    def __call__(self, response: Response, status_code: int) -> BaseModel:
        response.status_code = status_code
        return self._models[status_code]

    @property
    def responses(self) -> Dict:
        responses = {}
        for status_code in self._models:
            responses[status_code] = {"model": self._models[status_code]}
        return responses
