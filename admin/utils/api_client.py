import httpx
import streamlit as st

from admin.config import AdminConfig


class APIClient:
    """Streamlit Admin Dashboard용 Thin Client"""

    def __init__(self):
        self.config = AdminConfig()
        self.base_url = self.config.api_url.rstrip("/") + "/"
        self.timeout = 60.0

    def _handle_response(self, response: httpx.Response):
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            st.error(f"API Error ({e.response.status_code}): {e.response.text}")
            return None
        except Exception as e:
            st.error(f"Connection Error: {str(e)}")
            return None

    def get(self, endpoint: str, params: dict = None):
        endpoint = endpoint.lstrip("/")
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            response = client.get(endpoint, params=params)
            return self._handle_response(response)

    def post(self, endpoint: str, json: dict = None):
        endpoint = endpoint.lstrip("/")
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            response = client.post(endpoint, json=json)
            return self._handle_response(response)

    def upload_file(self, endpoint: str, files: any):
        """
        지원: 
        - 단일: files={'file': ('filename', content, 'mime')}
        - 다중: files=[('files', ('name1', content1, 'mime1')), ('files', ('name2', content2, 'mime2'))]
        """
        endpoint = endpoint.lstrip("/")
        # Multipart upload requires a longer timeout
        with httpx.Client(base_url=self.base_url, timeout=120.0) as client:
            response = client.post(endpoint, files=files)
            return self._handle_response(response)

    def delete(self, endpoint: str):
        endpoint = endpoint.lstrip("/")
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            response = client.delete(endpoint)
            return self._handle_response(response)



def get_api_client():
    return APIClient()
