import streamlit as st

st.set_page_config(
    page_title="Sovereignty Paths",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS for paths styling
st.markdown("""
<style>
    .path-hero {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        color: #f5f5f5;
        padding: 2.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin: 2rem 0;
        border: 2px solid #444;
    }
    
    .path-card {
        background: rgba(255, 255, 255, 0.02);
        border: 2px solid rgba(255, 204, 0, 0.3);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        transition: transform 0.2s, border-color 0.2s;
    }
    
    .path-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 204, 0, 0.6);
        box-shadow: 0 8px 25px rgba(255, 204, 0, 0.1);
    }
    
    .path-philosophy {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
        border-left: 4px solid #8b5cf6;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 0 12px 12px 0;
        font-style: italic;
    }
    
    .expert-wisdom {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 0 12px 12px 0;
    }
    
    .scoring-breakdown {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .path-comparison {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .comparison-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid #444;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="path-hero">
    <h1>🛡️ The Six Sovereignty Paths</h1>
    <h3>Choose Your Journey to Personal Freedom</h3>
    <p style="font-size: 1.1em; margin-top: 1.5rem; color: #ccc;">
        Each path leads to sovereignty, but the emphasis and daily practices differ. 
        Choose the one that resonates with your current life situation and goals.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Path Selection Overview
st.markdown("## 🎯 How to Choose Your Path")

st.markdown("""
**All paths lead to sovereignty**, but they emphasize different domains and daily practices. Your chosen path determines:
- **Scoring weights** for different activities (where your points come from)
- **Expert guidance** and philosophical framework
- **Welcome messaging** and coaching tone
- **Focus areas** for optimization and growth

You can switch paths at any time, but **consistency within a chosen path builds the strongest foundation.**
""")

# Path 1: Default (Balanced)
st.markdown("---")
st.markdown("""
<div class="path-card">
    <h2>⚖️ Default Path: Balanced Sovereignty</h2>
    <p style="font-size: 1.1em; color: #ffcc00; margin-bottom: 1.5rem;">
        <strong>"Master the fundamentals before advancing to specialization"</strong>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Core Philosophy:** Balanced sovereignty across all domains of life. This path recognizes that true freedom 
requires competence in body, mind, and resources without over-specializing in any single area.

**Who This Path Serves:**
- **Sovereignty beginners** who want a well-rounded foundation
- **Busy professionals** who need sustainable, balanced practices
- **Recovering extremists** who've burned out on single-domain optimization
- **Anyone unsure** which specialized path to choose

**Daily Focus Areas:**
- **Physical:** Home cooking, exercise, strength training
- **Mental:** Meditation, gratitude, learning
- **Financial:** Basic spending discipline, Bitcoin accumulation
- **Environmental:** Occasional earth-friendly actions
""")

st.markdown("""
<div class="scoring-breakdown">
    <h4>🎯 Scoring Breakdown (Max 100 points)</h4>
    <ul>
        <li><strong>Home-cooked meals:</strong> 6.67 points × 3 meals = 20 points</li>
        <li><strong>No junk food:</strong> 10 points</li>
        <li><strong>Exercise minutes:</strong> 0.5 points × 40 max = 20 points</li>
        <li><strong>Strength training:</strong> 10 points</li>
        <li><strong>Meditation:</strong> 10 points</li>
        <li><strong>Gratitude:</strong> 5 points</li>
        <li><strong>Learning:</strong> 10 points</li>
        <li><strong>No spending:</strong> 5 points</li>
        <li><strong>Bitcoin investment:</strong> 5 points</li>
        <li><strong>Environmental action:</strong> 5 points</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Expert Integration:** Draws equally from all four experts—Huberman's protocols, Cavaliere's training, 
Pollan's food wisdom, and Hyman's systems thinking—without favoring any single approach.
""")

# Path 2: Financial Path
st.markdown("---")
st.markdown("""
<div class="path-card">
    <h2>💰 Financial Path: Economic Sovereignty</h2>
    <p style="font-size: 1.1em; color: #ffcc00; margin-bottom: 1.5rem;">
        <strong>"Every dollar not spent on consumption is a vote for your future freedom"</strong>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Core Philosophy:** Bitcoin and minimalism as paths to economic sovereignty. This path prioritizes 
aggressive saving, conservative living, and long-term wealth accumulation through sound money principles.

**Who This Path Serves:**
- **Bitcoin maximalists** who understand sound money principles
- **High earners** who want to optimize savings and investment
- **Debt escapees** focused on financial recovery and independence
- **Minimalists** who find freedom through intentional consumption

**Daily Focus Areas:**
- **Financial:** No discretionary spending (15 pts), Bitcoin DCA (15 pts)
- **Learning:** Reading and education heavily rewarded (15 pts)
- **Physical:** Basic maintenance through home cooking and exercise
- **Mental:** Light meditation and gratitude practice
""")

st.markdown("""
<div class="scoring-breakdown">
    <h4>🎯 Scoring Breakdown (Max 100 points)</h4>
    <ul>
        <li><strong>No discretionary spending:</strong> 15 points</li>
        <li><strong>Bitcoin investment:</strong> 15 points</li>
        <li><strong>Learning:</strong> 15 points</li>
        <li><strong>Home-cooked meals:</strong> 5 points × 3 meals = 15 points</li>
        <li><strong>Exercise minutes:</strong> 0.25 points × 40 max = 10 points</li>
        <li><strong>Gratitude:</strong> 10 points</li>
        <li><strong>No junk food:</strong> 5 points</li>
        <li><strong>Meditation:</strong> 5 points</li>
        <li><strong>Strength training:</strong> 5 points</li>
        <li><strong>Environmental action:</strong> 5 points</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Expert Integration:** Heavily influenced by Austrian economics and low time-preference thinking. 
Incorporates Pollan's cooking wisdom for cost savings and basic Huberman protocols for cognitive performance.

**Key Mantras:**
- "Stack sats, stay humble"
- "Live below your means, invest above your dreams"
- "Time preference is everything"
""")

# Path 3: Mental Resilience
st.markdown("---")
st.markdown("""
<div class="path-card">
    <h2>🧠 Mental Resilience Path: Cognitive Sovereignty</h2>
    <p style="font-size: 1.1em; color: #ffcc00; margin-bottom: 1.5rem;">
        <strong>"A disciplined mind cannot be conquered by external chaos"</strong>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Core Philosophy:** Inner strength as the foundation of all sovereignty. This path prioritizes mental 
anti-fragility, emotional regulation, and cognitive clarity through daily practices that build psychological resilience.

**Who This Path Serves:**
- **High-stress professionals** who need mental fortification
- **Anxiety sufferers** seeking natural regulation tools
- **Students and knowledge workers** optimizing cognitive performance
- **Anyone overwhelmed** by modern information chaos

**Daily Focus Areas:**
- **Mental:** Meditation (15 pts), gratitude (15 pts), learning (15 pts)
- **Physical:** Light exercise for stress relief and brain health
- **Financial:** Basic savings discipline
- **Cognitive:** Continuous learning and skill development
""")

st.markdown("""
<div class="scoring-breakdown">
    <h4>🎯 Scoring Breakdown (Max 100 points)</h4>
    <ul>
        <li><strong>Meditation:</strong> 15 points</li>
        <li><strong>Gratitude practice:</strong> 15 points</li>
        <li><strong>Learning:</strong> 15 points</li>
        <li><strong>Exercise minutes:</strong> 0.25 points × 40 max = 10 points</li>
        <li><strong>No junk food:</strong> 10 points</li>
        <li><strong>Home-cooked meals:</strong> 5 points × 3 meals = 15 points</li>
        <li><strong>No spending:</strong> 5 points</li>
        <li><strong>Strength training:</strong> 5 points</li>
        <li><strong>Bitcoin investment:</strong> 5 points</li>
        <li><strong>Environmental action:</strong> 5 points</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Expert Integration:** Heavily emphasizes Huberman's protocols for stress management, sleep optimization, 
and cognitive enhancement. Incorporates Pollan's mindful eating for mental clarity.

**Key Mantras:**
- "Still mind, strong heart"
- "Clarity is the ultimate currency"
- "Stress is information, not the enemy"
""")

# Path 4: Physical Optimization
st.markdown("---")
st.markdown("""
<div class="path-card">
    <h2>🏋️ Physical Optimization Path: Bodily Sovereignty</h2>
    <p style="font-size: 1.1em; color: #ffcc00; margin-bottom: 1.5rem;">
        <strong>"Your body is your most important asset—train it like one"</strong>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Core Philosophy:** Physical sovereignty as the foundation for all other freedoms. This path emphasizes 
progressive overload in strength, nutrition, and recovery to build an anti-fragile, high-performance body.

**Who This Path Serves:**
- **Athletes and fitness enthusiasts** seeking systematic optimization
- **Aging individuals** who want to maintain physical sovereignty
- **Former couch potatoes** ready for serious physical transformation
- **Anyone who believes** "strong body, sovereign life"

**Daily Focus Areas:**
- **Physical:** Strength training (15 pts), home cooking (8 pts per meal), exercise
- **Nutritional:** Emphasis on protein, whole foods, meal prep discipline
- **Recovery:** Sleep and stress management for adaptation
- **Mental:** Basic practices to support physical goals
""")

st.markdown("""
<div class="scoring-breakdown">
    <h4>🎯 Scoring Breakdown (Max 100 points)</h4>
    <ul>
        <li><strong>Home-cooked meals:</strong> 8 points × 3 meals = 24 points</li>
        <li><strong>Strength training:</strong> 15 points</li>
        <li><strong>Exercise minutes:</strong> 0.5 points × 40 max = 20 points</li>
        <li><strong>No junk food:</strong> 10 points</li>
        <li><strong>Meditation:</strong> 6 points</li>
        <li><strong>Learning:</strong> 5 points</li>
        <li><strong>Gratitude:</strong> 5 points</li>
        <li><strong>No spending:</strong> 5 points</li>
        <li><strong>Bitcoin investment:</strong> 5 points</li>
        <li><strong>Environmental action:</strong> 5 points</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Expert Integration:** Heavily emphasizes Cavaliere's training philosophy and Pollan's whole food approach. 
Incorporates Huberman's recovery and performance protocols.

**Key Mantras:**
- "Strong body, sovereign life"
- "Train hard, live free"
- "Recovery is earned through work"
""")

# Path 5: Spiritual Growth
st.markdown("---")
st.markdown("""
<div class="path-card">
    <h2>🧘 Spiritual Growth Path: Consciousness Sovereignty</h2>
    <p style="font-size: 1.1em; color: #ffcc00; margin-bottom: 1.5rem;">
        <strong>"True freedom is liberation from unconscious patterns and reactivity"</strong>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Core Philosophy:** Consciousness and presence as the deepest form of sovereignty. This path cultivates 
awareness, compassion, and mindful living as the foundation for all other freedoms.

**Who This Path Serves:**
- **Spiritual seekers** wanting practical daily practices
- **Burnout survivors** seeking meaning beyond material success
- **Environmental activists** connecting inner and outer healing
- **Anyone drawn to** contemplative traditions and conscious living

**Daily Focus Areas:**
- **Spiritual:** Meditation (20 pts), gratitude (15 pts), environmental action (10 pts)
- **Mindful Living:** Conscious consumption, earth-friendly choices
- **Physical:** Basic maintenance through gentle movement and clean eating
- **Learning:** Study of wisdom traditions and consciousness development
""")

st.markdown("""
<div class="scoring-breakdown">
    <h4>🎯 Scoring Breakdown (Max 100 points)</h4>
    <ul>
        <li><strong>Meditation:</strong> 20 points</li>
        <li><strong>Gratitude practice:</strong> 15 points</li>
        <li><strong>Learning:</strong> 10 points</li>
        <li><strong>Environmental action:</strong> 10 points</li>
        <li><strong>No junk food:</strong> 10 points</li>
        <li><strong>Exercise minutes:</strong> 0.25 points × 40 max = 10 points</li>
        <li><strong>Home-cooked meals:</strong> 3.33 points × 3 meals = 10 points</li>
        <li><strong>No spending:</strong> 5 points</li>
        <li><strong>Strength training:</strong> 5 points</li>
        <li><strong>Bitcoin investment:</strong> 5 points</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Expert Integration:** Emphasizes Pollan's mindful eating philosophy and Hyman's systems thinking. 
Incorporates contemplative practices and environmental consciousness.

**Key Mantras:**
- "Present moment, infinite possibilities"
- "Consciousness is sovereignty"
- "Inner peace, outer impact"
""")

# Path 6: Planetary Stewardship
st.markdown("---")
st.markdown("""
<div class="path-card">
    <h2>🌍 Planetary Stewardship Path: Ecological Sovereignty</h2>
    <p style="font-size: 1.1em; color: #ffcc00; margin-bottom: 1.5rem;">
        <strong>"What heals the earth heals the self—sovereignty and sustainability are one"</strong>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Core Philosophy:** Personal sovereignty aligned with planetary regeneration. This path recognizes that 
individual and ecological health are inseparable, emphasizing choices that heal both self and earth.

**Who This Path Serves:**
- **Environmental activists** seeking personal-political alignment
- **Climate-conscious individuals** wanting daily meaningful action
- **Systems thinkers** who understand interconnection
- **Future parents** concerned about the world they're leaving behind

**Daily Focus Areas:**
- **Environmental:** Environmental action (20 pts), reduced consumption focus
- **Physical:** Sustainable eating, local food, minimal processing
- **Financial:** Conscious spending, ethical investment
- **Learning:** Understanding of ecological systems and regenerative practices
""")

st.markdown("""
<div class="scoring-breakdown">
    <h4>🎯 Scoring Breakdown (Max 100 points)</h4>
    <ul>
        <li><strong>Environmental action:</strong> 20 points</li>
        <li><strong>Home-cooked meals:</strong> 5 points × 3 meals = 15 points</li>
        <li><strong>No spending:</strong> 10 points</li>
        <li><strong>No junk food:</strong> 10 points</li>
        <li><strong>Learning:</strong> 10 points</li>
        <li><strong>Exercise minutes:</strong> 0.25 points × 40 max = 10 points</li>
        <li><strong>Meditation:</strong> 10 points</li>
        <li><strong>Gratitude:</strong> 5 points</li>
        <li><strong>Bitcoin investment:</strong> 5 points</li>
        <li><strong>Strength training:</strong> 5 points</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Expert Integration:** Heavily emphasizes Hyman's regenerative health approach and Pollan's food system 
awareness. Focuses on sustainable practices that benefit both personal and planetary health.

**Key Mantras:**
- "Heal the soil, heal the soul"
- "Regenerative sovereignty"
- "Local action, global impact"
""")

# Path Comparison
st.markdown("---")
st.markdown("## 🎯 Path Comparison Overview")

st.markdown("""
<div class="path-comparison">
    <div class="comparison-card">
        <h4>⚖️ Default</h4>
        <p><strong>Best for:</strong> Beginners</p>
        <p><strong>Focus:</strong> Balance</p>
        <p><strong>Top Priority:</strong> Foundation building</p>
    </div>
    
    <div class="comparison-card">
        <h4>💰 Financial</h4>
        <p><strong>Best for:</strong> Bitcoin enthusiasts</p>
        <p><strong>Focus:</strong> Economic freedom</p>
        <p><strong>Top Priority:</strong> Savings & investment</p>
    </div>
    
    <div class="comparison-card">
        <h4>🧠 Mental Resilience</h4>
        <p><strong>Best for:</strong> Stress management</p>
        <p><strong>Focus:</strong> Cognitive strength</p>
        <p><strong>Top Priority:</strong> Inner stability</p>
    </div>
    
    <div class="comparison-card">
        <h4>🏋️ Physical</h4>
        <p><strong>Best for:</strong> Athletes</p>
        <p><strong>Focus:</strong> Body optimization</p>
        <p><strong>Top Priority:</strong> Strength & nutrition</p>
    </div>
    
    <div class="comparison-card">
        <h4>🧘 Spiritual</h4>
        <p><strong>Best for:</strong> Seekers</p>
        <p><strong>Focus:</strong> Consciousness</p>
        <p><strong>Top Priority:</strong> Presence & meaning</p>
    </div>
    
    <div class="comparison-card">
        <h4>🌍 Planetary</h4>
        <p><strong>Best for:</strong> Environmentalists</p>
        <p><strong>Focus:</strong> Sustainability</p>
        <p><strong>Top Priority:</strong> Earth healing</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Choosing Your Path
st.markdown("---")
st.markdown("## 🧭 Choosing Your Sovereignty Path")

st.markdown("""
**Questions to help you choose:**

1. **What domain feels most urgent in your life right now?**
   - Body breaking down → Physical Optimization
   - Mind overwhelmed → Mental Resilience  
   - Finances stressed → Financial Path
   - Seeking meaning → Spiritual Growth
   - Environmental anxiety → Planetary Stewardship
   - Want balance → Default Path

2. **Which expert's philosophy resonates most?**
   - Huberman (neuroscience) → Mental Resilience
   - Cavaliere (training) → Physical Optimization
   - Pollan (food wisdom) → Spiritual Growth or Default
   - Hyman (systems) → Planetary Stewardship
   - Austrian Economics → Financial Path

3. **What's your current life phase?**
   - **Beginning sovereignty journey:** Default Path
   - **High earning years:** Financial Path
   - **High stress period:** Mental Resilience
   - **Health transformation:** Physical Optimization
   - **Midlife meaning search:** Spiritual Growth
   - **Raising children:** Planetary Stewardship

4. **Which daily practices feel most natural?**
   - Love meditation → Spiritual Growth or Mental Resilience
   - Love lifting → Physical Optimization
   - Love learning → Financial Path or Mental Resilience
   - Love cooking → Physical Optimization or Default
   - Love nature → Planetary Stewardship

**Remember:** There's no wrong choice. You can switch paths at any time, but consistency within a chosen path builds the strongest foundation.
""")

# Call to Action
st.markdown("---")
st.markdown("## 🚀 Ready to Choose Your Path?")

cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])

with cta_col2:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: rgba(255, 204, 0, 0.1); border: 2px solid rgba(255, 204, 0, 0.3); border-radius: 12px;">
        <h3 style="color: #ffcc00; margin-bottom: 1rem;">Begin Your Sovereignty Journey</h3>
        <p style="margin-bottom: 1.5rem;">Choose your path and start tracking your daily sovereignty.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🛡️ Start Tracking Sovereignty", type="primary", use_container_width=True):
        st.success("🎯 Ready to begin! Head to the landing page to register and choose your path.")
        st.markdown("[🏠 Go to Landing Page](https://dmh4681.github.io/sovereignty-score/)")

st.markdown("---")

# Footer
st.markdown("""
<div style="text-align: center; color: #888; margin-top: 3rem;">
    <p><em>"All paths lead to sovereignty, but each path walks differently."</em></p>
    <p>🛡️ Choose your journey. Walk with intention. Arrive at freedom.</p>
</div>
""", unsafe_allow_html=True)