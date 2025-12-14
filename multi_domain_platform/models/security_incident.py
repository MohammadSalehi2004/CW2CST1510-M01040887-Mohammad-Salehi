#Applying OOP to the incidents.py from week8

#defining class for securityincident
class SecurityIncident:
    """Represents a cybersecurity incident in the platform."""

    #securing all my columns from incidents.py(week8)
    def __init__(
        self,
        incident_id: int,
        date: str,
        incident_type: str,
        severity: str,
        status: str,
        description: str,
        reported_by: str,
        created_at: str
    ):  
        #used __ to keep it private
        self.__id = incident_id
        self.__date = date
        self.__incident_type = incident_type
        self.__severity = severity
        self.__status = status
        self.__description = description
        self.__reported_by = reported_by
        self.__created_at = created_at

    #methods for accessing the information, i left dates since i feel like these are more important
    def get_id(self) -> int:
        return self.__id

    def get_date(self) -> str:
        return self.__date

    def get_incident_type(self) -> str:
        return self.__incident_type

    def get_severity(self) -> str:
        return self.__severity

    def get_status(self) -> str:
        return self.__status

    def get_description(self) -> str:
        return self.__description
    
    def get_reported_by(self) -> str:
        return self.__reported_by
    
    def get_created_at(self) -> str:
        return self.__created_at

    #Allowing control to update the status for the incidents
    def update_status(self, new_status: str) -> None:
        self.__status = new_status
    
    #converting severity levels to numbers
    def get_severity_level(self) -> int:
        mapping = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }
        return mapping.get(self.__severity.lower(), 0)

    def __str__(self) -> str:
        return (
            f"Incident {self.__id} | Type: {self.__incident_type} | "
            f"Severity: {self.__severity.upper()} | Status: {self.__status} | "
            f"Date: {self.__date} | Reported by: {self.__reported_by} | "
            f"Created at: {self.__created_at} | Description: {self.__description}"
        )
"""  
#testing print
incident = SecurityIncident(
    1,
    "2025-12-13",
    "Hacking threat",
    "high",
    "open",
    "Systems going down",
    "Mohammad",
    "2025-12-13"
)

print(incident)
"""