import requests
import json

questions = [
    # Class 1-2
    ("Allah kaun hai?", "Class 1-2"),
    ("Hazrat Muhammad kaun the?", "Class 1-2"),
    ("Sach bolna kyun zaroori hai?", "Class 1-2"),
    ("Kalima kya hai?", "Class 1-2"),
    
    # Class 3-4
    ("Islam ke kitne arkan hain?", "Class 3-4"),
    ("Quran Majeed kab nazil hua?", "Class 3-4"),
    ("Amanat kya hai?", "Class 3-4"),
    ("Wuzu ka tarika kya hai?", "Class 3-4"),
    
    # Class 5-6
    ("Roza kyun zaroori hai?", "Class 5-6"),
    ("Zakat ki importance kya hai?", "Class 5-6"),
    ("Hajj kya hai?", "Class 5-6"),
    ("Surah Fatiha mein kya likha hai?", "Class 5-6"),
    
    # Class 7-8
    ("Ghazwa Uhud mein kya sikh milti hai?", "Class 7-8"),
    ("Ghazwa Badr kya tha?", "Class 7-8"),
    ("Ghazwa Khandaq mein kya hua?", "Class 7-8"),
    ("Anbiya kaun the?", "Class 7-8"),
    
    # Class 9-10
    ("Khulafa-e-Rashideen kaun kaun the?", "Class 9-10"),
    ("Hijrat ka kya matlab hai?", "Class 9-10"),
    ("Farishte kaun hain?", "Class 9-10"),
    ("Aasmani Kitaabon ke naam?", "Class 9-10"),
    
    # Class 11-12
    ("Isra aur Miraj kya tha?", "Class 11-12"),
    ("Halal aur Haram ka farak kya hai?", "Class 11-12"),
    ("Tayammum kya hai?", "Class 11-12"),
]

print("\n" + "="*80)
print("COMPREHENSIVE ISLAMIYAT CHATBOT TEST - FINAL VERIFICATION")
print("="*80 + "\n")

answered = 0
fallback = 0

for q, level in questions:
    try:
        r = requests.post('http://127.0.0.1:5000/api/chat', json={'message': q})
        resp = r.json()['response']
        
        # Check if it's a fallback response
        is_fallback = 'database mein nahi mila' in resp
        if is_fallback:
            fallback += 1
            status = "❌"
        else:
            answered += 1
            status = "✅"
        
        preview = resp[:75].replace('\n', ' ')
        print(f"{status} [{level}] {q}")
        print(f"   → {preview}...\n")
    except Exception as e:
        print(f"❌ [{level}] {q} - ERROR: {str(e)}\n")
        fallback += 1

print("="*80)
print(f"✅ PASSED: {answered}/{len(questions)} questions answered correctly")
print(f"❌ FALLBACK: {fallback}/{len(questions)} need more handlers")
success_rate = int((answered/len(questions)) * 100)
print(f"📊 Success Rate: {success_rate}%")
print("="*80)
