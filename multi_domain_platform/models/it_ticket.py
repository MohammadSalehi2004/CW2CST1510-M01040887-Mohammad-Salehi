#Applying OOP to the tickets.py from week8

#defining class for ITTickets
from datetime import datetime

class ITTicket:
    """Represents an IT support ticket."""

    #securing all my columns from tickets.py(week8)
    def __init__(
        self,
        ticket_id: int,
        priority: str,
        status: str,
        category: str,
        subject: str,
        assigned_to: str | None,
        created_at: str,
        resolved_date: str | None = None
    ):
        # private attributes
        self.__id = ticket_id
        self.__ticket_id = ticket_id   # fixed: external_ticket_id was undefined
        self.__priority = priority
        self.__status = status
        self.__category = category
        self.__subject = subject
        self.__assigned_to = assigned_to
        self.__created_at = created_at
        self.__resolved_date = resolved_date

    #getters from lab example and for the rest of columns in my tickets.py
    def get_id(self) -> int:
        return self.__id

    def get_ticket_id(self) -> int:
        return self.__ticket_id

    def get_priority(self) -> str:
        return self.__priority

    def get_status(self) -> str:
        """Return the current ticket status."""
        return self.__status

    def get_category(self) -> str:
        return self.__category

    def get_subject(self) -> str:
        return self.__subject

    def get_assigned_to(self) -> str | None:
        return self.__assigned_to

    def get_created_at(self) -> str:
        return self.__created_at

    def get_resolved_date(self) -> str | None:
        return self.__resolved_date

    def assign_to(self, staff_name: str) -> None:
        """Assign ticket to."""
        self.__assigned_to = staff_name

    def close_ticket(self) -> None:
        """Close the ticket and mark the resolved date."""
        self.__status = "Closed"
        self.__resolved_date = datetime.now()

    def __str__(self) -> str:
        return (
            f"IT Ticket {self.__id}: {self.__subject} | "
            f"Priority: {self.__priority} | Status: {self.__status} | "
            f"Assigned to: {self.__assigned_to} | Created at: {self.__created_at} | "
            f"Resolved: {self.__resolved_date}"
        )
    
#example for print like the lab practices
"""ticket = ITTicket(
    1,
    "High",
    "Open",
    "Network",
    "Internet down",
    None,
    "2025-12-13"
)

print(ticket)"""
