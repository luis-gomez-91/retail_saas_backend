class PlanLimitExceeded(Exception):
    """El plan actual no permite crear más recursos de este tipo."""

    def __init__(self, message: str = 'Límite del plan alcanzado.', *, code: str = 'plan_limit'):
        self.code = code
        super().__init__(message)
