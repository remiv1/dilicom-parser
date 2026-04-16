"""
Module des exceptions personnalisées pour la gestion des erreurs de connexion et d'authentification
au serveur SFTP de Dilicom, ainsi que pour les erreurs lors des opérations SFTP.
"""

class DilicomConnectionError(Exception):
    """
    Exception levée en cas d'erreur de connexion au serveur SFTP de Dilicom.
    """
    def stdr_message(self):
        """
        Message d'erreur standard pour les problèmes de connexion au serveur SFTP de Dilicom.
        """
        return "Connexion SFTP non établie. Connectez-vous avant de télécharger un fichier."


class DilicomAuthenticationError(Exception):
    """
    Exception levée en cas d'erreur d'authentification au serveur SFTP de Dilicom.
    """
    def stdr_message(self):
        """
        Message d'erreur standard pour les problèmes d'authentification au serveur SFTP de Dilicom.
        """
        return "Erreur d'authentification au serveur SFTP de Dilicom."


class DilicomSFTPError(Exception):
    """
    Exception levée en cas d'erreur lors des opérations SFTP avec le serveur de Dilicom.
    """
    def stdr_message(self):
        """
        Message d'erreur standard pour les problèmes lors des opérations SFTP avec le serveur.
        """
        return "Erreur lors des opérations SFTP avec le serveur de Dilicom."
