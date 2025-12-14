#Applying OOP to the users.py from week8

#defining class for User
class User:
    """Represents a user in the Multi-Domain Intelligence Platform.
    taking username, hashed password and role of each user in parameter.
    """

    def __init__(self, username: str, password_hash: str, role: str):
        #private attributes
        self.__username = username
        self.__password_hash = password_hash
        self.__role = role

    # Accessor methods
    def get_username(self) -> str: #-> str tells us that it will return a string
        return self.__username

    def get_role(self) -> str:
        return self.__role

    def verify_password(self, plain_password: str, hasher) -> bool:
        """
        Check if a plain-text password matches this user's hash.
        Verify a plain-text password against the stored hash.
        (You will inject this from your AuthManager.)
        """
        return hasher.verify_password(plain_password, self.__password_hash)

    def __str__(self) -> str:
        return f"User({self.__username}, role={self.__role})"
    