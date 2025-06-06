import streamlit as st

st.set_page_config(
    page_title="Sovereignty Philosophy",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS for philosophy styling
st.markdown("""
<style>
    .philosophy-hero {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        color: #f5f5f5;
        padding: 3rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin: 2rem 0;
        border: 2px solid #444;
    }
    
    .philosophy-essay {
        background: rgba(255, 255, 255, 0.02);
        border-left: 4px solid #ffcc00;
        padding: 2rem;
        margin: 2rem 0;
        border-radius: 0 12px 12px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .sovereignty-principle {
        background: linear-gradient(135deg, rgba(255, 204, 0, 0.1), rgba(255, 204, 0, 0.05));
        border: 1px solid rgba(255, 204, 0, 0.3);
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
    }
    
    .manifesto-section {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: #f1f5f9;
        padding: 2.5rem;
        border-radius: 16px;
        margin: 2rem 0;
        border: 2px solid #64748b;
    }
    
    .philosophy-quote {
        font-size: 1.4em;
        font-style: italic;
        color: #ffcc00;
        text-align: center;
        margin: 2rem 0;
        padding: 1rem;
        border-top: 2px solid #444;
        border-bottom: 2px solid #444;
    }
    
    .principle-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="philosophy-hero">
    <h1>🛡️ The Sovereignty Philosophy</h1>
    <h3>Reclaim Health, Freedom, and Future Wealth</h3>
    <p style="font-size: 1.2em; margin-top: 1.5rem; color: #ccc;">
        "We were never meant to be this sick, this tired, or this dependent."
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Introduction
st.markdown("## 🎯 What is Sovereignty?")

st.markdown("""
**Sovereignty** is not political independence or geographic isolation. It's **personal autonomy** built through 
daily discipline across the domains that matter most: your body, your mind, your resources, and your future.

In a world designed to erode your agency—through processed foods, financial complexity, and engineered dependency—the 
sovereignty path is a return to fundamentals. It's the recognition that **your daily choices compound into your life circumstances.**

Every home-cooked meal, every workout, every dollar saved, every moment of stillness is a vote. A vote for vitality. 
A vote for resilience. A vote for freedom. **And we believe votes should count.**
""")

# Core Philosophy Essays
st.markdown("---")
st.markdown("## 📜 The Three Pillars of Sovereignty")

# Essay 1: Body as Private Property
st.markdown("### 🏛️ What If Your Body Is Your Last Piece of Private Property?")

st.markdown("""
In an era where nearly every inch of life is monetized, tracked, and controlled, sovereignty begins where ownership 
is still absolute: **the body**. If your body is the final territory untouched by corporations, governments, 
and algorithms, then the way you care for it becomes a radical act of defiance.

We are surrounded by systems designed to erode physical autonomy. Ultra-processed foods, designed for addiction. 
Sedentary lifestyles engineered by convenience. Healthcare systems that react to disease rather than cultivate health. 
A population easily distracted and chronically ill is easier to pacify.

But what if your body was sacred ground? Not in a religious sense, but as **the last asset no one can repossess** 
— unless you hand it over. Every decision to eat clean food, to move with intention, to sleep deeply, becomes an act of preservation. 
Every push-up, every home-cooked meal, every skipped commercial for a walk outside is a refusal to let someone else write your fate.

**To reclaim the body is to reclaim the future. It's the only foundation strong enough to build true sovereignty upon. 
Because without health, what good is freedom?**
""")

# Essay 2: Internal Exit
st.markdown("### 🧭 The Exit is Not External — It's Internal")

st.markdown("""
Many seek the exit: from the system, the noise, the chaos. They dream of unplugging, of escaping into some purer life. 
But most fail to realize that **the first walls they must tear down are not out there — they are within.**

The world programmed you to believe you are powerless, to trade comfort for control, to seek validation over truth. 
These beliefs are not yours; they were planted. You inherited fears and habits from generations past, from media, 
from school, from broken systems pretending to offer solutions.

You cannot buy your way out. You cannot flee to the woods with a broken compass. First, you must **reboot your 
internal OS**. You must decide what is real, what is enough, what is yours to carry. True sovereignty begins when 
you define your own metrics for success, your own rituals for strength, your own rhythm of life.

**The sovereign path doesn't lead away from society; it leads inward, to a fortified core. From that place, you are unshakable.**
""")

# Essay 3: Outlasting Collapse
st.markdown("### ⚡ You Can't Outrun the Collapse, But You Can Outlast It")

st.markdown("""
We are living through an unraveling. Trust in institutions is crumbling. The financial system runs on fumes. 
Health, both physical and mental, is in freefall. Some look away. Some panic. **The sovereign prepares.**

You cannot stop what is coming, nor predict its exact timing. But you can fortify your body, sharpen your mind, 
and align your daily choices with resilience. Eat meals that make you stronger. Save money in forms that can't be 
printed into dust. Train your body to lift, run, and endure. Teach your children how to grow food and question narratives.

Sovereignty isn't about retreating into fear. It's about **building a life that still functions — even flourishes — 
when the old world stutters**. It's about growing real wealth: health, time, skill, community, truth. 
These are not volatile. They are antifragile.

**You won't outpace the collapse. But you can stand when others fall. You can shine when others panic. 
You can endure. That's what makes you dangerous. That's what makes you free.**
""")

st.markdown("---")

# Core Sovereignty Principles
st.markdown("## ⚖️ The Eight Core Principles")

principles = [
    {
        "title": "🏗️ Daily Discipline Compounds",
        "description": "Personal sovereignty is built through daily discipline across multiple domains. Small, consistent actions compound into unshakeable autonomy over time."
    },
    {
        "title": "🔗 Health = Wealth = Freedom",
        "description": "These domains are interconnected—weakness in one erodes the others. True wealth includes your body, mind, time, and skills."
    },
    {
        "title": "🕐 Low Time Preference Thinking",
        "description": "Sacrifice immediate pleasure for long-term sovereignty. Your future self will thank you for the discipline you practice today."
    },
    {
        "title": "💪 Anti-Fragile Systems",
        "description": "Build systems that get stronger under stress, not just resilient. Embrace challenges as opportunities to grow."
    },
    {
        "title": "🎯 Skin in the Game", 
        "description": "Align your incentives with your values—put your own resources at risk. Talk is cheap; action reveals truth."
    },
    {
        "title": "🧹 Via Negativa Wisdom",
        "description": "Often what you don't do matters more than what you do. Eliminate the harmful before adding the beneficial."
    },
    {
        "title": "🧠 First Principles Reasoning",
        "description": "Think from first principles, not conventional wisdom or social proof. Question everything, especially what 'everyone knows.'"
    },
    {
        "title": "🛡️ Internal Systems Over External Circumstances",
        "description": "Build yourself into someone who can't be controlled. Your body, mind, and resources are your last pieces of private property."
    }
]

st.markdown('<div class="principle-grid">', unsafe_allow_html=True)
for principle in principles:
    st.markdown(f"""
    <div class="sovereignty-principle">
        <h4>{principle['title']}</h4>
        <p>{principle['description']}</p>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Expert Influences
st.markdown("## 🎓 Expert Foundations")

st.markdown("""
The Sovereignty Path integrates wisdom from leading experts across health, finance, and consciousness:
""")

experts_col1, experts_col2 = st.columns(2)

with experts_col1:
    st.markdown("""
    **🧠 Andrew Huberman**
    - Optimize circadian rhythms and metabolic health
    - Stress + recovery cycles build resilience
    - Dopamine management is sovereignty
    - Morning protocols set daily foundation
    
    **💪 Jeff Cavaliere (Athlean-X)**
    - Train like your life depends on it
    - Consistency beats intensity
    - Progressive overload across all domains
    - Recovery is earned through work
    """)

with experts_col2:
    st.markdown("""
    **🌱 Michael Pollan**
    - "Eat food, not too much, mostly plants"
    - Cook your own food—control your inputs
    - Real food connects you to the earth
    - Mindful eating is meditation in action
    
    **🏥 Mark Hyman (Food Fix)**
    - Food is medicine—every bite matters
    - Systemic health requires systemic thinking
    - Choose anti-inflammatory living
    - Regenerative practices heal both personal and planetary health
    """)

st.markdown("---")

# The Manifesto
st.markdown("---")
st.markdown("## 🛡️ The Sovereign Path Manifesto")

st.markdown("### 💛 Sovereignty is the new health plan.")

st.markdown("""
We believe that health is not just about calories, steps, or gym selfies — it is the **foundational layer of personal power.** 
A sovereign body leads to a sovereign mind. A sovereign mind makes sovereign choices. And those choices compound.

Every clean meal, every strength session, every moment of stillness — is a vote.
""")

# The three votes - using columns for better visual impact
vote_col1, vote_col2, vote_col3 = st.columns(3)
with vote_col1:
    st.markdown("### ⚡ A vote for **vitality**")
with vote_col2:
    st.markdown("### 🛡️ A vote for **resilience**")  
with vote_col3:
    st.markdown("### 🕊️ A vote for **freedom**")

st.markdown("""
That's why we built the **Sovereignty Score** — a daily, open-source tool to track the habits that actually matter. 
No fads. No complexity. Just the fundamentals, done with intention and repetition.

**If you're tired of waiting for someone else to fix your health, your finances, or your future — walk the path.**

No one's coming to save you. But you can. And you won't walk alone.
""")

# Philosophy Quote
st.markdown("""
<div class="philosophy-quote">
    "The sovereign path doesn't lead away from society; it leads inward, to a fortified core. 
    From that place, you are unshakable."
</div>
""", unsafe_allow_html=True)

# Call to Action
st.markdown("---")
st.markdown("## 🚀 Ready to Begin Your Sovereignty Journey?")

cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])

with cta_col2:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: rgba(255, 204, 0, 0.1); border: 2px solid rgba(255, 204, 0, 0.3); border-radius: 12px;">
        <h3 style="color: #ffcc00; margin-bottom: 1rem;">Start Tracking Your Sovereignty</h3>
        <p style="margin-bottom: 1.5rem;">Choose your path, track your progress, build your freedom.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🛡️ Begin Your Sovereignty Path", type="primary", use_container_width=True):
        st.switch_page("pages/5_Paths.py")

st.markdown("---")

# Footer
st.markdown("""
<div style="text-align: center; color: #888; margin-top: 3rem;">
    <p><em>"Every meal, every workout, every investment is a vote for your freedom."</em></p>
    <p>🛡️ Built for the sovereign. By the sovereign.</p>
</div>
""", unsafe_allow_html=True)