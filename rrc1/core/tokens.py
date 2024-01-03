from rest_framework_simplejwt.tokens import RefreshToken


class CustomToken(RefreshToken):

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)

        token['role'] = user.role
        token['username'] = user.username
        return token
