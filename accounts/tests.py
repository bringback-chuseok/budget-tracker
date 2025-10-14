from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthCookieTests(APITestCase):
    def test_register_creates_user_and_hashes_password(self):
        payload = {
            'username': 'newbie',
            'email': 'newbie@example.com',
            'password': 'strongpass123',
        }

        response = self.client.post('/auth/register/', payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], '회원가입이 완료되었습니다.')
        created_user = User.objects.get(username='newbie')
        self.assertTrue(created_user.check_password(payload['password']))
        self.assertEqual(created_user.email, payload['email'])

    def setUp(self):
        self.password = 'testpass123'
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password=self.password,
        )

    def test_login_sets_jwt_cookies(self):
        response = self.client.post(
            '/auth/login/',
            {'username': self.user.username, 'password': self.password},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], '로그인에 성공했습니다.')
        self.assertIn(settings.AUTH_COOKIE, response.cookies)
        self.assertIn(settings.AUTH_COOKIE_REFRESH, response.cookies)
        self.assertNotEqual(response.cookies[settings.AUTH_COOKIE].value, '')

    def test_refresh_uses_cookie_when_payload_empty(self):
        self.client.post(
            '/auth/login/',
            {'username': self.user.username, 'password': self.password},
            format='json',
        )

        self.assertIn(settings.AUTH_COOKIE_REFRESH, self.client.cookies)

        response = self.client.post('/auth/token/refresh/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], '토큰을 재발급했습니다.')
        self.assertIn(settings.AUTH_COOKIE, response.cookies)

    def test_logout_blacklists_refresh_token(self):
        login_response = self.client.post(
            '/auth/login/',
            {'username': self.user.username, 'password': self.password},
            format='json',
        )
        refresh_token = login_response.cookies[settings.AUTH_COOKIE_REFRESH].value

        response = self.client.post('/auth/logout/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], '로그아웃되었습니다.')
        self.assertIn(settings.AUTH_COOKIE, response.cookies)
        self.assertEqual(response.cookies[settings.AUTH_COOKIE].value, '')
        self.assertEqual(response.cookies[settings.AUTH_COOKIE_REFRESH].value, '')

        reuse_response = self.client.post(
            '/auth/token/refresh/',
            {'refresh': refresh_token},
            format='json',
        )
        self.assertEqual(reuse_response.status_code, status.HTTP_401_UNAUTHORIZED)
