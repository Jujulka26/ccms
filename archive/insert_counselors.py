import sys
import os
import mysql.connector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend", "app"))
from db import add_counselor


def get_connection():
    return mysql.connector.connect(host="localhost", user="root", password="", database="ccms_db")


def clear_counselors():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("DELETE FROM tbl_counselor_profile")
        cursor.execute("DELETE FROM tbl_counselor")
        cursor.execute("ALTER TABLE tbl_counselor AUTO_INCREMENT = 1")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        print("Cleared all existing counselors.")
    finally:
        cursor.close()
        conn.close()


# Modalities: Cognitive | Behavioral | Humanistic | Psychodynamic (up to 2, comma-separated)
# ~60% single, ~40% dual — mirrors ML training data distribution

counselors = [
    # ── Anxiety specialists ───────────────────────────────────────────────────
    {
        "name": "Mei Ling Tan",
        "age": 34,
        "gender": "Female",
        "ethnicity": "Chinese",
        "specialization": "Anxiety",
        "counselor_language": "Mandarin, English",
        "counselor_modality": "Cognitive, Behavioral",   # dual — CBT maps here
        "experience_years": 10,
        "about_me": "I specialise in anxiety management and help clients build practical coping skills through structured, evidence-based techniques that address both thought patterns and daily behaviour.",
        "expertise_tags": "Anxiety, Panic Attacks, Work Stress, Cognitive, Behavioral",
        "helpful_thought_1": "I feel overwhelmed and don't know where to start.",
        "helpful_thought_2": "I want to feel more in control of my thoughts.",
        "modality_desc": "Using both Cognitive and Behavioral techniques, we identify unhelpful thought patterns and pair them with behaviour-change exercises — creating lasting shifts in how you feel and act.",
        "image": "Mei Ling Tan.png",
    },
    {
        "name": "Siti Rahimah",
        "age": 45,
        "gender": "Female",
        "ethnicity": "Malay",
        "specialization": "Anxiety",
        "counselor_language": "Malay, English",
        "counselor_modality": "Cognitive",               # single — REBT is Cognitive
        "experience_years": 18,
        "about_me": "As a senior counsellor I help clients challenge irrational beliefs that fuel anxiety, replacing them with balanced, realistic thinking for a more grounded daily life.",
        "expertise_tags": "Anxiety, Social Anxiety, Perfectionism, Cognitive, Core Beliefs",
        "helpful_thought_1": "I always worry about what others think of me.",
        "helpful_thought_2": "I put too much pressure on myself to be perfect.",
        "modality_desc": "Cognitive therapy helps us identify the specific beliefs driving your distress and actively challenge them — leading to lasting changes in how you feel and respond.",
        "image": "Siti Rahimah.png",
    },
    {
        "name": "Julian Fox",
        "age": 29,
        "gender": "Male",
        "ethnicity": "Other",
        "specialization": "Anxiety",
        "counselor_language": "English",
        "counselor_modality": "Humanistic",              # single
        "experience_years": 5,
        "about_me": "I provide a deeply empathetic, non-directive environment for those battling social and general anxiety — allowing you to find your own voice at your own pace.",
        "expertise_tags": "Anxiety, Social Phobia, Humanistic, Empathetic Listening, Self-Acceptance",
        "helpful_thought_1": "I'm always worried I'm doing something wrong.",
        "helpful_thought_2": "I just need someone who won't push me.",
        "modality_desc": "Humanistic counselling offers a completely safe, zero-pressure space. You lead the sessions — I listen, reflect, and support without any agenda.",
        "image": "Julian Fox.png",
    },
    {
        "name": "Farhana binti Yusof",
        "age": 30,
        "gender": "Female",
        "ethnicity": "Malay",
        "specialization": "Anxiety",
        "counselor_language": "Malay, English",
        "counselor_modality": "Behavioral",              # single — mindfulness-based = Behavioral
        "experience_years": 6,
        "about_me": "I work with young professionals heavily burdened by anxiety, using behavioural and grounding techniques to anchor overactive, racing minds into the present.",
        "expertise_tags": "Anxiety, Generalized Anxiety, Millennials, Behavioral, Grounding",
        "helpful_thought_1": "I am procrastinating so much because of my anxiety.",
        "helpful_thought_2": "My brain won't shut off at night.",
        "modality_desc": "Behavioral therapy uses breath, grounding, and exposure techniques to anchor you in the present moment — gradually reducing the hold anxiety has over daily life.",
        "image": "Farhana binti Yusof.png",
    },

    # ── Depression specialists ─────────────────────────────────────────────────
    {
        "name": "Ariff Bin Hassan",
        "age": 41,
        "gender": "Male",
        "ethnicity": "Malay",
        "specialization": "Depression",
        "counselor_language": "Malay, English",
        "counselor_modality": "Humanistic",              # single
        "experience_years": 14,
        "about_me": "I create a warm, non-judgmental space where clients feel truly heard as they work through depression, low mood, and loss of self-worth.",
        "expertise_tags": "Depression, Self-esteem, Grief, Loss, Life Transitions, Humanistic",
        "helpful_thought_1": "I feel like nothing will ever get better.",
        "helpful_thought_2": "I don't feel understood by the people around me.",
        "modality_desc": "In our sessions we focus on understanding your feelings without judgement — you set the pace and the direction, always.",
        "image": "Ariff Bin Hassan.png",
    },
    {
        "name": "Kevin Raj",
        "age": 32,
        "gender": "Male",
        "ethnicity": "Indian",
        "specialization": "Depression",
        "counselor_language": "Tamil, English",
        "counselor_modality": "Behavioral",              # single
        "experience_years": 6,
        "about_me": "I use behavioural activation and compassion-focused techniques to help clients with depression reconnect with meaningful activities and rebuild day-to-day motivation.",
        "expertise_tags": "Depression, Behavioral Activation, Self-compassion, Young Adults, Motivation",
        "helpful_thought_1": "I have no motivation to do anything anymore.",
        "helpful_thought_2": "I feel empty even when things seem fine on the outside.",
        "modality_desc": "Behavioral therapy breaks the cycle of withdrawal — we plan small, meaningful activities to rebuild your energy and reconnect you with what matters.",
        "image": "Kevin Raj.png",
    },
    {
        "name": "Sarah Chen",
        "age": 28,
        "gender": "Female",
        "ethnicity": "Chinese",
        "specialization": "Depression",
        "counselor_language": "Mandarin, English",
        "counselor_modality": "Cognitive",               # single
        "experience_years": 4,
        "about_me": "I work with young adults and university students facing depression, using cognitive strategies and behavioural activation to rebuild lost motivation and a clearer sense of self.",
        "expertise_tags": "Depression, Quarter-Life Crisis, Youth, Cognitive, Goal Setting",
        "helpful_thought_1": "I feel lost and disconnected from my peers.",
        "helpful_thought_2": "Every small task feels like climbing a mountain.",
        "modality_desc": "Cognitive therapy focuses on identifying the thought traps keeping you stuck in low mood — then building a step-by-step plan to act from intention rather than emotion.",
        "image": "Sarah Chen.png",
    },
    {
        "name": "Kavitha Menon",
        "age": 42,
        "gender": "Female",
        "ethnicity": "Indian",
        "specialization": "Depression",
        "counselor_language": "English, Tamil",
        "counselor_modality": "Cognitive, Psychodynamic",  # dual
        "experience_years": 14,
        "about_me": "I help clients challenge the deep-seated negative core beliefs that drive depression, blending cognitive restructuring with exploration of past experiences that shaped those beliefs.",
        "expertise_tags": "Depression, Postpartum Depression, Cognitive, Psychodynamic, Core Beliefs",
        "helpful_thought_1": "I feel like a burden to my family.",
        "helpful_thought_2": "No matter what I achieve, it never feels like enough.",
        "modality_desc": "Combining Cognitive and Psychodynamic approaches, we identify the beliefs keeping you stuck and trace where they came from — so we can address both the thought and its root.",
        "image": "Kavitha Menon.png",
    },
    {
        "name": "Marcus Thompson",
        "age": 36,
        "gender": "Male",
        "ethnicity": "Other",
        "specialization": "Depression",
        "counselor_language": "English",
        "counselor_modality": "Behavioral",              # single
        "experience_years": 9,
        "about_me": "An Australian expat focusing on treating depression through somatic and behavioural lenses, bringing gentle awareness back to the body and the present moment.",
        "expertise_tags": "Depression, Emotional Numbness, Behavioral, Somatic Awareness, Body-Mind",
        "helpful_thought_1": "Nothing gives me joy anymore.",
        "helpful_thought_2": "I just feel hollow inside most days.",
        "modality_desc": "Behavioral therapy with a somatic focus helps us observe depressive patterns through both the mind and body — gently reactivating connection to the present.",
        "image": "Marcus Thompson.png",
    },
    {
        "name": "Claire Dupont",
        "age": 40,
        "gender": "Female",
        "ethnicity": "Other",
        "specialization": "Depression",
        "counselor_language": "English",
        "counselor_modality": "Humanistic, Psychodynamic",  # dual
        "experience_years": 11,
        "about_me": "My approach to depression is fully client-led — I provide a warm, accepting space to explore feelings and understand how early experiences quietly shape the present.",
        "expertise_tags": "Depression, Existential Crisis, Humanistic, Psychodynamic, Meaning-Making",
        "helpful_thought_1": "I don't feel seen by anyone in my daily life.",
        "helpful_thought_2": "I am struggling to find meaning in my life lately.",
        "modality_desc": "Blending Humanistic warmth with Psychodynamic depth, we explore what you feel today and gently connect it to patterns formed over your lifetime — at your pace.",
        "image": "Claire Dupont.png",
    },

    # ── Stress specialists ────────────────────────────────────────────────────
    {
        "name": "Priya Nair",
        "age": 29,
        "gender": "Female",
        "ethnicity": "Indian",
        "specialization": "Stress",
        "counselor_language": "Tamil, English",
        "counselor_modality": "Behavioral",              # single
        "experience_years": 5,
        "about_me": "I guide clients in using behavioural and grounding techniques to manage everyday stress and build emotional resilience that holds up under pressure.",
        "expertise_tags": "Stress, Burnout, Behavioral, Grounding, Work-Life Balance",
        "helpful_thought_1": "I am constantly exhausted and can't switch off.",
        "helpful_thought_2": "I feel anxious all the time but I don't know why.",
        "modality_desc": "Behavioral sessions teach you to observe stress triggers without reacting automatically — small daily practices that create sustainable calm and resilience.",
        "image": "Priya Nair.png",
    },
    {
        "name": "Ahmad Fadzil",
        "age": 50,
        "gender": "Male",
        "ethnicity": "Malay",
        "specialization": "Stress",
        "counselor_language": "Malay, English",
        "counselor_modality": "Cognitive, Behavioral",   # dual
        "experience_years": 22,
        "about_me": "With over two decades of experience I help professionals and families manage chronic stress through structured techniques that address both thinking patterns and daily habits.",
        "expertise_tags": "Stress, Career Burnout, Family Issues, Cognitive, Behavioral, Coping Skills",
        "helpful_thought_1": "My work is taking over my life and I can't keep up.",
        "helpful_thought_2": "I feel responsible for everything and it's crushing me.",
        "modality_desc": "Cognitive and Behavioral work together here — we identify your biggest stressors, challenge the beliefs amplifying them, and build concrete daily habits to manage them.",
        "image": "Ahmad Fadzil.png",
    },
    {
        "name": "Dr. Sarah Jenkins",
        "age": 42,
        "gender": "Female",
        "ethnicity": "Other",
        "specialization": "Stress",
        "counselor_language": "English",
        "counselor_modality": "Cognitive",               # single
        "experience_years": 15,
        "about_me": "Originally from the UK, I help expats and locals navigate cross-cultural workplace burnout and life transitions by challenging the demanding self-expectations that drive chronic stress.",
        "expertise_tags": "Stress, Expat Adjustments, Career Burnout, Cognitive, Self-Acceptance",
        "helpful_thought_1": "I feel completely alienated in my current environment.",
        "helpful_thought_2": "I'm pushing myself to the breaking point for my career.",
        "modality_desc": "Cognitive therapy addresses the rigid demands we place on ourselves and our environment — learning to replace impossible standards with flexible, self-accepting alternatives.",
        "image": "Dr. Sarah Jenkins.png",
    },
    {
        "name": "Karthik Raj",
        "age": 45,
        "gender": "Male",
        "ethnicity": "Indian",
        "specialization": "Stress",
        "counselor_language": "Tamil, English, Malay",
        "counselor_modality": "Cognitive, Behavioral",   # dual
        "experience_years": 16,
        "about_me": "I use cognitive and behavioural techniques to combat severe executive stress, perfectionism, and anger issues driven by high-pressure workplace demands.",
        "expertise_tags": "Stress, Executive Burnout, Anger Management, Cognitive, Behavioral, Male Mental Health",
        "helpful_thought_1": "I snap at my family because I'm so stressed from work.",
        "helpful_thought_2": "Things HAVE to go my way or everything is a disaster.",
        "modality_desc": "Through Cognitive work we dismantle the absolute rules driving your stress, and through Behavioral practice we replace reactive patterns with deliberate, grounded responses.",
        "image": "Karthik Raj.png",
    },
    {
        "name": "Benny Ng",
        "age": 60,
        "gender": "Male",
        "ethnicity": "Chinese",
        "specialization": "Stress",
        "counselor_language": "Mandarin, English",
        "counselor_modality": "Humanistic, Psychodynamic",  # dual
        "experience_years": 30,
        "about_me": "As a veteran counsellor I specialise in complex life transitions, retirement stress, and midlife identity — offering deep, reflective support grounded in decades of experience.",
        "expertise_tags": "Stress, Retirement, Midlife Crisis, Humanistic, Psychodynamic, Life Meaning",
        "helpful_thought_1": "I don't know my purpose anymore after retiring.",
        "helpful_thought_2": "My life changes are happening too fast to process.",
        "modality_desc": "Combining Humanistic presence with Psychodynamic reflection, we explore the meaning behind your stress and trace the deeper patterns shaping how you respond to change.",
        "image": "Benny Ng.png",
    },

    # ── Trauma specialists ────────────────────────────────────────────────────
    {
        "name": "David Lim",
        "age": 38,
        "gender": "Male",
        "ethnicity": "Chinese",
        "specialization": "Trauma",
        "counselor_language": "Mandarin, English",
        "counselor_modality": "Cognitive, Behavioral",   # dual
        "experience_years": 12,
        "about_me": "I have extensive experience working with trauma survivors, helping clients safely process difficult memories and rebuild a sense of safety through structured, evidence-based work.",
        "expertise_tags": "Trauma, PTSD, Abuse, Resilience, Cognitive, Behavioral",
        "helpful_thought_1": "I keep reliving something that happened to me.",
        "helpful_thought_2": "I don't feel safe opening up to people.",
        "modality_desc": "Cognitive and Behavioral approaches for trauma work together — revisiting difficult experiences in a carefully structured way while building safety behaviours and grounding skills.",
        "image": "David Lim.png",
    },
    {
        "name": "Jamie Wong",
        "age": 27,
        "gender": "Female",
        "ethnicity": "Chinese",
        "specialization": "Trauma",
        "counselor_language": "Mandarin, English",
        "counselor_modality": "Humanistic",              # single
        "experience_years": 3,
        "about_me": "I offer a gentle, person-centred approach for those healing from trauma — entirely at your pace, in a space built on safety, warmth, and no judgement.",
        "expertise_tags": "Trauma, Childhood Issues, Identity, Humanistic, Safe Space, Self-Discovery",
        "helpful_thought_1": "I carry a lot from my past that I've never talked about.",
        "helpful_thought_2": "I just want someone to listen without judging me.",
        "modality_desc": "Humanistic counselling is led entirely by you — I am here to understand, reflect, and hold space as you explore your experiences without any pressure or agenda.",
        "image": "Jamie Wong.png",
    },
    {
        "name": "Dr. Hannah Schmidt",
        "age": 55,
        "gender": "Female",
        "ethnicity": "Other",
        "specialization": "Trauma",
        "counselor_language": "English",
        "counselor_modality": "Cognitive, Behavioral",   # dual
        "experience_years": 25,
        "about_me": "With decades of clinical experience across Europe and Asia, I provide structured cognitive and behavioural interventions to safely process deep-rooted traumatic experiences.",
        "expertise_tags": "Trauma, PTSD, Complex Trauma, Cognitive, Behavioral, Structured Therapy",
        "helpful_thought_1": "I can't escape the bad memories. They control my life.",
        "helpful_thought_2": "I isolate myself so I don't feel vulnerable.",
        "modality_desc": "Cognitive and Behavioral therapy for trauma systematically addresses avoidance patterns and helps reprocess fearful memories within a structured, safe, and boundaried environment.",
        "image": "Dr. Hannah Schmidt.png",
    },
    {
        "name": "Nur Atiqah",
        "age": 31,
        "gender": "Female",
        "ethnicity": "Malay",
        "specialization": "Trauma",
        "counselor_language": "Malay, English",
        "counselor_modality": "Behavioral",              # single
        "experience_years": 7,
        "about_me": "I integrate trauma-informed behavioural approaches to help clients gently reconnect with their bodies after traumatic events, without feeling overwhelmed or unsafe.",
        "expertise_tags": "Trauma, Somatic Healing, Behavioral, Emotional Regulation, Body-Awareness",
        "helpful_thought_1": "I want to be able to relax without feeling panicked.",
        "helpful_thought_2": "I feel detached from myself and my emotions.",
        "modality_desc": "Behavioral therapy with a trauma-sensitive lens focuses on gentle, safe body-awareness and grounding exercises — always working within your window of tolerance.",
        "image": "Nur Atiqah.png",
    },
    {
        "name": "Arun Prakash",
        "age": 33,
        "gender": "Male",
        "ethnicity": "Indian",
        "specialization": "Trauma",
        "counselor_language": "Tamil, English",
        "counselor_modality": "Humanistic, Psychodynamic",  # dual
        "experience_years": 7,
        "about_me": "I practice deeply affirming person-centred therapy for men recovering from silent trauma, blending present-focused warmth with careful exploration of how the past shapes today.",
        "expertise_tags": "Trauma, Men's Mental Health, Stigma, Humanistic, Psychodynamic, Healing",
        "helpful_thought_1": "I feel weak asking for help about this trauma.",
        "helpful_thought_2": "I've held onto this secret for far too long.",
        "modality_desc": "Humanistic warmth meets Psychodynamic depth — your safety and autonomy come first, and together we gently explore how past experiences have shaped your present self.",
        "image": "Arun Prakash.png",
    },
]


if __name__ == "__main__":
    clear_counselors()
    inserted = 0
    for c in counselors:
        try:
            add_counselor(
                name=c["name"],
                age=c["age"],
                gender=c["gender"],
                ethnicity=c["ethnicity"],
                specialization=c["specialization"],
                counselor_language=c["counselor_language"],
                counselor_modality=c["counselor_modality"],
                experience_years=c["experience_years"],
                about_me=c["about_me"],
                expertise_tags=c["expertise_tags"],
                helpful_thought_1=c["helpful_thought_1"],
                helpful_thought_2=c["helpful_thought_2"],
                modality_desc=c["modality_desc"],
                image=c["image"],
            )
            print(f"  Inserted: {c['name']} [{c['counselor_modality']}]")
            inserted += 1
        except Exception as e:
            print(f"  ERROR {c['name']}: {e}")

    print(f"\nDone — {inserted}/{len(counselors)} counselors inserted.")
