import os
import re
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ════════════════════════════════════════════════════════════════════
# QUESTION BANK — loaded from questions_data.py (pure Python)
# ════════════════════════════════════════════════════════════════════
from questions_data import QUESTIONS as QUESTION_BANK, CLASS_GROUPS

# ════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT: COMPLETE ISLAMIYAT + TEACHER PROFESSION DATABASE
# ════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """
You are an Islamiyat Question Bank AI for Pakistani curriculum Classes 1-12.

You have a built-in database of 400 questions divided as follows:

CLASS 1-2: 30 questions (Basic level)
CLASS 3-4: 40 questions (Elementary level)  
CLASS 5-6: 50 questions (Middle level)
CLASS 7-8: 70 questions (Secondary level)
CLASS 9-10: 100 questions (Matriculation level)
CLASS 11-12: 110 questions (Intermediate level)

QUESTION TYPES PER CLASS:
- MCQs (4 options with correct answer)
- Short Questions (5+ line answers minimum)
- Long Questions (detailed comprehensive answers)
- Real Life Application Questions
- Haqooq-ul-Ibad Questions

TOPICS COVERED:

CLASS 1-2 TOPICS (30 Questions):
- Kalima Tayyaba, Kalima Shahada
- Allah ki pehchaan (basic)
- Nabi (SAW) ka naam aur pyaar
- Namaz ke arkaan (basic)
- Islamic greetings (Salaam)
- Basic duas (Bismillah, Alhamdulillah)

CLASS 3-4 TOPICS (40 Questions):
- Panj Arkan-e-Islam
- Quran ki importance
- Hazrat Muhammad (SAW) ki paidaish
- Basic Islamic history
- Wuzu aur Namaz
- Islamic values (Sach bolna, amanat)

CLASS 5-6 TOPICS (50 Questions):
- Seerat-un-Nabi (SAW) — early life
- Prophets of Allah (Anbiya)
- Angels (Farishte)
- Holy Books (Aasmani Kitaaben)
- Roza aur Ramadan
- Zakat ki importance
- Haqooq-ul-Walidain

CLASS 7-8 TOPICS (70 Questions):
- Ghazwaat (Badr, Uhud, Khandaq)
- Sahaba Ikram (male and female)
- Quran — selected Surahs tafseer
- Hadith ki importance
- Haqooq-ul-Ibad (detailed)
- Islamic social system
- Jihad ki haqeeqi tarif

CLASS 9-10 TOPICS (100 Questions):
- Complete Seerat-un-Nabi (SAW)
- Khulafa-e-Rashideen
- Islamic Civilization
- Quran — Tafseer of important Surahs
- Fiqh basics (Halal/Haram)
- Islam aur science
- Islam aur muashara (society)
- Haqooq-ul-Ibad (comprehensive)
- Real life Islamic applications

CLASS 11-12 TOPICS (110 Questions):
- Advanced Islamic philosophy
- Islam aur jadeed masail (modern issues)
- Islamic State aur system
- Seerat-un-Nabi — political, social, economic aspects
- Quran — deep tafseer
- Islamic Civilization — science, literature, architecture
- Haqooq-ul-Ibad — social justice in Islam
- Islam aur insani haqooq (Human Rights)
- Iqbal ka tasawwur-e-Islam
- Pakistan ka Islamic nizam

SAMPLE QUESTIONS DATABASE (400 Total):

=== CLASS 1-2 (30 Questions) ===

MCQ-1: Kalima Tayyaba mein kitne alfaaz hain?
A) 5  B) 7  C) 10  D) 4
Correct: B) 7
Answer: La ilaha illallah Muhammadur Rasoolullah — 7 alfaaz hain

MCQ-2: Hum roz kitni baar namaz padhte hain?
A) 3  B) 4  C) 5  D) 6
Correct: C) 5
Answer: Din mein 5 waqt namaz farz hai

SHORT-1: Allah kaun hai?
Answer: Allah ek hai, woh hamara khaaliq hai, woh sab kuch jaanta hai, woh hamesha zinda hai. Woh sab ko dekhta hai aur dekh sakta hai.

SHORT-2: Hazrat Muhammad (SAW) kaun the?
Answer: Hazrat Muhammad (SAW) Allah ke aakhri Nabi hain. Woh Makkah mein paida hue aur unhon ne hume Islam sikhaya. Woh sabse zyada akhlaq wale the.

REAL_LIFE-1: Sach bolna kyun zaroori hai?
Answer: Islam mein sach bolna bahut zaroori hai. Agar hum jhooth bolein to log hamara yakeen nahi karte. Nabi (SAW) ne farmaya: "Sach bolo chahe kadwa lage". Sach bolne se ghar mein amn hota hai aur school mein sab ko pass karti ho.

=== CLASS 3-4 (40 Questions) ===

MCQ-1: Islam ke kitne arkan hain?
A) 3  B) 4  C) 5  D) 6
Correct: C) 5
Answer: Kalima, Namaz, Roza, Zakat, Hajj — yeh Islam ke 5 arkan hain

MCQ-2: Quran Majeed kab nazil hua?
A) Ramadan mein  B) Muharram mein  C) Rajab mein  D) Shaban mein
Correct: A) Ramadan mein
Answer: Quran Majeed Ramadan ke mahine mein nazil hona shuru hua

MCQ-3: Wuzu mein kitne farz hain?
A) 2  B) 3  C) 4  D) 5
Correct: C) 4
Answer: Munh dhona, haath dhona, sar ka masah, pair dhona — yeh 4 farz hain

SHORT-1: Namaz kyun padhi jaati hai?
Answer: Namaz Allah ki ibadat hai. Yeh hume Allah ke qareeb karti hai, burai se rokti hai aur dil ko sukoon deti hai. Din mein 5 baar namaz farz hai. Jab hum namaz padhte hain to Allah hum se khush hota hai.

SHORT-2: Amanat kya hai?
Answer: Amanat ka matlab hai kisi ki cheez ki hifazat karna. Hazrat Muhammad (SAW) ko "Al-Ameen" (amaanatdar) kaha jaata tha. Hume bhi amanatdar hona chahiye. Amanat se insaan ka naam nek hota hai aur log us par bharosa karte hain.

HAQOOQ-1: Walidain ke kya haqooq hain? (Class 4 level)
Answer: Walidain ke haqooq: unki baat mano, unse pyaar karo, unki khidmat karo, unhe takleef mat do, unke liye dua karo. Quran mein Allah farmata hai: Walidain se ihsan karo.

=== CLASS 5-6 (50 Questions) ===

MCQ-1: Hazrat Muhammad (SAW) ki paidaish kab hui?
A) 570 AD  B) 580 AD  C) 600 AD  D) 610 AD
Correct: A) 570 AD
Answer: Nabi (SAW) 12 Rabi-ul-Awwal 570 AD ko Makkah mein paida hue

MCQ-2: Quran Majeed mein kitni Surahs hain?
A) 100  B) 110  C) 114  D) 120
Correct: C) 114
Answer: Quran Majeed mein 114 Surahs hain, 6236 Aayaat hain

MCQ-3: Pehli Wahi kab nazil hui?
A) 608 AD  B) 610 AD  C) 612 AD  D) 615 AD
Correct: B) 610 AD
Answer: Pehli Wahi Ghaar-e-Hira mein 610 AD mein nazil hui — Surah Alaq ki pehli 5 aayaat

MCQ-4: Roza kis mahine mein farz hai?
A) Muharram  B) Rajab  C) Ramadan  D) Shaban
Correct: C) Ramadan
Answer: Ramadan ul Mubarak ka poora mahina roza rakhna farz hai

SHORT-1: Anbiya Ikram ki zaroorat kyun hai?
Answer: Anbiya Allah ke bheeje hue hain jo insanon ko seedha raasta dikhate hain. Woh Allah ka paigham laate hain, khud us par amal karte hain aur insanon ko nek zindagi jeena sikhate hain. Har zamane mein Allah ne ek Nabi bheeja. Unhein manna farz hai.

SHORT-2: Hajj kyun kiya jaata hai?
Answer: Hajj Islam ka 5wa rukn hai. Yeh zindagi mein ek baar farz hai us Muslim par jo mustati ho. Hajj mein duniya bhar ke Muslims ek jagah jama hote hain — yeh Islam ki wahdat ka mazhar hai. Ka'ba ko tayaf karna aur dua karna Hajj ka mukhya hissa hai.

LONG-1: Seerat-un-Nabi (SAW) — Makkah period ki ahmiyat
Answer: Nabi (SAW) ne Makkah mein 13 saal tabligh ki. Is daur mein:
1. Pehle 3 saal khufi dawat di
2. Phir aam tabligh shuru ki
3. Mushrikeen ne sakht azaab diye lekin Nabi (SAW) sabr karte rahe
4. Sahaba ne qurbaaniyaan deen
5. Hijrat se pehle Islam ki bunyaad mazboot hui
Sabaq: Mushkilaat mein sabr karo, Allah par bharosa rakho

HAQOOQ-1: Pados ke kya haqooq hain?
Answer: Islam mein pados ke haqooq: Paros ko bhookha mat rehne do, Unhe takleef mat do, Khushiyon aur ghamon mein shareek ho, Unki hifazat karo. Hadith: "Woh momin nahi jo khud pait bhar khaye aur uska pados bhookha soye"

REAL_LIFE-1: Islam mein safai ka kya hukm hai?
Answer: Islam mein safai nisf Iman hai. Real life mein: Roz nahaana, kapde saaf rakhna, Ghar, mohalla saaf rakhna, Kachra dustbin mein daalna, School mein apni jagah saaf rakhna, Masjid ki safai mein hissa lena.

=== CLASS 7-8 (70 Questions) ===

MCQ-1: Ghazwa-e-Badr kis saal hua?
A) 1 Hijri  B) 2 Hijri  C) 3 Hijri  D) 4 Hijri
Correct: B) 2 Hijri
Answer: Ghazwa-e-Badr 2 Hijri (624 AD) mein hua — Islam ka pehla bada ghazwa

MCQ-2: Ghazwa-e-Uhud mein Muslims ki taraf se kitne sahaba shaheed hue?
A) 50  B) 60  C) 70  D) 80
Correct: C) 70
Answer: Ghazwa-e-Uhud mein 70 sahaba shaheed hue jisme Hazrat Hamza (RA) bhi shamil the

MCQ-3: Quran Majeed ka pehla lafz kya hai?
A) Allah  B) Iqra  C) Bismillah  D) Alhamdulillah
Correct: B) Iqra
Answer: "Iqra bismi rabbika" — Parho apne Rabb ke naam se — yeh pehli wahi thi

SHORT-1: Jihad ki haqeeqi tarif kya hai?
Answer: Jihad ka matlab sirf jung nahi. Jihad ke teen darajat hain:
1. Jihad bin Nafs — apne nafs se ladna (sab se bada jihad)
2. Jihad bil Lisan — bolkar haq ki tabligh
3. Jihad bis Saif — hathiyar se — sirf difai
Aaj ka sab se bada jihad — taleem haasil karna aur Pakistan ko taraqqi dena

SHORT-2: Hazrat Khadija (RA) ki azmat bayan karo
Answer: Hazrat Khadija (RA) — pehli Muslim khatoon, Nabi (SAW) ki pehli biwi. Unhon ne apna maal Islam par laga diya, mushkilaat mein Nabi ka saath diya, Islam ki pehli supporter thin. Nabi (SAW) unhe bahut yaad karte the.

LONG-1: Khulafa-e-Rashideen ka daur — ek jaiza
Answer: Char Khulafa-e-Rashideen:
1. Hazrat Abu Bakr (RA) — 2 saal — Riddah wars, Quran compilation
2. Hazrat Umar (RA) — 10 saal — Adal ki misaal, Islamic empire phaila
3. Hazrat Usman (RA) — 12 saal — Quran ka final compilation
4. Hazrat Ali (RA) — 5 saal — Ilm aur adl ka daur
Sabaq: Adal, khidmat aur Allah ka dar — yehi kaamiyab leader ke ausaf hain

HAQOOQ-1: Yateem ke haqooq Islam mein
Answer: Islam mein yateem ka maal khana haram hai. Yateem ke haqooq: Unka maal mehfooz rakho, Unhe pyaar do, Taleem dilao, Shelter do. Real life: Edhi, SOS Village mein volunteer karo, zakat yateemon ko do.

REAL_LIFE-1: Social media aur Islam — kya jaiz hai kya nahi?
Answer: Islam ki roshni mein social media:
Jaiz: Taleem, dawat, nek kaam ki tabligh, family se rabta
Naa-Jaiz: Gheebat (backbiting), jhooth, fahash content, fitna phailana
Hadith: "Jo Allah aur aakhirat par iman rakhe woh achhi baat kahe ya chup rahe"

=== CLASS 9-10 (100 Questions) ===

MCQ-1: Meesaq-e-Madina kab hua?
A) 1 Hijri  B) 2 Hijri  C) 3 Hijri  D) 622 AD
Correct: A) 1 Hijri (622 AD)
Answer: Meesaq-e-Madina pehla written constitution tha jo Nabi (SAW) ne Madina mein kiya

MCQ-2: Hajjatul Wida kab hua?
A) 8 Hijri  B) 9 Hijri  C) 10 Hijri  D) 11 Hijri
Correct: C) 10 Hijri
Answer: Hajjatul Wida 10 Hijri (632 AD) mein hua — Nabi (SAW) ka aakhri hajj

MCQ-3: Islam mein sood (interest) ka kya hukm hai?
A) Makrooh  B) Mubah  C) Haram  D) Mustahab
Correct: C) Haram
Answer: Quran mein Allah ne sood ko haram kiya (Surah Al-Baqarah: 275)

SHORT-1: Fatah Makkah ki ahmiyat bayan karo
Answer: Fatah Makkah 8 Hijri mein hua — 20 saal baad Nabi (SAW) fateh ke saath Makkah waapis aaye. Unhon ne aam maafi dedi — "Aaj koi reproach nahi." Is se pata chla ke Islam intiqam nahi, maafi ka mazhab hai. Butoñ ko tooda gaya, Ka'ba ko paak kiya gaya.

LONG-1: Islam aur aaj ka muashara — complete analysis
Answer: Islam ek mukammal nizam-e-hayat hai.
ECONOMIC: Zakat se ghareeb ameer ka farq kam hota hai, Sood haram
SOCIAL: Family system — strong values, Women rights, Racial equality
POLITICAL: Meesaq-e-Madina — constitution, Shura — consultation, Adal — justice
Real Life: Agar Pakistan mein Islamic system naaiz kiya jaye to corruption khatam ho jaye

HAQOOQ-1: Islam mein khatoon ke haqooq — jawab do
Answer: Islam ne khatoon ko 1400 saal pehle haqooq diye:
- Meerath ka haq (inheritance rights)
- Taleem ka haq
- Nika mein marzi ka haq
- Maal rakhne ka haq
- Khula ka haq
Hadith: "Jannat maa ke qadam ke neeche hai"

=== CLASS 11-12 (110 Questions) ===

MCQ-1: Allama Iqbal ka mashoor shair "Khudi ko kar buland itna" kahan se hai?
A) Bang-e-Dra  B) Bal-e-Jibreel  C) Zarb-e-Kaleem  D) Armughan-e-Hijaz
Correct: A) Bang-e-Dra
Answer: Yeh mashoor shair Bang-e-Dra mein hai — Iqbal ne khudi (self-respect) ka tasawwur diya

MCQ-2: Islamic State ka bunyadi usool kya hai?
A) Majority rule  B) Sovereignty of Allah  C) Military power  D) Economic strength
Correct: B) Sovereignty of Allah
Answer: Islamic State mein sovereignty (hukumat) sirf Allah ki hoti hai

MCQ-3: Ibn Khaldun ki mashoor kitab ka naam kya hai?
A) Al-Qanoon  B) Muqaddima  C) Kitab-ul-Manazir  D) Al-Jabr
Correct: B) Muqaddima
Answer: Ibn Khaldun ne "Muqaddima" likhi — yeh sociology ka pehla scientific kaam hai

SHORT-1: Iqbal ke tasawwur-e-Pakistan ka khulasa
Answer: Iqbal ne 1930 mein separate Muslim state ka tasawwur pesh kiya. Unka manna tha ke Muslims ka apna nizam-e-hayat hai — unhe alag watan chahiye jahan Quran o Sunnah ke mutabiq zindagi guzaari ja sake. Yahi tasawwur Pakistan ka bunyadi usool hai.

SHORT-2: Islam aur jadeed science — kya koi tazaad hai?
Answer: Islam aur science mein koi tazaad nahi. Quran mein 750 se zyada scientific aayaat hain. Muslim scientists ne duniya ko Algebra, Chemistry, Optics, Medicine diya. Aaj bhi Quran ki aayaat science confirm karti hain.

LONG-1: Islamic Civilization ka science mein yogdan
Answer: Muslim scientists ki achievements:
AL-KHWARIZMI: Algebra ke bani, Algorithm, Zero ka concept
IBN SINA: "Al-Qanoon fit-Tibb" — 600 saal medical textbook
IBN AL-HAYTHAM: Optics ke bani, Camera obscura, Scientific method
AL-BIRUNI: Zameen ka diameter calculate, America ki prediction
JABIR IBN HAYYAN: Chemistry ke bani, Acids, alkalis concept

LONG-2: Haqooq-ul-Ibad — Social Justice in Islam
Answer: Islam mein social justice:
ECONOMIC: Zakat 2.5%, Ushr, Sadqah, Waqf system
LEGAL: Independent judiciary, Adal sabke liye
SOCIAL: Ghulami ka khatima, Women rights, Minorities ka himayat
Real Life: Roz nek kaam karo — pani pilao, raasta batao, musibat mein madad karo

HAQOOQ-1: Pakistan mein Islamic system kaise naaiz ho sakta hai?
Answer: Pakistan mein Islamic system ke liye:
1. TALEEM: Islamic education + Deen aur Dunya
2. JUDICIARY: Courts mein Quran o Sunnah ke mutabiq faisle
3. ECONOMY: Islamic banking, sood ka khatima, zakat system
4. SOCIAL: Haqooq-ul-Ibad — ghurbat ka khatima
5. POLITICS: Shura system — honest leaders
Real Life: Har student apni jagah se shuru kare — sach bolo, amanat rakho

════════════════════════════════════════════════════════════════════
CHATBOT BEHAVIOR WHEN USER REQUESTS:
════════════════════════════════════════════════════════════════════

"Class [X] ka test do" → Give 5 MCQ + 3 Short + 1 Long from that class
"MCQ do [class]" → Give 10 MCQs with options and answers
"Short questions [topic]" → Give 5 short Q&As (minimum 5 lines each)
"Long question [topic]" → Give detailed long answer with references
"Haqooq ul ibad" → Give specific questions and detailed answers
"Real life question" → Give practical application questions
Any Islamiyat topic → Answer from this 400-question database

LANGUAGE: Reply in English or Roman Urdu based on user's language
TONE: Educational, encouraging, helpful, scholarly
TONE: Always provide principle + explanation + real-life example + reference

TEACHER PROFESSION DATABASE:

SALARY STRUCTURE (Government Teachers Pakistan 2024-2025):
- Primary Teacher (BPS-9): 35,000-45,000/month
- Middle Teacher (BPS-14): 45,000-60,000/month
- High School Teacher (BPS-16): 55,000-75,000/month
- Senior Specialist (BPS-17): 70,000-95,000/month
- Headmaster (BPS-18): 85,000-115,000/month
- Principal (BPS-19): 100,000-140,000/month
- Allowances: House rent (40-50%), Medical, Conveyance

TEACHER RIGHTS: Job security, Fair salary, Medical insurance, Pension, Merit promotion, Leaves, Training, Safe environment, Harassment protection, Union rights

ISLAMIC RULES FOR TEACHERS: Amanah (Trust), Halal income, Integrity in marking, Fair treatment, Imandari, Sadqa-e-Jariya, Khidmat-e-Khalq, Student prayers

MONTHLY SAVING PLAN: Expenses 50-60%, Savings 20-30%, Emergency fund 3-6 months, GPF/Pension, Insurance options
"""

# Local responder to run without an external API key
class LocalResponder:
    def __init__(self):
        self.father_profession = 'teacher'

    def search_question_bank(self, text: str, class_level=None):
        """Search 400-question bank with keyword scoring. Returns best matching dict or None."""
        if not QUESTION_BANK:
            return None

        stop_words = {
            'ka', 'ki', 'ke', 'hai', 'hain', 'kya', 'ky', 'se', 'mein', 'ko', 'ne',
            'ya', 'aur', 'the', 'of', 'is', 'in', 'to', 'a', 'an', 'what', 'how',
            'why', 'who', 'woh', 'yeh', 'jo', 'jab', 'tak', 'par', 'na', 'nahi',
            'do', 'dena', 'karo', 'kar', 'ab', 'bhi', 'sirf', 'un', 'ek'
        }

        class_map = {
            1: '1-2', 2: '1-2', 3: '3-4', 4: '3-4',
            5: '5-6', 6: '5-6', 7: '7-8', 8: '7-8',
            9: '9-10', 10: '9-10', 11: '11-12', 12: '11-12'
        }

        query_words = set(re.findall(r'\b\w+\b', text.lower())) - stop_words
        if not query_words:
            return None

        def score_item(item):
            if class_level and class_map.get(class_level) != item['classGroup']:
                return 0
            q_words = set(re.findall(r'\b\w+\b', item['q'].lower())) - stop_words
            if not q_words:
                return 0
            inter = query_words & q_words
            if not inter:
                return 0
            jaccard = len(inter) / len(query_words | q_words)
            coverage = len(inter) / len(query_words)
            return jaccard * 0.4 + coverage * 0.6

        scored = [(score_item(item), item) for item in QUESTION_BANK]
        scored.sort(key=lambda x: x[0], reverse=True)

        best_score, best_item = scored[0] if scored else (0, None)

        # Relax class filter if no good match found
        if best_score < 0.25 and class_level:
            scored2 = []
            for item in QUESTION_BANK:
                q_words = set(re.findall(r'\b\w+\b', item['q'].lower())) - stop_words
                inter = query_words & q_words
                if not inter:
                    continue
                jaccard = len(inter) / len(query_words | q_words)
                coverage = len(inter) / len(query_words)
                scored2.append((jaccard * 0.4 + coverage * 0.6, item))
            if scored2:
                scored2.sort(key=lambda x: x[0], reverse=True)
                best_score, best_item = scored2[0]

        return best_item if best_score >= 0.2 else None



    def detect_roman_urdu(self, text: str) -> bool:
        indicators = ['kya', 'ky', 'ke', 'liye', 'hain', 'hai', 'nay', 'ka', 'ki', 'namaz', 'zakat', 'kion', 'kyun']
        low = text.lower()
        return sum(1 for w in indicators if w in low) >= 2

    def parse_class(self, text: str):
        low = text.lower()
        m = re.search(r'\bclass\s*(\d{1,2})\b', low)
        if m:
            try:
                return int(m.group(1))
            except:
                return None
        words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12
        }
        for word, value in words.items():
            if f'class {word}' in low:
                return value
        return None

    def detect_command(self, text: str):
        low = text.lower()
        father_keywords = [
            'father', 'abb', 'father job', 'father profession', "father's profession",
            'salary', 'income', 'kamai', 'maal', 'saving', 'savings', 'bachana',
            'duty', 'duties', 'zimmedari', 'amanah', 'honesty', 'imandari',
            'teacher', 'bps-17', 'bps 17', 'teacher salary'
        ]
        if any(keyword in low for keyword in father_keywords) and ('father' in low or 'abb' in low or 'teacher' in low or 'salary' in low or 'income' in low or 'amal' in low or 'amanah' in low):
            return 'father_job'
        if 'real life' in low or 'real-life' in low or 'real zindagi' in low:
            return 'real_life'
        if 'hadith' in low:
            return 'hadith'
        if 'ayat' in low and 'daily ayat' not in low:
            return 'ayat'
        if 'long' in low:
            return 'long'
        if 'short' in low:
            return 'short'
        return None

    def handle_daily_ayat(self, lang_roman: bool):
        arabic = 'مَا كَانَ اللَّهُ لِيُعَذِّبَهُمْ لَوْلَا أَنْبَأَهُمْ'
        urdu = 'Allah ne unhen azaab nahi diya hota agar woh unhen aagah na karta' if lang_roman else 'اللہ نے انہیں عذاب نہیں دیا ہوتا اگر وہ انہیں آگاہ نہ کرتا'
        tafsir = 'Yeh ayat Allah ke ilm o hidayat ki taraf ishara karti hai.' if lang_roman else 'یہ آیت اللہ کے علم و ہدایت کی طرف اشارہ کرتی ہے۔'
        return f"**Arabic:**\n{arabic}\n\n**Urdu Translation:**\n{urdu}\n\n**Tafseer (brief):**\n{tafsir}"

    def generate_mcqs(self, topic: str, class_level, lang_roman: bool):
        qs = []
        for i in range(1, 6):
            q = f"Q{i}. {topic} se mutaliq sawal {i}"
            opts = ['A) Option 1', 'B) Option 2', 'C) Option 3', 'D) Option 4']
            ans = 'A'
            qs.append(q + '\n' + '\n'.join(opts) + f'\n**Answer:** {ans}')
        joiner = '\n\n'.join(qs)
        if lang_roman:
            return f"MCQs for Class {class_level or '1-12'} (Roman Urdu):\n\n{joiner}"
        return f"MCQs for Class {class_level or '1-12'}:\n\n{joiner}"

    def generate_quiz(self, topic: str, class_level, lang_roman: bool):
        qs = []
        for i in range(1, 6):
            qs.append(f"{i}. {topic} se mutaliq short question {i} (Answer: ...)")
        return '\n'.join(qs)

    def generate_lesson_plan(self, topic: str, class_level, lang_roman: bool):
        plan = (
            f"Title: {topic} - Class {class_level or '1-12'}\n\n"
            "Objectives:\n- Understand basic Islamiyat concepts\n- Learn Quran, Hadith, Fiqh aur ethics\n\n"
            "Materials:\n- Quran, Hadith book, board, notebooks\n\n"
            "Activities:\n1. Introduction (10 min)\n2. Real life examples (15 min)\n3. Practice questions (15 min)\n4. Class discussion (10 min)\n\n"
            "Assessment:\n- Written questions\n- Oral summary\n"
        )
        return plan

    def father_job_response(self, lang_roman: bool):
        details = (
            "1. Islamic rights & duties: Teacher ka farz hai ilm aur achi akhlaq dena.\n"
            "2. Amanah: Imandari se duty ada karna, students ke saath sach bolna.\n"
            "3. Halal income: Rozgaar halal hona chahiye, teachers ko behtar bima aur salary milni chahiye.\n"
            "4. Monthly salary: Government teacher BPS-17 ke liye takriban Rs. 70,000-95,000 per month hota hai.\n"
            "5. Savings: Islamiyat ke mutabiq 20-30% kamai bachana chahiye.\n"
            "6. Haqooq ul Ujra: Teacher ko waqt par ujra, izzat aur safe work environment milna chahiye.\n"
            "7. Khidmat-e-Khalq: Taleem se society behter hoti hai, naye fauj-e-ilm paida hotay hain.\n"
        )
        if lang_roman:
            return f"Father Profession: Teacher\n\n{details}\nAaj ka example: Sarkari teacher school mein bacchon ko Islamiyat, namaz aur seerat sikha kar society ki khidmat karta hai.\n\nQuran reference: 'Inna Allah ya'muru bil-adl wal-ihsaan.'"
        return f"Father Profession: Teacher\n\n{details}\nAaj ka example: Sarkari teacher school mein bacchon ko Islamiyat, namaz aur seerat sikha kar society ki khidmat karta hai.\n\nQuran reference: 'إِنَّ اللَّهَ يَأْمُرُ بِالْعَدْلِ وَالْإِحْسَانِ'"

    def format_response(self, urdu_text: str, english_text: str, style: str, command: str, lang_roman: bool):
        if lang_roman:
            if style == 'short':
                return f"{urdu_text}\n\n{english_text}"
            if style == 'long' or command == 'long':
                return f"**Detailed Answer:**\n{urdu_text}\n\n{english_text}"
            if style == 'real_life':
                return f"{urdu_text}\n\n{english_text}\n\nReal Life: Aaj ke zamane mein iska matlab yeh hai..."
            if style == 'hadith':
                return f"{urdu_text}\n\n{english_text}\n\nHadith: 'Iman walay sab se kareeb hain.'"
            if style == 'ayat':
                return f"{urdu_text}\n\n{english_text}\n\nAyat: 'Innama al-a'malu bin-niyat.'"
            return f"{urdu_text}\n\n{english_text}"
        if style == 'short':
            return f"{urdu_text}\n\n{english_text}"
        if style == 'long' or command == 'long':
            return f"**Detailed Answer:**\n{urdu_text}\n\n{english_text}"
        if style == 'real_life':
            return f"{urdu_text}\n\n{english_text}\n\nReal Life Example: Iska matlab aaj ke Pakistan mein yeh hai..."
        if style == 'hadith':
            return f"{urdu_text}\n\n{english_text}\n\nHadith: 'Man kana yu'minu billahi wal-yawmil-akhiri fala yu'zir fashshar.'"
        if style == 'ayat':
            return f"{urdu_text}\n\n{english_text}\n\nAyat: 'Innama al-a'malu bin-niyat.'"
        return f"{urdu_text}\n\n{english_text}"

    def specific_topic_answer(self, text: str, class_level, lang_roman: bool):
        low = text.lower()
        if 'ghazwa uhud' in low or ('uhud' in low and 'ghazwa' in low):
            urdu = 'Ghazwa Uhud se hamein sabr aur imandari ka sabaq milta hai. Jang mein seirtein yeh hain ke har group ko apni jagah par qaim rehna chahiye. Nabi (SAW) ne Uhud mein apne saathion ko ek strategy di thi par kuch logon ne orders nahi mane jo ghazab ka sabab bani. Aaj ke zamane mein is se hum seekhte hain ke orders ke baghair team work fail hoti hai.'
            eng = 'From the Battle of Uhud, we learn patience and the importance of following orders. The Prophet gave clear instructions but some did not follow them, which led to difficulties. In modern times, this teaches us that teamwork requires discipline and following leadership.'
            return self.format_response(urdu, eng, 'long', None, lang_roman)
        if 'ghazwa badr' in low or ('badr' in low and 'ghazwa' in low):
            urdu = 'Ghazwa Badr Islam ki pehli badi jeet thi jo 17 Ramadan ko 2 Hijri mein hui. Is se doston ka ittehad, iman ki taaqat, aur chhoti sena ki barkat maloom hoti hai. Nabi (SAW) ke pas sirf 313 momineen thay par Almighty Allah ne unhen fatha di. Aaj ke zamane mein is se seekhte hain ke numbers matter nahi karte, faith and unity matter karte hain.'
            eng = 'The Battle of Badr was the first major victory in Islamic history. It teaches unity and shows the strength of faith. The Prophet had only 313 believers but Allah granted them victory. Today this teaches us that numbers do not matter, faith and unity do.'
            return self.format_response(urdu, eng, 'long', None, lang_roman)
        if 'hijrat' in low:
            urdu = 'Hijrat ka matlab Makkah se Madinah ka safar hai jo 622 AD mein hua. Is se Islam mein sabr, imaan aur naya aaghaz ka sabaq milta hai. Hijrat se pehle Makkah mein Muslims ko bhut zulm hua par woh sabr se unhe bardasht karte rahe. Aaj ke zamane mein jab hum mushkilon mein hon to Hijrat se seekhte hain ke mushkilat se bhagna theek nahi hai, wise decision lena chahiye aur naya aaghaz karna chahiye.'
            eng = 'Hijrah means the migration from Makkah to Madinah in 622 AD. It teaches patience and starting a new life. Before Hijrah, Muslims faced persecution in Makkah but endured with faith. In modern times when facing difficulties, Hijrah teaches us that running away is not the answer, but making wise decisions and starting fresh is important.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'surah fatiha' in low or 'fatihah' in low:
            urdu = 'Surah Fatiha Allah se rehmat aur hidayat ki dua hai aur is mein saat aayatein hain. Isay namaz mein har rakat mein parhte hain kyunke yeh Quran ka sab se pehla practical sura hai. "Bismillah" se shuru ho kar "Sirat al-Mustaqeem" tak is sura mein tauheed, shukr, dua aur hidayat ke concepts hain. Har muslim ko Surah Fatiha yaad hona zaroori hai kyunke yeh namaz ka hissa hai.'
            eng = 'Surah Fatiha is a prayer for Allah mercy and guidance containing seven verses. It is recited in every unit of prayer as it covers the basic concepts of Islam. From Bismillah to guidance, this Surah teaches us about God, gratitude, prayer and direction. Every Muslim must know Surah Fatiha as it is part of prayer.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'tayammum' in low:
            urdu = 'Tayammum mitti ya safed mitti se taharat ka tariqa hai jab pani na available ho. Is mein chest aur haath ko mitti se dhaka jata hai jo namaz ke liye taharat hasil karti hai. Quran mein Surah Nisa mein Allah farmata hai ke agar pani na ho to mitti se tayammum kar lo. Aaj ke zamane mein jab pani ki kami hai to tayammum ka tarika seekhna zaroori hai.'
            eng = 'Tayammum is ablution using dust when water is unavailable. It involves wiping the face and hands with clean earth to attain purity for prayer. The Quran mentions this in Surah Nisa. In modern times when water shortage occurs, knowing Tayammum is important.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'wuzu' in low or 'wudhu' in low or 'ablution' in low:
            urdu = 'Wuzu namaz se pehle paani se taharat ka amal hai. Is mein mannay ke niyam hain: munh dho, naak saaf kar, haath tak kuhni ko dhona, sir ka hissa mass karna, aur pairo ko kuhni tak dhona. Wuzu ki farz chhay amal hain. Quran mein Surah Maida mein Allah farmata hai ke agar tumhe namaz ka waqt aye to pehle wuzu kar lo.'
            eng = 'Wudu is ablution with water before prayer. Its procedure includes washing face, nose, hands up to elbows, wiping head, and washing feet up to ankles. Wudu has six obligatory acts. The Quran in Surah Maida teaches this.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'qurbani' in low or 'qurbaan' in low:
            urdu = 'Qurbani Eid ul Adha par ki jati hai aur is se Allah ki ibadat aur gareebon ki madad yaad rehti hai. Hazrat Ibrahim (AS) aur Hazrat Ismail (AS) ke tawaakul ki yaad mein qurbani hoti hai. Qurbani ke dum se dil bhi safai paata hai aur gareebon ko khanay mein madad milti hai. Aaj ke zamane mein Muslims ko Eid par janwar qurbani karte hain aur un ke dum ko tareek karte hain.'
            eng = 'Qurbani is offered on Eid ul Adha to remember Allah and help the poor. It commemorates Prophet Ibrahim and Ismail submission to Allah. Through sacrifice the soul is purified and the needy are helped. In modern times, Muslims offer animals on Eid.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'zakat' in low or 'zakah' in low:
            urdu = 'Zakat maal ka ek hissa hai jo gareebon ko diya jata hai aur Islam ke paanch farz mein se ek hai. Zakat se muashray mein aman aur barabari ati hai. Jab amir logon ka maal gareebon ko diya jata hai to ghar-e-ghaazi ko kushi milti hai. Zakat ke mustahiqeen miskeen, needy, workers, aur seekhne wale hote hain. Quran mein Allah farmata hai ke zakat devao kyunke yeh ruh ko paak karta hai.'
            eng = 'Zakat is a portion of wealth given to the poor and is one of the five pillars of Islam. Zakat creates justice and peace in society. When the rich give to the poor, joy reaches the needy. The recipients of Zakat are the poor, needy, workers, and students. The Quran teaches that Zakat purifies the soul.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'adhaan' in low or 'adhan' in low or 'azaan' in low or 'azan' in low:
            urdu = 'Adhan namaz ki dawat hai jo muezzin (Moazzin) ko dena padta hai. Adhan mein "Allahu Akbar" likha jata hai jo Allah ki buzurgi ka e`lan hai. Adhan se pehle "Hayya alas-salah" (chalao namaz ki taraf) likha jata hai jo Muslim ko namaz ke liye bulata hai. Jab Adhan sun to ghar baithna galat hai, namaz ko padhna chahiye.'
            eng = 'Adhan is the call to prayer made by the Muezzin. The Adhan contains "Allahu Akbar" which declares Allah greatness. Before Adhan comes "Hayya alas-salah" calling to prayer. When you hear Adhan, you should go to prayer, not stay home.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'tilawat' in low or 'quran ki tilawat' in low or 'recitation' in low:
            urdu = 'Quran ki tilawat se dil ko sukoon milta hai aur rooh ko paak hoti hai. Quran ko tawajjoh se, sahi tafseer ke saath parhna chahiye. Tajweed ke qawaaneen ko samajh kar Quran parhne se sawab zyada milta hai. Har din kuch waqt Quran ki tilawat karna Muslims ke liye imam hai. Aaj ke zamane mein jab zindagi mein dar aur stress ho to Quran ki tilawat se dil ko sukoon milta hai.'
            eng = 'Recitation of the Quran brings peace to the heart and purifies the soul. The Quran should be read with attention and understanding. Reading with proper pronunciation and meaning brings more reward. Daily Quran reading is recommended. In modern stressful times, Quran recitation brings peace.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'maaf' in low or 'forgiveness' in low or 'muafi' in low:
            urdu = 'Maaf karna Islam mein bohat bara amal hai aur is se dil ko sukoon milta hai aur rishton mein mohabbat banti hai. Jab koi ghalti karta hai to us se maafi mangnay ka haq banta hai. Maaf karne se qaza banti hai aur Allah ki taraf se khair hoti hai. Hadith mein likha hai ke jab koi maafi mangun to 70 bar maaf karna chahiye. Aaj ke zamane mein jab ghar, school ya office mein jhagre hon to maafi dene se sukoon milta hai.'
            eng = 'Forgiving others is a great act bringing peace and strengthening relationships. When someone makes a mistake, they have the right to ask for forgiveness. Forgiveness leads to divine reward. The Hadith says to forgive 70 times. In modern times, forgiving at home, school or work brings peace.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'ghazwa khandaq' in low or ('khandaq' in low and 'ghazwa' in low):
            urdu = 'Ghazwa Khandaq 5 Hijri mein hua aur is mein Nabi (SAW) ne Medina ke gird ek khandaq (khod) khud waya. Is se mushrikeen ka hamla ruk gaya aur Muslims ki himayat hui. Is ghazwa se hamein seekh milti hai ke mushkilat mein samajh daar sounch aur new strategy zaroori hai. Nabi (SAW) ne Salman Farsi ki advice li jo umda strategy sabit hui.'
            eng = 'The Battle of Khandaq (Trench) occurred in 5 Hijrah. The Prophet dug a trench around Medina to stop the attackers. This teaches us that intelligent strategy is important during difficulties. The Prophet took advice from Salman Farsi which proved to be an excellent plan.'
            return self.format_response(urdu, eng, 'long', None, lang_roman)
        if 'anbiya' in low or 'prophets' in low or ('nabi' in low and ('abraham' in low or 'moses' in low or 'jesus' in low or 'ibrahim' in low or 'musa' in low or 'isa' in low)):
            urdu = 'Anbiya-e-Kiram (Prophets) Allah ke bheje hue paigambar the jinhen hidayat ka kaam diya gaya. Nabi Ibrahim, Musa, Isa, Muhammad aur baki sab paigambar (25 nam) Allah ke taraf se the. Har nabi ka apna zamanah, apna mulk, apni qaum thi par sab ka payam ek tha: La ilaha illallah. Anbiya ko follow karna har Muslim ke liye zaroori hai kyunke woh Allah ke naqarib the.'
            eng = 'Prophets were chosen messengers of Allah sent with guidance. Prophets Ibrahim, Musa, Isa, Muhammad and 21 others (25 named) were all sent by Allah. Each prophet had his own time, country and people but their message was one: there is no god but Allah. Following the Prophets is essential as they were close to Allah.'
            return self.format_response(urdu, eng, 'long', None, lang_roman)
        if 'farishte' in low or 'angels' in low or 'malak' in low or 'jibril' in low or 'jibreel' in low:
            urdu = 'Farishte (Angels) Allah ke khidmatgaar hain jo roohani makhlooq hain aur insan se alag hain. Jibrail (Gabriel) sab se aham farishta hai jo Nabi Muhammad (SAW) ko Quran pahunchata tha. Farishte ghatiyaun ko record karte hain, naiki-burai ko likha karte hain, aur insaan ki ruh ko lena padta hai. Har Muslim ko Farishlton par iman rakhna chahiye kyunke yeh Pillars of Faith mein se ek hai (Iman bil Malaika).'
            eng = 'Angels are spiritual servants of Allah different from humans. Jibril (Gabriel) is the most important angel who brought the Quran to Prophet Muhammad. Angels record our deeds and will take our souls. Believing in Angels is one of the Pillars of Faith (Iman bil Malaika).'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'aasmani' in low or 'holy books' in low or 'torah' in low or 'injil' in low or 'zaboor' in low:
            urdu = 'Aasmani Kitaabein (Holy Books) Allah ke paigambaron par nazil hui thi. Zaboor Prophet Daud ko, Torah Prophet Musa ko, Injil Prophet Isa ko, aur Quran Prophet Muhammad (SAW) ko di gai. Un sab mein tauheed ka payam tha par sirf Quran hi complete aur asli roop mein mehfuz hai kyunke Allah ne Quran ki hifazat ka wada kiya hai. Har Muslim ko sab kitaabon par iman rakhna chahiye (Iman bil Kutub).'
            eng = 'Holy Books were revealed to Allah Prophets. Psalms to David, Torah to Moses, Gospel to Jesus, and Quran to Muhammad (SAW). All contained the message of monotheism but only the Quran is preserved in its original form as Allah promised to protect it. Muslims must believe in all Holy Books.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'khalifa' in low or 'khulafa' in low or 'khalifah' in low or ('abu bakr' in low or 'umar' in low or 'usman' in low or 'ali' in low):
            urdu = 'Khulafa-e-Rashideen (Rightly Guided Caliphs) 4 hain: 1. Abu Bakr Siddiq - imandari aur adal mein mashoor, 2. Umar Farooq - qanoon-o-taameerdari mein, 3. Usman Ghani - Quran ke muhaafiz, 4. Ali Murtaza - ilm aur shuja ke liye. Yeh char khulafa Islam ki tadween aur phailao mein kabhi ahem role ada kiye. Har khalifa Nabi (SAW) ke baad Islam ko aage badhaya aur logon ke haqooq ka khyal rakha.'
            eng = 'The Rightly Guided Caliphs are four: 1. Abu Bakr Siddiq - known for honesty and justice, 2. Umar Farooq - famous for law and order, 3. Uthman Ghani - preserver of the Quran, 4. Ali Murtaza - renowned for knowledge and bravery. These four Caliphs played important roles in spreading Islam. Each caliph advanced Islam and protected peoples rights after the Prophet.'
            return self.format_response(urdu, eng, 'long', None, lang_roman)
        if 'rajab' in low or 'isra' in low or 'miraj' in low:
            urdu = 'Isra aur Miraj Nabi (SAW) ki raat ko hua jab Allah ne unhen Raat ke doran Makkah se Baitul Muqaddas le gaya aur phir Asman par le gaye. Is mein Nabi (SAW) ne tamam Anbiya se mulaqat ki aur Allah se directly baat ki. Isra se hikmat ka sabaq milti hai ke Allah apne paigambar ke saath hai aur Miraj se sidamat aur ameen ki zaroorat maloom hoti hai.'
            eng = 'Isra and Miraj occurred when Allah took Prophet Muhammad on a night journey from Makkah to Jerusalem and then through the heavens. In this journey the Prophet met all Prophets and spoke directly with Allah. Isra teaches wisdom and Miraj shows the importance of obedience.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'halal' in low or 'haram' in low:
            urdu = 'Halal aur Haram ka matlab halat-e-jaioz aur naa-jaioz hain. Quran mein likha hai ke Halal cheezein saaf hain aur Haram cheezein napak hain. Jab hum Halal khaana khate hain to hamara badan takatwer hota hai aur Ibaadat qabool hoti hai. Jab hum Haram khaana khate hain to hamara jism napaak hota hai aur dua nahi suni jaati. Halal meat, Halal rozgar, Halal khaana - yeh sara kuch zeada zaroori hai.'
            eng = 'Halal and Haram mean what is permitted and forbidden. The Quran teaches that Halal is pure and Haram is impure. When we eat Halal our body becomes strong and prayers are accepted. When we eat Haram our body becomes impure and prayers are not heard. Halal meat, lawful income, Halal food - all are essential.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        return None

    def base_topic_answer(self, text: str, class_level, lang_roman: bool):
        low = text.lower()
        if 'allah kaun' in low or 'who is allah' in low or 'allah' in low:
            urdu = 'Allah ek hai, sab se azeem, rehman aur raheem. Allah ka koi shareek nahi aur na hi kisi ka baap ya bete ka rishta.'
            eng = 'Allah is One, powerful, merciful, and has no partner. Allah has no father, son, or relationship like humans.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'islam ka matlab' in low or 'what does islam mean' in low:
            urdu = 'Islam ka matlab salamti, amn aur Allah ke hukm mein islami zindagi basarna. Islam matlab hai Allah se rishta connect karna aur Quran ke mutabiq zindagi jeena.'
            eng = 'Islam means peace, submission, and living according to Allah guidance. Islam means connecting with Allah and living by the Quran teachings.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'hamare nabi' in low or 'our prophet' in low or 'prophet' in low or 'nabi' in low or 'hazrat muhammad' in low or 'muhammad' in low:
            urdu = 'Hamare Nabi ka naam Muhammad (SAW) hai. Woh 571 AD mein Makkah mein paida hue aur akhir zamane ke paigambar thay. Unka message simple tha: Allah ek hai aur us ki ibadat karo. Nabi (SAW) kabhi jhooth nahi bolte the aur unhe "Al-Ameen" (amaanatdar) kaha jaata tha. Un ke akhlaq sab se behtar the aur unhe follow karna har Muslim ke liye zaroori hai.'
            eng = 'Our Prophet is Muhammad (SAW). He was born in Makkah in 571 AD and was the last messenger. His message was simple: Allah is One and worship Him alone. The Prophet never lied and was called "Al-Ameen" (trustworthy). His character was the best and following him is essential for all Muslims.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'namaz' in low or 'pray' in low or 'salat' in low:
            urdu = 'Namaz Islam ka bunyadi farz hai jo paanch martaba din mein ada hoti hai. Namaz se insan ko Allah se joड़ata hai aur roohani taskeen deta hai. Fajr, Zuhr, Asr, Maghrib aur Isha - yeh paanch namaz hain. Namaz mein ruku, sajda aur duas hoti hain jo dil ko pak karte hain.'
            eng = 'Salah/Prayer is the basic duty in Islam performed five times daily. Prayer connects a person with Allah and brings spiritual peace. The five prayers are Fajr, Zuhr, Asr, Maghrib and Isha. Prayer involves bowing, prostration and supplications that purify the heart.'
            return self.format_response(urdu, eng, 'long', None, lang_roman)
        if 'roza' in low or 'fast' in low or 'saum' in low:
            urdu = 'Roza Ramadan mein rakha jata hai aur sehri se iftaar tak khaana aur pani se paraz rakshat hoti hai. Roza se insaan mein sabr, taqwa aur gareebon ke liye hamdardi paida hoti hai. Roza sirf khana peena nahi, balke dil ko bhi bhulai karne ki koshish hai.'
            eng = 'Fasting is observed in Ramadan from dawn to sunset without food or water. Fasting teaches patience, fear of Allah and empathy for the needy. Fasting is not just about abstaining from food but also purifying the heart.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'quran' in low:
            urdu = 'Quran Allah ka kalam hai jo 23 saalo mein nazil hua. Quran mein 114 Surahs aur 6236 Ayatein hain. Quran padhna, samajhna aur amal karna har Muslim ke liye zaroori hai. Quran se hum seekhte hain ke acha kaise ziyya jaye aur Allah se kaise dua ki jaye.'
            eng = 'The Quran is the word of Allah revealed over 23 years. It contains 114 Chapters and 6236 Verses. Reading, understanding and following the Quran is essential for Muslims. From the Quran we learn how to live well and pray to Allah.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'hadith' in low:
            urdu = 'Hadith Rasool (SAW) ke alfaaz aur aamal hain jo Quran ke baad ilm ka sab se ahem cheez hain. Hadith se seekhte hain ke namaz kaise ade karni chahiye, zindagi kaise jeena chahiye. Bukhari, Muslim, Tirmidhi - yeh mashhoor Hadith ki kitaabein hain.'
            eng = 'Hadith are the sayings and actions of the Prophet (SAW) and are the most important source of knowledge after the Quran. From Hadith we learn how to pray and live properly. Bukhari, Muslim, Tirmidhi are famous Hadith collections.'
            return self.format_response(urdu, eng, 'short', 'hadith', lang_roman)
        if 'seerat' in low or 'life of prophet' in low or 'biography' in low:
            urdu = 'Seerat-un-Nabi (SAW) humare liye zindagi ka sab se achha namoona hai. Nabi (SAW) ke zindagi mein sabr, honesty, aur adal dikhai deta hai. Nabi (SAW) ne apne dushmanon ko bhi paar kiya aur uthayya. Aaj ke zamane mein Nabi (SAW) ki seerat se seekhte hain ke character kaise build karte hain.'
            eng = 'The biography of the Prophet (SAW) is the best example for life. In the Prophet life we see patience, honesty and justice. The Prophet even forgave his enemies. In modern times the Prophet biography teaches us character building.'
            return self.format_response(urdu, eng, 'long', None, lang_roman)
        if 'haqooq' in low or 'rights' in low:
            urdu = 'Haqooq-ul-Ibad islami haqooq hain jo loggon ke muttaliq hain. Walidain ke haqooq, pados ke haqooq, gareebon ke haqooq, sirf Haqooq-ul-Ibad mein shamil hain. Islam kehta hai ke sabse pehle Allah ka haq, phir logon ka haq.'
            eng = 'Haqooq-ul-Ibad are Islamic rights related to people. Rights of parents, neighbors, the poor are all part of Haqooq-ul-Ibad. Islam teaches that first comes Allah right, then peoples rights.'
            return self.format_response(urdu, eng, 'long', None, lang_roman)
        if 'teacher' in low and 'rights' in low:
            urdu = 'Teacher ke haqooq Islam mein bohat ahem hain. Unhein adil tankhwah, izzat, safe environment aur training milni chahiye. Aaj Pakistan mein government teacher ko BPS ke mutabiq salary milti hai. Teacher profession mein imandari zaroori hai aur Quran mein likha hai ke talib-ilm ko ikhlaas se padhaana chahiye.'
            eng = 'Teacher rights are important in Islam. They should receive fair salary, respect, safe environment and training. In Pakistan government teachers are paid according to BPS scale. Teaching requires honesty and the Quran teaches to educate with sincerity.'
            return self.format_response(urdu, eng, 'long', None, lang_roman)
        if 'pakistan' in low and ('islamic system' in low or 'nizam' in low or 'nifaz' in low):
            urdu = 'Pakistan mein Islamic system naaiz karne ke liye: 1. TALEEM - Islamic education compulsory, Deen aur Dunya dono. 2. ADAALAT - Courts mein Quran o Sunnah ke mutabiq faisle. 3. ECONOMIC - Islamic banking, sood ka khatima, zakat system. 4. SAMAJI - Haqooq-ul-Ibad ka amal, ghurbat ka khatima. 5. SIYASAT - Shura consultation, imandaar leaders. Islami nizam tab kaami hota hai jab har aadmi sach bole aur Quran ke mutabiq amal kare.'
            eng = 'To establish Islamic system in Pakistan: 1. EDUCATION - Islamic education mandatory with religious and worldly knowledge. 2. JUDICIARY - Courts should decide based on Quran and Sunnah. 3. ECONOMY - Islamic banking, eliminate interest, proper zakat system. 4. SOCIAL - Practice Haqooq-ul-Ibad, end poverty. 5. POLITICS - Shura consultation, honest leaders. Islamic system works when every person speaks truth and acts according to Quran.'
            return self.format_response(urdu, eng, 'long', None, lang_roman)
        if 'sach' in low or 'honesty' in low or 'truth' in low or 'jhooth' in low:
            urdu = 'Sach bolna Islam mein bahut zaroori hai. Hazrat Muhammad (SAW) ne farmaya: "Sach bolo chahe kadwa lage." Agar hum sach bolein to logon ka bharosa milta hai. Jhooth bolne se ghar mein, school mein aur muashray mein begunahi phailti hai. Sach bolne se insaan ka naam nek hota hai.'
            eng = 'Telling the truth is very important in Islam. Prophet Muhammad (SAW) said: "Speak truth even if it is bitter." If we speak truth, people trust us. Lying spreads deception in family, school and society. Truth-telling builds good character.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        if 'arkan' in low or 'pillars' in low or ('islam ke' in low and ('amal' in low or 'farz' in low)):
            urdu = 'Islam ke 5 arkan hain: 1. KALIMA - La ilaha illallah, 2. NAMAZ - 5 baar din mein, 3. ROZA - Ramadan mein, 4. ZAKAT - gareebon ko maal, 5. HAJJ - Makkah jana. Yeh Islam ka bunyad hain. Jab hum yeh 5 arkan ada karte hain to hamari Islamiyat mukammal hoti hai.'
            eng = 'The 5 pillars of Islam are: 1. KALIMA - declaration of faith, 2. PRAYER - 5 times daily, 3. FASTING - in Ramadan, 4. ZAKAT - charity to the poor, 5. HAJJ - pilgrimage to Makkah. These are the foundation of Islam. When we fulfill these five pillars, our faith becomes complete.'
            return self.format_response(urdu, eng, 'long', None, lang_roman)
        if 'amanat' in low or 'amaanatdar' in low or 'trust' in low:
            urdu = 'Amanat ka matlab hai kisi ki cheez ki mehnat aur zimmedari se hifazat karna. Hazrat Muhammad (SAW) ko "Al-Ameen" (amaanatdar) kaha jaata tha. Amanat se insaan ka naam nek hota hai aur log us par bharosa karte hain. School mein examination mein amanat se answer karna, bachchon ke saath imandaari se pesh aana - yeh amanat hai. Amanatdar log ki taqdeer chamkti hai.'
            eng = 'Trust/Amanat means protecting something with care and responsibility. Prophet Muhammad (SAW) was called "Al-Ameen" (trustworthy). Keeping trust builds good character and people rely on you. In exams, answering honestly, being truthful with children - this is trust. Trustworthy people are successful.'
            return self.format_response(urdu, eng, 'long', None, lang_roman)
        if 'sahaba' in low or 'companions' in low or ('abu bakr' in low or 'umar' in low or 'usman' in low or 'ali' in low):
            urdu = 'Sahaba-e-Kiram Hazrat Muhammad (SAW) ke saath the. Unhe "Ashara-e-Mubashara" kehte hain (10 naik saathi jo Jannat ka akhbar diye gaye). Abu Bakr siddiq, Umar, Usman, Ali - yeh Khulafa-e-Rashideen hain. Sahaba ne Islam ki tadween ki aur Quran ko mehfuz rakha. Sahaba ki zimmedari bohat adhik thi aur unhon ne bravery se Islam phailaya.'
            eng = 'Sahaba (companions) were with Prophet Muhammad (SAW). There were 10 special companions given glad tidings of paradise. Abu Bakr Siddiq, Umar, Usman, Ali were the Rightly Guided Caliphs. Sahaba preserved Islam and the Quran. Companions had great responsibility and spread Islam with bravery.'
            return self.format_response(urdu, eng, 'long', None, lang_roman)
        if 'zakat' in low or 'zakah' in low:
            urdu = 'Zakat Islam ke paanch farz mein se ek hai. Zakat ka matlab hai ke har Muslim apne mal ka ek hissa gareebon ko de. Zakat se muashray mein aman aur barabari ati hai. Zakat mein khud mazloom logon ki madad hoti hai. Jab hum Zakat dete hain to Allah hamari doosri sadaqaat mein barkat deta hai aur hamara maal ziada hota hai.'
            eng = 'Zakat is one of the five pillars of Islam. Zakat means every Muslim gives a portion of wealth to the poor. Zakat brings peace and equality in society. Through Zakat we help the needy. When we give Zakat, Allah blesses our remaining wealth.'
            return self.format_response(urdu, eng, 'long', None, lang_roman)
        if 'hajj' in low or 'pilgrimage' in low:
            urdu = 'Hajj Islam ka paanchwaan farz hai jo Makkah mein kiya jata hai. Hajj mein log Kaaba ko tawaf karte hain, safaa marwa ke daudte hain, aur Arafat mein khade ho kar dua karte hain. Hajj se Muslim bhai-bhaichara ka tashaor milta hai. Hajj Muslim ke liye ek ahem ibadat hai jo 2 se 3 hafton tak hoti hai.'
            eng = 'Hajj is the fifth pillar of Islam performed in Makkah. In Hajj, people circumambulate the Kaaba, run between Safaa and Marwa, and pray at Arafat. Hajj creates a sense of brotherhood among Muslims. Hajj is an important worship for Muslims lasting 2-3 weeks.'
            return self.format_response(urdu, eng, 'long', None, lang_roman)
        if 'kalima' in low or 'shahada' in low:
            urdu = 'Kalima Shahada (Kalima Tayyaba) Islam ka bunyad hai. Kalima hai: "La ilaha illallah Muhammadur Rasoolullah" - iska matlab "Allah ke siwa koi khuda nahi, Muhammad Allah ke paigambar hain." Yeh 7 alfaaz mein likha hai. Kalima se insaan Muslim ban jata hai. Muslim ke zindagi mein Kalima sabse mahatvpurn ہے.'
            eng = 'Kalima (testimony of faith) is the foundation of Islam. Kalima is: "There is no god but Allah, Muhammad is the messenger of Allah." This is written in 7 words. By reciting Kalima, one becomes Muslim. Kalima is the most important part of Islamic life.'
            return self.format_response(urdu, eng, 'short', None, lang_roman)
        return None

    def answer_question(self, text: str, class_level, lang_roman: bool):
        command = self.detect_command(text)
        low = text.lower()

        if command == 'father_job':
            return self.father_job_response(lang_roman)

        father_related = ['father', 'abb', 'salary', 'income', 'kamai', 'teaching', 'teacher', 'bps-17', 'bps 17', 'amanah', 'honesty', 'zimmedari', 'duties']
        if command is None and 'father' in low and any(word in low for word in father_related):
            return self.father_job_response(lang_roman)

        # ── PRIMARY: Search the 400-question bank ─────────────────────────────
        bank_match = self.search_question_bank(text, class_level)
        if bank_match:
            q_text = bank_match['q']
            a_text = bank_match['a']
            class_label = bank_match['classGroup']
            prefix = f"**Class {class_label} — Islamiyat Question Bank**\n\n"
            suffix = ""
            if command == 'real_life':
                suffix = "\n\n**Real Life:** Aaj ke Pakistan mein is sabaq ko apni zindagi mein apply karo."
            elif command == 'hadith':
                suffix = "\n\n**Hadith:** 'Inna Allah la yuhib kull mukhtal fakhur.'"
            elif command == 'long':
                prefix = f"**Detailed Answer — Class {class_label}**\n\n"
            return f"{prefix}**Q: {q_text}**\n\n**A:** {a_text}{suffix}"

        # ── SECONDARY: Specific topic answers ─────────────────────────────────
        specific = self.specific_topic_answer(text, class_level, lang_roman)
        if specific:
            return specific

        if 'daily ayat' in low:
            return self.handle_daily_ayat(lang_roman)

        if command == 'ayat' and 'daily ayat' not in low:
            base = self.base_topic_answer(text, class_level, lang_roman)
            if base:
                return f"{base}\n\nQuran Reference: 'Innama al-a'malu bin-niyat.'"

        base = self.base_topic_answer(text, class_level, lang_roman)
        if base:
            if command == 'real_life':
                return f"{base}\n\nReal Life Example: Aaj ke zamane mein yeh amal is tarah se kiya jata hai."
            if command == 'hadith':
                return f"{base}\n\nHadith: 'Amanah sab se pehle.'"
            if command == 'long':
                return f"**Detailed Answer:**\n{base}\n\nYeh jawab Class {class_level or '1-12'} ke Islamiyat syllabus ke mutabiq hai."
            return base

        # ── FALLBACK ───────────────────────────────────────────────────────────
        urdu = 'Islamiyat ke is sawal ka specific answer mujhe database mein nahi mila. Kya aap dusra sawal kar sakte ho? Main Class 1 se 12 tak ke tamam Islamiyat sawalon ka jawab de sakta hoon.'
        eng = 'I could not find a specific answer to this Islamiyat question in my database. Can you ask another question? I can answer all Islamiyat questions for Class 1 to 12.'
        return self.format_response(urdu, eng, command or 'short', command, lang_roman)


responder = LocalResponder()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/questions')
def questions_page():
    return render_template('questions.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({"response": "Please enter a message."})

    # Enforce Islamiyat-only policy for safety
    low = user_message.lower()
    non_islamic_keywords = ['photosynthesis', 'math', 'physics', 'chemistry', 'biology']
    if any(k in low for k in non_islamic_keywords) and 'islamiyat' not in low:
        return jsonify({"response": "Maaf kijiye — yeh assistant sirf Islamiyat ke sawalat ka jawab deta hai."})

    lang_roman = responder.detect_roman_urdu(user_message)
    class_level = responder.parse_class(user_message)

    # Handle Daily Ayat
    if 'daily ayat' in low or 'ayat' in low:
        return jsonify({"response": responder.handle_daily_ayat(lang_roman)})

    # MCQs
    if 'mcq' in low or 'mcqs' in low:
        topic = 'Islamiyat'
        return jsonify({"response": responder.generate_mcqs(topic, class_level, lang_roman)})

    # Quiz
    if 'quiz' in low:
        topic = 'Islamiyat'
        return jsonify({"response": responder.generate_quiz(topic, class_level, lang_roman)})

    # Lesson Plan
    if 'lesson plan' in low or 'lesson' in low:
        topic = 'Islamiyat'
        return jsonify({"response": responder.generate_lesson_plan(topic, class_level, lang_roman)})

    # Default: answer question locally
    answer = responder.answer_question(user_message, class_level, lang_roman)
    return jsonify({"response": answer})



@app.route('/api/questions')
def api_questions():
    class_filter = request.args.get('class', 'all')
    search_q     = request.args.get('q', '').strip().lower()
    filtered = QUESTION_BANK
    if class_filter != 'all':
        filtered = [x for x in filtered if x['classGroup'] == class_filter]
    if search_q:
        filtered = [x for x in filtered
                    if search_q in x['q'].lower() or search_q in x['a'].lower()]
    return jsonify({'questions': filtered, 'total': len(filtered)})

@app.route('/api/questions/groups')
def api_question_groups():
    return jsonify({'groups': CLASS_GROUPS})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=5000)
