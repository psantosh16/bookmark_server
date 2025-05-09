from firebase_admin import credentials, auth, initialize_app, App
import os
from fastapi import HTTPException, Request

class FirebaseService:
    _instance = None
    _app: App = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
            cls._initialize_firebase()
        return cls._instance

    @classmethod
    def _initialize_firebase(cls):
        if cls._app is None:
            FIREBASE_CRED_PATH = os.getenv('FIREBASE_CRED_PATH', 'firebase_credentials.json')
            if not os.path.exists(FIREBASE_CRED_PATH):
                raise RuntimeError('Firebase credentials file not found.')
            cred = credentials.Certificate(FIREBASE_CRED_PATH)
            cls._app = initialize_app(cred)


# Initialize Firebase service
firebase_service = FirebaseService() 