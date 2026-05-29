"""
IMPROVED AI Advisor - Context-Aware Skincare Chatbot
Now responds differently based on user's ACTUAL skin conditions
"""

def get_ai_advice(skin_score, acne_count, severity, question, acne_details=None):
    """
    Calls Claude AI with RICH CONTEXT about the user's skin.
    Different questions get different answers based on actual skin analysis.
    """
    try:
        import anthropic

        # ── BUILD RICH CONTEXT ──────────────────────────
        context_lines = [
            f"Skin Health Score: {skin_score}/100",
            f"Severity Level: {severity}",
            f"Acne Spots Detected: {acne_count}",
        ]
        
        if acne_details:
            if acne_details.get('redness_percent', 0) > 15:
                context_lines.append(f"Redness detected: {acne_details['redness_percent']:.0f}% of face")
            if acne_details.get('oiliness_percent', 0) > 40:
                context_lines.append(f"Oily skin: {acne_details['oiliness_percent']:.0f}% oily regions")
            if acne_details.get('dark_spot_count', 0) > 0:
                context_lines.append(f"Dark spots: {acne_details['dark_spot_count']} detected")
        
        context_str = "\n".join(context_lines)
        
        # ── BUILD SPECIALIZED SYSTEM PROMPT ─────────────
        # The prompt changes based on what problem is most evident
        system_prompt = build_system_prompt(severity, acne_count, acne_details)
        
        # ── CALL CLAUDE ─────────────────────────────────
        client = anthropic.Anthropic()
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=350,
            system=system_prompt + f"\n\nUSER'S SKIN ANALYSIS:\n{context_str}",
            messages=[{"role": "user", "content": question}]
        )
        
        return message.content[0].text
        
    except ImportError:
        return "AI advisor requires 'anthropic' library. Run: pip install anthropic"
    except Exception as e:
        print(f"AI Advisor error: {e}")
        return "AI advisor temporarily unavailable. Check your ANTHROPIC_API_KEY."


def build_system_prompt(severity, acne_count, acne_details=None):
    """
    Build a SPECIALIZED system prompt that changes based on the user's skin condition.
    This makes the AI give more relevant, targeted advice.
    """
    
    base = """You are SkinAI, a professional AI skincare advisor. Your role is to:
1. Provide evidence-based skincare advice
2. Give specific product recommendations (by ingredient, not brand names)
3. Explain the science behind skincare
4. Be encouraging and supportive
5. Keep answers under 150 words
6. Never suggest they ignore professional medical advice

IMPORTANT: Answer the USER'S QUESTION directly and specifically based on their skin condition."""
    
    # ── CUSTOMIZE BASED ON SEVERITY ─────────────────
    if severity == "Clear":
        specialized = """
SKIN CONDITION: Clear skin ✨
Your user has excellent skin. Your advice should focus on:
- Maintaining their current routine
- Prevention strategies (sun protection, hydration)
- Advanced skincare (serums, treatments that are nice-to-have)
- Long-term skin health"""
    
    elif severity == "Mild":
        specialized = """
SKIN CONDITION: Mild acne/issues
Your user has some breakouts or minor concerns. Your advice should:
- Suggest gentle treatments (salicylic acid 0.5-2%, niacinamide)
- Emphasize lifestyle: sleep, water, stress
- Address the ROOT CAUSE (oiliness? hormones? diet?)
- Give step-by-step routine advice
- Avoid over-treating which makes it worse"""
    
    elif severity == "Moderate":
        specialized = """
SKIN CONDITION: Moderate acne/issues
Your user has noticeable breakouts or significant skin problems. Your advice should:
- Suggest clinical-strength treatments (benzoyl peroxide, salicylic acid 2%+)
- Address underlying causes (hormonal? dietary?)
- Explain when to see a dermatologist
- Discuss combination therapy approach
- Be realistic about timeline (8-12 weeks to see improvement)
- Warn about potential irritation from stronger treatments"""
    
    else:  # Severe
        specialized = """
SKIN CONDITION: Severe acne/significant issues
Your user has extensive breakouts or serious skin problems. Your advice should:
- STRONGLY RECOMMEND seeing a dermatologist soon
- Explain why prescription medications may be needed
- Discuss professional treatments (laser, chemical peels)
- Address psychological impact of severe acne
- Explain how to prevent scarring
- Be supportive — this is treatable but needs professional help
- NOT minimize the severity or suggest DIY-only solutions"""
    
    # ── ACNE-SPECIFIC CUSTOMIZATION ─────────────────
    if acne_count > 8:
        specialized += """

FOCUS AREA: Multiple breakouts
This user needs:
- Multi-step acne regimen (not just one product)
- Understanding that acne takes time to heal (don't switch products every week)
- Lifestyle advice: pillowcase changes, phone hygiene, not touching face
- Possible hormonal or dietary triggers to investigate"""
    
    elif acne_count > 0:
        specialized += """

FOCUS AREA: Occasional breakouts
This user probably needs:
- Spot treatment (not full-face acne treatment)
- Trigger identification: stress? diet? products?
- Preventive routine rather than intensive treatment"""
    
    # ── OILINESS CUSTOMIZATION ─────────────────────
    if acne_details and acne_details.get('oiliness_percent', 0) > 50:
        specialized += """

FOCUS AREA: Very oily skin
This user should hear about:
- Lightweight, non-comedogenic products
- Matifying moisturizers (not heavy creams)
- Blotting papers instead of touching face
- How diet (high omega-6 oils) impacts sebum production
- Weekly exfoliation to prevent pore clogging"""
    
    # ── REDNESS CUSTOMIZATION ───────────────────────
    if acne_details and acne_details.get('redness_percent', 0) > 25:
        specialized += """

FOCUS AREA: Significant redness
This user needs:
- Calming ingredients: azelaic acid, niacinamide, centella asiatica
- UV protection (prevents redness from getting darker)
- Avoid triggers: spicy food, alcohol, hot showers
- Anti-inflammatory approach (not just acne-focused)"""
    
    return base + "\n" + specialized