class QBException(Exception):
    """ Basic Quotebeholder exception """


class TokenNotFound(QBException):
    """ Token is not found """


class AccountNotFound(QBException):
    """ Account ID is not found """
