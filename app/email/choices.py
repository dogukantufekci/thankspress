from app.choices import Choices

class EmailStatusChoices(Choices):
    NOT_VERIFIED = 0
    VERIFIED = 1
    REPORTED = 2
    DELETED = 3