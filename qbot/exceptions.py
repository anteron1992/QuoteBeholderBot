class QBException(Exception):
    """ Basic QuoteBeholder exception """


class TokenNotFound(QBException):
    """ Token is not found """


class AccountNotFound(QBException):
    """ Account ID is not found """


class DatabaseSchemeError(QBException):
    """ Database scheme not found """


class DatabaseConnectionError(QBException):
    """ Connecting database error """


class DatabaseTableError(QBException):
    """ Table is not found """
