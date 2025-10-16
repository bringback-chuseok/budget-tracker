"""
Provider-specific helper functions for social login.

각 OAuth 제공자의 토큰을 검증하고 사용자 프로필 정보를 반환한다.
실제 HTTP 호출은 requests로 수행하며, 테스트에서는 이 모듈의 함수를
patch하여 외부 네트워크 의존성을 제거할 수 있다.
"""

from dataclasses import dataclass

import requests
from requests import HTTPError


class SocialLoginError(Exception):
    """소셜 로그인 처리 중 발생한 오류."""


@dataclass
class SocialProfile:
    provider: str
    provider_user_id: str
    email: str
    name: str | None = None


def _request(
    url: str,
    *,
    method: str = "get",
    headers: dict[str, str] | None = None,
    params=None,
    timeout: int = 5,
):
    response = requests.request(
        method, url, headers=headers, params=params, timeout=timeout
    )
    try:
        response.raise_for_status()
    except HTTPError as exc:
        raise SocialLoginError("외부 인증 서버와 통신에 실패했습니다.") from exc
    try:
        return response.json()
    except ValueError as exc:
        raise SocialLoginError("외부 인증 서버 응답이 올바르지 않습니다.") from exc


def fetch_google_profile(id_token: str) -> SocialProfile:
    """
    Google OAuth ID 토큰을 검증하고 사용자 이메일 정보를 반환한다.
    """
    payload = _request(
        "https://oauth2.googleapis.com/tokeninfo",
        params={"id_token": id_token},
    )

    email = payload.get("email")
    sub = payload.get("sub")

    if not email or not sub:
        raise SocialLoginError("구글 사용자 정보에 이메일이 없습니다.")

    return SocialProfile(
        provider="google",
        provider_user_id=sub,
        email=email,
        name=payload.get("name"),
    )


def fetch_kakao_profile(access_token: str) -> SocialProfile:
    """
    Kakao OAuth 액세스 토큰을 검증하고 사용자 정보를 반환한다.
    """
    payload = _request(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    kakao_id = payload.get("id")
    kakao_account = payload.get("kakao_account", {})
    email = kakao_account.get("email")

    if not kakao_id or not email:
        raise SocialLoginError("카카오 사용자 정보에 이메일이 없습니다.")

    profile = kakao_account.get("profile") or {}

    return SocialProfile(
        provider="kakao",
        provider_user_id=str(kakao_id),
        email=email,
        name=profile.get("nickname"),
    )


def get_social_profile(provider: str, token: str) -> SocialProfile:
    """
    주어진 provider/token 조합으로 SocialProfile 객체를 반환한다.
    """
    if provider == "google":
        return fetch_google_profile(token)
    if provider == "kakao":
        return fetch_kakao_profile(token)
    raise SocialLoginError("지원하지 않는 소셜 로그인 제공자입니다.")
