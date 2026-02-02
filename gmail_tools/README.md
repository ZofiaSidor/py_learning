# Gmail Cleanup Tools

Automatyczne porządkowanie skrzynki Gmail - kategoryzacja i przenoszenie wiadomości do folderów.

## 📋 Funkcje

- **Automatyczna kategoryzacja** - 12 kategorii wiadomości
- **Dry run mode** - podgląd przed wykonaniem zmian
- **Gmail API OAuth** - bezpieczna autoryzacja
- **Batch processing** - przetwarzanie 500 wiadomości na raz

## 🗂️ Kategorie

### Główne kategorie:
1. **Rekrutacja/LinkedIn** - LinkedIn, rekruterzy, oferty pracy
2. **Tech/GitHub** - GitHub, GitLab, Dependabot, pull requests
3. **Powiadomienia** - Newslettery, no-reply, powiadomienia
4. **Finanse** - Faktury, płatności, rachunki
5. **Zakupy** - Amazon, Allegro, zamówienia, dostawy
6. **Kalendarz** - Zaproszenia kalendarzowe
7. **Spotkania** - Fireflies, Zoom, Meet, Teams

### Nowe kategorie (rozszerzone):
8. **Gemini/Meet Notes** - Automatyczne notatki ze spotkań
9. **Edukacja/Webinary** - Webinary, kursy online, szkolenia
10. **Tech Services/Hosting** - Hostinger, domeny, SSL, hosting
11. **Rozrywka/Media** - BookBeat, Spotify, audiobooki, podcasty
12. **Inne** - Pozostałe wiadomości

## 🚀 Instalacja

### 1. Zainstaluj wymagane biblioteki

```bash
sudo apt-get install python3-google-api-python-client python3-google-auth-oauthlib
```

### 2. Skonfiguruj Gmail API

Zobacz instrukcje: [gmail_enable_api.md](gmail_enable_api.md)

Krótko:
1. Włącz Gmail API w Google Cloud Console
2. Uruchom: `python3 gmail_auth.py`
3. Zaloguj się i zatwierdź dostęp

### 3. Uruchom cleanup

```bash
python3 gmail_cleanup.py
```

## 📁 Pliki

- `gmail_cleanup.py` - Główny skrypt porządkowania (6.9 KB)
- `gmail_auth.py` - OAuth autoryzacja (2.4 KB)
- `gmail_enable_api.md` - Instrukcje konfiguracji
- `.gitignore` - Zabezpieczenie credentials

## ⚠️ Bezpieczeństwo

**NIGDY NIE COMMITUJ:**
- `token.pickle` - Token OAuth
- `client_secret.json` - Credentials OAuth
- `credentials.json` - Credentials

Pliki te są chronione przez `.gitignore`.

## 📊 Statystyki

- Przetwarza: **500 wiadomości na uruchomienie**
- Kategoryzuje: **12 kategorii**
- Pokazuje postęp: **co 50 wiadomości**
- Dry run: **Tak, zawsze najpierw podgląd**

## 🔄 Jak używać

1. **Pierwsze uruchomienie:**
   ```bash
   python3 gmail_auth.py
   python3 gmail_cleanup.py
   ```

2. **Kolejne uruchomienia:**
   ```bash
   python3 gmail_cleanup.py
   ```

3. **Jeśli masz więcej niż 500 wiadomości** - uruchom ponownie aż INBOX będzie pusty

## 📝 Notatki

- Skrypt działa w trybie **dry run** - pokazuje podgląd przed wykonaniem
- Wymaga potwierdzenia `TAK` przed przeniesieniem wiadomości
- Tworzy etykiety (foldery) automatycznie jeśli nie istnieją
- Przenosi wiadomości z INBOX do odpowiednich folderów

## 🛠️ Rozszerzenia

Możesz dodać własne kategorie edytując funkcję `categorize_email()` w `gmail_cleanup.py`.

Przykład:
```python
if any(word in from_lower or word in subject_lower for word in
       ['custom', 'keywords']):
    return 'Moja Kategoria'
```

## 📧 Autor

Zofia Sidor
- Email: zofia.sidor@zofiasidor.com
- Projekt: Łowcy Kariery

---

**Ostatnia aktualizacja:** 2026-02-02
**Wersja:** 2.0 (z rozszerzonymi kategoriami)
