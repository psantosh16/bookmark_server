from fastapi import FastAPI, HTTPException, Depends, Request
from firebase_admin import auth
# from supabase import create_client, Client
import os
from dotenv import load_dotenv
from services.firebase import FirebaseService

app = FastAPI()
load_dotenv()


# Supabase setup
# SUPABASE_URL = os.getenv('SUPABASE_URL')
# SUPABASE_KEY = os.getenv('SUPABASE_KEY')
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.get('/')
def root():
    return {'message': '<h1>Service is running successfully</h1>'}

@app.get('/users/me')
def get_current_user(user=Depends(FirebaseService.verify_firebase_user)):
    return {'uid': user.uid, 'email': user.email}

# @app.post('/data')
# def create_data(item: dict, user=Depends(FirebaseService.verify_firebase_user)):
#     response = supabase.table('data').insert(item).execute()
#     return response.data

# @app.get('/data')
# def read_data(user=Depends(FirebaseService.verify_firebase_user)):
#     response = supabase.table('data').select('*').execute()
#     return response.data

# @app.put('/data/{item_id}')
# def update_data(item_id: int, item: dict, user=Depends(FirebaseService.verify_firebase_user)):
#     response = supabase.table('data').update(item).eq('id', item_id).execute()
#     return response.data

# @app.delete('/data/{item_id}')
# def delete_data(item_id: int, user=Depends(FirebaseService.verify_firebase_user)):
#     response = supabase.table('data').delete().eq('id', item_id).execute()
#     return response.data 