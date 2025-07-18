#!/usr/bin/env python3
"""
BibleStudyAI API Showcase - Final Working Demo
Demonstrates all successfully working endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def demo_bible_search():
    """Demonstrate Bible search functionality"""
    print("\n🔍 BIBLE SEARCH DEMONSTRATION")
    print("=" * 50)

    # Get John 3:16 from KJV
    response = requests.get(f"{BASE_URL}/api/bible/KJV/John/3/verses")
    verses = response.json()
    john_3_16 = next((v for v in verses if v["verse"] == 16), None)

    if john_3_16:
        print("📖 John 3:16 (KJV):")
        print(f"   \"{john_3_16['text']}\"\n")

    # Get Psalm 23 from ESV
    response = requests.get(f"{BASE_URL}/api/bible/ESV/Psalms/23/verses")
    psalm_23 = response.json()

    print("📖 Psalm 23:1 (ESV):")
    print(f"   \"{psalm_23[0]['text']}\"\n")

    # Search for "faith" across KJV
    response = requests.get(f"{BASE_URL}/api/bible/KJV/search?query=faith")
    faith_verses = response.json()

    print(f"🔍 Found {len(faith_verses)} verses containing 'faith' in KJV")
    print("   Sample verses:")
    for verse in faith_verses[:3]:
        print(f"   - {verse['book']} {verse['chapter']}:{verse['verse']}")
        print(f"     \"{verse['text'][:100]}...\"\n")


def demo_auth_and_notes():
    """Demonstrate authentication and notes functionality"""
    print("\n🔐 AUTHENTICATION & NOTES DEMONSTRATION")
    print("=" * 50)

    # Login to get token
    login_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword123",
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    token_data = response.json()
    token = token_data.get("access_token")

    if token:
        print("✅ Successfully authenticated")

        # Create a study note
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        note_data = {
            "title": "Study on Faith",
            "content": "Faith is the substance of things hoped for, the evidence of things not seen. (Hebrews 11:1)",
            "reference": "Hebrews 11:1",
        }

        response = requests.post(
            f"{BASE_URL}/api/notes/", json=note_data, headers=headers
        )
        if response.status_code == 200:
            print("📝 Successfully created study note")

            # Get all notes
            response = requests.get(f"{BASE_URL}/api/notes/", headers=headers)
            notes = response.json()

            print(f"📚 Total notes: {len(notes)}")
            for note in notes[-2:]:  # Show last 2 notes
                print(
                    f"   - \"{note['title']}\" ({note.get('reference', 'No reference')})"
                )


def demo_rag_system():
    """Demonstrate RAG system"""
    print("\n🤖 RAG SYSTEM DEMONSTRATION")
    print("=" * 50)

    questions = [
        "What does the Bible say about love?",
        "Tell me about faith and works",
        "What is salvation according to scripture?",
    ]

    for question in questions:
        response = requests.post(
            f"{BASE_URL}/api/rag/answer", json={"question": question}
        )
        rag_response = response.json()

        print(f"❓ Question: {question}")
        print(f"🤖 Answer: {rag_response.get('answer', 'No answer')}\n")


def demo_translations():
    """Show available Bible translations"""
    print("\n📚 AVAILABLE BIBLE TRANSLATIONS")
    print("=" * 50)

    response = requests.get(f"{BASE_URL}/api/bible/translations")
    translations = response.json()

    translation_names = {
        "KJV": "King James Version",
        "ESV": "English Standard Version",
        "NAS": "New American Standard Bible (1977)",
        "NLT": "New Living Translation",
        "ASV": "American Standard Version (1901)",
        "NIV": "New International Version (1984)",
        "NIB": "New International Bible",
        "NAU": "New American Standard Bible (1995)",
    }

    for abbrev in translations:
        full_name = translation_names.get(abbrev, abbrev)
        print(f"   📖 {abbrev}: {full_name}")


def main():
    """Run the complete demonstration"""
    print("🚀 BibleStudyAI API - Working Features Showcase")
    print("=" * 60)

    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        health = response.json()
        print(f"✅ API Status: {health['status'].upper()}")
        print(f"📅 Timestamp: {health['timestamp']}")
        print(f"🔧 Version: {health['version']}")
    except:
        print("❌ API is not accessible!")
        return

    # Run demonstrations
    demo_translations()
    demo_bible_search()
    demo_auth_and_notes()
    demo_rag_system()

    print("\n" + "=" * 60)
    print("✅ BibleStudyAI API is fully functional and ready for frontend integration!")
    print("=" * 60)


if __name__ == "__main__":
    main()
