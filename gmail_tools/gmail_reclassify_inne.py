#!/usr/bin/env python3
"""
Gmail Reclassify "Inne" - Przeklasyfikowanie folderu "Inne"
Przenosi wiadomości z "Inne" do bardziej szczegółowych kategorii
"""

import os
import pickle
from googleapiclient.discovery import build
from collections import defaultdict

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

def categorize_email(from_addr, subject):
    """Kategoryzuje email - TYLKO nowe kategorie z analizy "Inne" """
    from_lower = from_addr.lower()
    subject_lower = subject.lower()

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

    # Jeśli nie pasuje - zostaje w Inne
    return 'Inne'

def reclassify_inne(service):
    """Przeklasyfikowuje wiadomości z folderu Inne"""
    print("🔍 Szukam folderu 'Inne'...")

    # Pobierz ID etykiety "Inne"
    labels = service.users().labels().list(userId='me').execute()
    inne_label_id = None

    for label in labels.get('labels', []):
        if label['name'] == 'Inne':
            inne_label_id = label['id']
            break

    if not inne_label_id:
        print("❌ Folder 'Inne' nie istnieje")
        return {}

    # Pobierz wiadomości z "Inne"
    results = service.users().messages().list(
        userId='me',
        labelIds=[inne_label_id],
        maxResults=500
    ).execute()

    messages = results.get('messages', [])
    print(f"   Znaleziono: {len(messages)} wiadomości w folderze 'Inne'\n")

    if not messages:
        print("✅ Folder 'Inne' jest pusty!")
        return {}

    # Kategoryzacja
    categories = defaultdict(list)

    print("🔍 Kategoryzuję wiadomości...")
    for i, msg in enumerate(messages):
        if i % 50 == 0 and i > 0:
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

        # Kategoryzuj
        category = categorize_email(from_header, subject)

        # Dodaj tylko jeśli NIE jest "Inne" (czyli znaleziono lepszą kategorię)
        if category != 'Inne':
            categories[category].append({
                'id': msg['id'],
                'from': from_header,
                'subject': subject
            })

    print(f"✅ Analiza zakończona: {len(messages)} wiadomości\n")

    # Pokaż co zostanie przeniesione
    to_move = sum(len(msgs) for msgs in categories.values())
    staying = len(messages) - to_move

    print(f"📊 Do przeniesienia: {to_move} wiadomości")
    print(f"📊 Zostaje w 'Inne': {staying} wiadomości\n")

    return categories

def create_labels(service, categories):
    """Tworzy etykiety jeśli nie istnieją"""
    print("📁 Sprawdzam etykiety...\n")

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

def move_to_folders(service, categories, label_ids, inne_label_id, dry_run=True):
    """Przenosi wiadomości do folderów"""
    print(f"\n📦 Przenoszę wiadomości (dry_run={dry_run})...\n")

    stats = defaultdict(int)

    for category, messages in categories.items():
        label_id = label_ids[category]
        print(f"   {category}: {len(messages)} wiadomości")

        for msg in messages[:5]:  # Pokaż przykłady
            print(f"      • {msg['subject'][:60]}")

        if len(messages) > 5:
            print(f"      ... i {len(messages)-5} więcej")

        if not dry_run:
            # Przenieś wiadomości (usuwanie Inne, dodawanie nowej kategorii)
            for msg in messages:
                service.users().messages().modify(
                    userId='me',
                    id=msg['id'],
                    body={
                        'addLabelIds': [label_id],
                        'removeLabelIds': [inne_label_id]
                    }
                ).execute()
            stats[category] = len(messages)

        print()

    return stats

def main():
    """Główna funkcja"""
    print("="*70)
    print("GMAIL RECLASSIFY 'INNE' - PRZEKLASYFIKOWANIE FOLDERU")
    print("="*70)
    print()

    # Połącz z Gmail
    service = get_gmail_service()
    if not service:
        return

    # Pobierz ID etykiety "Inne"
    labels = service.users().labels().list(userId='me').execute()
    inne_label_id = None
    for label in labels.get('labels', []):
        if label['name'] == 'Inne':
            inne_label_id = label['id']
            break

    # Analizuj folder Inne
    categories = reclassify_inne(service)

    if not categories:
        print("✅ Wszystkie wiadomości w 'Inne' są już dobrze skategoryzowane!")
        return

    # Pokaż statystyki
    print("="*70)
    print("STATYSTYKI PRZEKLASYFIKOWANIA")
    print("="*70)
    for category, messages in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {category:30} {len(messages):4} wiadomości")

    # Utwórz etykiety
    label_ids = create_labels(service, categories)

    # DRY RUN - pokaż co zostanie zrobione
    print("\n" + "="*70)
    print("PODGLĄD ZMIAN (DRY RUN)")
    print("="*70)
    move_to_folders(service, categories, label_ids, inne_label_id, dry_run=True)

    # Zapytaj użytkownika
    print("="*70)
    print("⚠️  UWAGA: To przeniesie wiadomości z 'Inne' do nowych folderów!")
    print("="*70)
    response = input("\nCzy wykonać operację? (TAK/nie): ")

    if response.upper() == 'TAK':
        stats = move_to_folders(service, categories, label_ids, inne_label_id, dry_run=False)
        print("\n" + "="*70)
        print("✅ SUKCES! Przeklasyfikowanie zakończone")
        print("="*70)
        for category, count in stats.items():
            print(f"  ✓ {category}: {count} wiadomości przeniesionych")
    else:
        print("\n❌ Anulowano. Żadne zmiany nie zostały wykonane.")

if __name__ == '__main__':
    main()
