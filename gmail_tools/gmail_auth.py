#!/usr/bin/env python3
"""
Gmail API Authentication Script
Tworzy token.pickle dla dostępu do Gmail API
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Scope - pełny dostęp do Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate():
    """Autoryzuje dostęp do Gmail API"""
    creds = None
    token_file = os.path.expanduser('~/token.pickle')
    # Użyj istniejących credentials z gcalcli
    credentials_file = os.path.expanduser('~/.gcalcli/client_secret.json')

    # Sprawdź czy istnieje token
    if os.path.exists(token_file):
        print("✅ Znaleziono istniejący token")
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    # Jeśli brak ważnych credentials, autoryzuj
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Odświeżam wygasły token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                print("❌ BŁĄD: Brak pliku client_secret.json")
                print(f"   Powinien być w: {credentials_file}")
                return None

            print("🔐 Rozpoczynam autoryzację OAuth...")
            print("   Otworzy się przeglądarka - zaloguj się i zatwierdź dostęp")

            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)

        # Zapisz token
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
        print(f"✅ Token zapisany: {token_file}")

    return creds

if __name__ == '__main__':
    print("="*60)
    print("GMAIL API - AUTORYZACJA")
    print("="*60)
    print()

    creds = authenticate()

    if creds:
        print()
        print("="*60)
        print("✅ SUKCES! Autoryzacja zakończona.")
        print("="*60)
        print()
        print("Teraz możesz uruchomić skrypt porządkowania Gmail:")
        print("  python3 ~/gmail_cleanup.py")
    else:
        print()
        print("="*60)
        print("❌ Autoryzacja nieudana")
        print("="*60)
        print()
        print("Sprawdź instrukcje w: ~/gmail_setup_instrukcje.md")
