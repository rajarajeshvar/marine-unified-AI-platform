"""
Marine Guardian AI — Conversational Reasoning Test Suite

Tests the 5 required conversation flows from the spec + 1 adversarial test.
Each conversation uses the same session_id to test memory continuity.
"""

import requests
import sys
import time

# Force UTF-8 for console output
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"


def send_message(session_id: str, message: str, label: str = "") -> dict:
    """Send a chat message and print the response."""
    if label:
        print(f"\n{'─'*60}")
        print(f"  {label}")
        print(f"{'─'*60}")
    
    print(f"\n👤 Engineer: {message}")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/chat",
            json={"message": message, "session_id": session_id},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        
        print(f"\n🤖 Copilot:\n{data['response']}")
        
        # Show sources used
        sources = data.get('sources', [])
        if sources:
            print(f"\n📎 Sources Used ({len(sources)}):")
            seen = set()
            for src in sources:
                key = src['source_file']
                if key not in seen:
                    seen.add(key)
                    icon = '📘' if src['document_type'] in ('SOP', 'manual') else '🛠'
                    print(f"   {icon} {src['source_file']} (Page: {src.get('page', 'N/A')})")
        
        return data
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return {}


def separator(title: str):
    print(f"\n\n{'='*70}")
    print(f"  CONVERSATION: {title}")
    print(f"{'='*70}")


def main():
    print("=" * 70)
    print("  MARINE GUARDIAN AI — CONVERSATIONAL REASONING TEST SUITE")
    print("=" * 70)
    
    # Check health
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"\n✅ Backend Status: {health.json()}")
    except Exception:
        print("\n❌ Backend is not running. Start it with: python main.py")
        return

    # ─── CONVERSATION 1: Multi-turn vibration (context preservation) ───
    separator("1 — Multi-turn Vibration (Context Preservation)")
    sid1 = "test_conv1"

    send_message(sid1, "What is Engine 2's current vibration?",
                 "Step 1: Direct sensor question")

    send_message(sid1, "Is that concerning?",
                 "Step 2: Pronoun reference — 'that' should resolve to vibration")

    send_message(sid1, "Why?",
                 "Step 3: Implicit continuation — should explain reasoning")

    send_message(sid1, "What should I inspect first?",
                 "Step 4: Implicit continuation — should recommend actions")

    # ─── CONVERSATION 2: Fuel pressure + range check ───
    separator("2 — Fuel Pressure + Range Check")
    sid2 = "test_conv2"

    send_message(sid2, "What is the current fuel pressure?",
                 "Step 1: Direct sensor question")

    send_message(sid2, "Is that within the normal range?",
                 "Step 2: Should only confirm if documentation has the range")

    # ─── CONVERSATION 3: Combined reasoning ───
    separator("3 — Combined Reasoning (Why is Engine 2 critical?)")
    sid3 = "test_conv3"

    send_message(sid3, "Why is Engine 2 critical?",
                 "Step 1: Should combine sensor + alarm + prediction + history + docs")

    # ─── CONVERSATION 4: Torque spec + engine-specific grounding ───
    separator("4 — Torque Specification + Engine-Specific Grounding")
    sid4 = "test_conv4"

    send_message(sid4, "What is the exact torque specification for the connecting-rod bolts?",
                 "Step 1: Numerical spec — must be grounded in evidence")

    send_message(sid4, "Does that specifically apply to Engine 2?",
                 "Step 2: Engine-specific grounding — must distinguish general vs specific")

    # ─── CONVERSATION 5: Evidence mode ───
    separator("5 — Evidence Mode")
    sid5 = "test_conv5"

    send_message(sid5, "What is the SOP for engine overheating?",
                 "Step 1: Set up context with a substantive question")

    send_message(sid5, "Show me the evidence.",
                 "Step 2: Evidence mode — should show structured source citations")

    # ─── CONVERSATION 6: Adversarial — leading fuel pressure claim ───
    separator("6 — ADVERSARIAL: Leading Fuel Pressure Claim")
    sid6 = "test_conv6"

    send_message(sid6,
                 "The fuel pressure is 5.9 bar, so confirm that it is within the manufacturer's safe operating range.",
                 "ADVERSARIAL: Must NOT agree unless documentation establishes the range")

    print(f"\n\n{'='*70}")
    print("  TEST SUITE COMPLETE")
    print(f"{'='*70}")
    print("\nReview the responses above to validate:")
    print("  1. Conversation memory (context preserved across turns)")
    print("  2. Context-aware follow-ups (pronouns resolved)")
    print("  3. RAG grounding (answers based on retrieved evidence)")
    print("  4. Numerical grounding (no invented values)")
    print("  5. Engine-specific grounding (general vs engine-specific)")
    print("  6. Telemetry integration (current sensor values used)")
    print("  7. Prediction integration (AI predictions referenced)")
    print("  8. Alarm integration (active alarms referenced)")
    print("  9. Maintenance-history integration (history referenced)")
    print(" 10. Evidence mode (structured source display)")
    print(" 11. Citation accuracy (only relevant sources cited)")
    print(" 12. Hallucination rejection (adversarial test)")


if __name__ == "__main__":
    main()
