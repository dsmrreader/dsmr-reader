import enum
from enum import unique
from typing import Union, Dict

from django.utils import timezone


class MonitoringStatusIssue(object):
    source: str
    description: str
    since: timezone.datetime

    def __init__(self, source: str, description: str, since: timezone.datetime):
        self.source = str(source)
        self.description = str(description)
        self.since = since

    def serialize(self) -> Dict:
        return {
            "source": self.source,
            "description": self.description,
            "since": timezone.localtime(self.since),
        }


@unique
class Capability(enum.Enum):
    """List of types of capabilities available. They act as feature flags in this project."""

    ANY = "any"
    ELECTRICITY = "electricity"
    ELECTRICITY_RETURNED = "electricity_returned"
    MULTI_PHASES = "multi_phases"
    VOLTAGE = "voltage"
    POWER_CURRENT = "power_current"
    GAS = "gas"
    WEATHER = "weather"
    COSTS = "costs"


class CapabilityReport(object):
    """Lists all capabilities found. Acts like a dict in disguise to ease usage in templates."""

    _capabilities: Dict[str, Capability]

    def __init__(self):
        self._capabilities = {}

    def add(self, capability: Capability):
        self._capabilities[capability.value] = capability

    def __contains__(self, capability: Union[str, Capability]) -> bool:
        """Check whether the capability is found in this report."""
        if isinstance(capability, str):
            try:
                # Presumes all capability enums names are simply the uppercase value.
                getattr(Capability, capability.upper())
            except AttributeError as exc:
                raise KeyError("Unknown capability: " + capability) from exc

        if isinstance(capability, Capability):
            capability = capability.value

        return capability in self._capabilities.keys()

    def __getitem__(self, capability):
        return self.__contains__(capability)

    def __len__(self) -> int:
        return len(self._capabilities)
