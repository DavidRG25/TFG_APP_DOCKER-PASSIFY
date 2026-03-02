from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from paasify.middleware import TokenAuthMiddleware
from paasify.models import StudentModel


class TokenAuthMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester', email='tester@example.com', password='abc12345'
        )
        self.profile = StudentModel.UserProfile.objects.create(
            user=self.user, nombre='Tester', year='tester@example.com'
        )
        self.middleware = TokenAuthMiddleware(lambda request: HttpResponse('ok'))

    def test_sets_user_when_token_is_valid(self):
        from paasify.models.TokenModel import ExpiringToken
        token_obj = ExpiringToken.objects.create(user=self.user)
        request = self.factory.get('/api/containers/', HTTP_AUTHORIZATION=f'Bearer {token_obj.key}')

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.user, self.user)

    def test_returns_401_when_token_invalid(self):
        request = self.factory.get(
            '/api/containers/', HTTP_AUTHORIZATION='Bearer invalid.token.example'
        )

        response = self.middleware(request)

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {'detail': 'Token invalido o expirado.', 'code': 'token_not_valid'},
        )
