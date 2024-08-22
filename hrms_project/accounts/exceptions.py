class AuthenticationError(Exception):
    pass

class UserCreationError(Exception):
    pass

class UserUpdateError(Exception):
    pass

class UserDeletionError(Exception):
    pass
class UserNotFoundException(Exception):
    pass