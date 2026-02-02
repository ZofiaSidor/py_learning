#!/usr/bin/env python3
"""
Gmail Cleanup Script
Porządkuje Gmail - przenosi wiadomości do folderów według kategorii
"""

import os
import pickle
from googleapiclient.discovery import build
from collections import defaultdict
import re

def get_gmail_service():
    """Łączy się z Gmail API"""
    token_file = os.path.expanduser('~/token.pickle')

    if not os.path.exists(token_file):
        print("❌ Brak token.pickle")
        print("   Uruchom najpierw: python3 ~/gmail_auth.py")
        return None

    with open(token_file, 'rb') as token:
        creds = pickle.load(token)

    return build('gmail', 'v1', credentials=creds)

def analyze_inbox(service):
    """Analizuje skrzynkę odbiorczą"""
    print("📊 Analizuję skrzynkę odbiorczą...")

    # Pobierz wiadomości z inbox
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        maxResults=500  # Możesz zwiększyć
    ).execute()

    messages = results.get('messages', [])
    print(f"   Znaleziono: {len(messages)} wiadomości w INBOX")

    if not messages:
        print("✅ Inbox jest pusty!")
        return {}

    # Kategoryzacja
    categories = defaultdict(list)

    print("🔍 Kategoryzuję wiadomości...")
    for i, msg in enumerate(messages):
        if i % 50 == 0:
            print(f"   Przetworzono: {i}/{len(messages)}")

        # Pobierz szczegóły wiadomości
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['From', 'Subject']
        ).execute()

        headers = msg_data['payload']['headers']
        from_header = next((h['value'] for h in headers if h['name'] == 'From'), '')
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')

        # Kategoryzuj na podstawie From i Subject
        category = categorize_email(from_header, subject)
        categories[category].append({
            'id': msg['id'],
            'from': from_header,
            'subject': subject
        })

    print(f"✅ Analiza zakończona: {len(messages)} wiadomości")
    return categories

def categorize_email(from_addr, subject):
    """Kategoryzuje email na podstawie nadawcy i tematu"""
    from_lower = from_addr.lower()
    subject_lower = subject.lower()

    # Regex patterns
    if any(word in from_lower or word in subject_lower for word in
           ['linkedin', 'recruiters', 'jobvite', 'talent', 'recruitment']):
        return 'Rekrutacja/LinkedIn'

    if any(word in from_lower or word in subject_lower for word in
           ['github', 'gitlab', 'dependabot', 'pull request', 'pr #']):
        return 'Tech/GitHub'

    if any(word in from_lower for word in
           ['noreply', 'no-reply', 'notification', 'newsletter']):
        return 'Powiadomienia'

    if any(word in from_lower or word in subject_lower for word in
           ['invoice', 'payment', 'faktura', 'płatność', 'rachunek']):
        return 'Finanse'

    if any(word in from_lower or word in subject_lower for word in
           ['amazon', 'allegro', 'zamówienie', 'order', 'dostawa']):
        return 'Zakupy'

    if 'calendar' in from_lower or 'invitation' in subject_lower:
        return 'Kalendarz'

    if any(word in from_lower for word in
           ['fireflies', 'zoom', 'meet', 'teams']):
        return 'Spotkania'

    # Nowe kategorie - bardziej szczegółowe

    # Gemini/Meet Notes - notatki automatyczne ze spotkań
    if any(word in from_lower for word in
           ['gemini-notes@google.com', 'meet-notes']):
        return 'Gemini/Meet Notes'
    if any(word in subject_lower for word in
           ['notatki:', 'notes:', 'meeting notes', 'transkrypcja']):
        return 'Gemini/Meet Notes'

    # Edukacja/Webinary - webinary, kursy online, szkolenia
    if any(word in from_lower or word in subject_lower for word in
           ['streamyard', 'webinar', 'vibecoding', 'campusai', 'campus ai',
            'kurs', 'szkolenie', 'workshop', 'masterclass', 'ai skills today',
            'bolt.new', 'stackblitz', 'coursera', 'udemy']):
        return 'Edukacja/Webinary'

    # Tech Services/Hosting - domeny, hosting, serwisy techniczne
    if any(word in from_lower or word in subject_lower for word in
           ['hostinger', 'domain', 'hosting', 'server', 'ssl', 'dns',
            'konserwacja', 'maintenance', 'uptime', 'cloudflare', 'vercel']):
        return 'Tech Services/Hosting'

    # Rozrywka/Media - audiobooki, streaming, social media rozrywkowe
    if any(word in from_lower or word in subject_lower for word in
           ['bookbeat', 'instagram', 'spotify', 'youtube', 'netflix',
            'audioteka', 'empik', 'audiobook', 'podcast']):
        return 'Rozrywka/Media'

    # Domyślnie
    return 'Inne'

def create_labels(service, categories):
    """Tworzy etykiety (foldery) w Gmail"""
    print("\n📁 Tworzę etykiety...")

    # Pobierz istniejące etykiety
    results = service.users().labels().list(userId='me').execute()
    existing_labels = {label['name']: label['id'] for label in results.get('labels', [])}

    label_ids = {}

    for category in categories.keys():
        if category in existing_labels:
            label_ids[category] = existing_labels[category]
            print(f"   ✓ {category} (już istnieje)")
        else:
            # Utwórz nową etykietę
            label = service.users().labels().create(
                userId='me',
                body={
                    'name': category,
                    'labelListVisibility': 'labelShow',
                    'messageListVisibility': 'show'
                }
            ).execute()
            label_ids[category] = label['id']
            print(f"   ✓ {category} (utworzono)")

    return label_ids

def move_to_folders(service, categories, label_ids, dry_run=True):
    """Przenosi wiadomości do folderów"""
    print(f"\n📦 Przenoszę wiadomości (dry_run={dry_run})...")

    stats = defaultdict(int)

    for category, messages in categories.items():
        label_id = label_ids[category]
        print(f"\n   {category}: {len(messages)} wiadomości")

        for msg in messages[:5]:  # Pokaż przykłady
            print(f"      • {msg['subject'][:60]}")

        if len(messages) > 5:
            print(f"      ... i {len(messages)-5} więcej")

        if not dry_run:
            # Przenieś wiadomości (usuwanie INBOX, dodawanie kategorii)
            for msg in messages:
                service.users().messages().modify(
                    userId='me',
                    id=msg['id'],
                    body={
                        'addLabelIds': [label_id],
                        'removeLabelIds': ['INBOX']
                    }
                ).execute()
            stats[category] = len(messages)

    return stats

def main():
    """Główna funkcja"""
    print("="*70)
    print("GMAIL CLEANUP - PORZĄDKOWANIE SKRZYNKI")
    print("="*70)
    print()

    # Połącz z Gmail
    service = get_gmail_service()
    if not service:
        return

    # Analizuj inbox
    categories = analyze_inbox(service)

    if not categories:
        return

    # Pokaż statystyki
    print("\n" + "="*70)
    print("STATYSTYKI KATEGORYZACJI")
    print("="*70)
    for category, messages in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {category:30} {len(messages):4} wiadomości")

    # Utwórz etykiety
    label_ids = create_labels(service, categories)

    # DRY RUN - pokaż co zostanie zrobione
    print("\n" + "="*70)
    print("PODGLĄD ZMIAN (DRY RUN)")
    print("="*70)
    move_to_folders(service, categories, label_ids, dry_run=True)

    # Zapytaj użytkownika
    print("\n" + "="*70)
    print("⚠️  UWAGA: To przeniesie wiadomości z INBOX do folderów!")
    print("="*70)
    response = input("\nCzy wykonać operację? (TAK/nie): ")

    if response.upper() == 'TAK':
        stats = move_to_folders(service, categories, label_ids, dry_run=False)
        print("\n" + "="*70)
        print("✅ SUKCES! Porządki zakończone")
        print("="*70)
        for category, count in stats.items():
            print(f"  ✓ {category}: {count} wiadomości przeniesionych")
    else:
        print("\n❌ Anulowano. Żadne zmiany nie zostały wykonane.")

if __name__ == '__main__':
    main()
