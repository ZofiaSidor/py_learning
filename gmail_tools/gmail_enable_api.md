# WŁĄCZENIE GMAIL API - UPROSZCZONE INSTRUKCJE

## ✅ CO JUŻ MASZ:
- Projekt Google Cloud: `integral-helper-463620-h7`
- OAuth credentials (client_secret.json)
- Skrypty gotowe do użycia

## 📋 CO MUSISZ ZROBIĆ:

### KROK 1: Włącz Gmail API (2 minuty)

1. Wejdź na: **https://console.cloud.google.com/**
2. Zaloguj się jako: **zofia.sidor@zofiasidor.com**
3. Upewnij się że wybrany jest projekt: **integral-helper-463620-h7**
   (sprawdź w dropdown na górze)
4. Menu (☰) → **APIs & Services** → **Library**
5. Szukaj: `Gmail API`
6. Kliknij **Gmail API**
7. Kliknij **ENABLE**

### KROK 2: Autoryzuj dostęp (1 minuta)

W Linuxie uruchom:
```bash
python3 ~/gmail_auth.py
```

- Otworzy się przeglądarka
- Zaloguj się jako zofia.sidor@zofiasidor.com
- Kliknij **Allow** / **Zezwól**
- Po autoryzacji pojawi się: "The authentication flow has completed"

Token zostanie zapisany w: `~/token.pickle`

### KROK 3: Uruchom porządki w Gmail

```bash
python3 ~/gmail_cleanup.py
```

Skrypt:
1. Przeanalizuje Twój INBOX
2. Pokaże podgląd kategoryzacji (dry run)
3. Zapyta o zgodę przed przeniesieniem
4. Przeniesie wiadomości do folderów

---

## ⚠️ UWAGA:

Gmail API wymaga dodania scope w OAuth consent screen.

Jeśli podczas autoryzacji zobaczysz błąd "Access blocked", musisz:

1. Menu (☰) → **APIs & Services** → **OAuth consent screen**
2. Kliknij **EDIT APP**
3. Przejdź do **Scopes** → **ADD OR REMOVE SCOPES**
4. Znajdź: `.../auth/gmail.modify`
5. Zaznacz i **UPDATE**
6. **SAVE AND CONTINUE**

Potem uruchom ponownie: `python3 ~/gmail_auth.py`

---

## 🎯 GOTOWE!

Po tych krokach będziesz miał:
- ✅ Dostęp do Gmail API
- ✅ Automatyczne porządkowanie skrzynki
- ✅ Wszystko skategoryzowane

Powodzenia! 🚀
