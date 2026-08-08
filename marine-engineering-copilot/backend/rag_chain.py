"""
Marine Guardian AI — RAG Chain

Connects ChromaDB retrieval with LLM using a marine-specific
system prompt. Ensures strict numerical grounding, query-aware 
retrieval, and hallucination prevention.
"""

import os
import re
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config import (
    CHROMA_DB_DIR, EMBEDDING_MODEL, CHROMA_COLLECTION_NAME,
    RETRIEVAL_TOP_K, SIMILARITY_THRESHOLD
)
from llm_provider import get_llm


# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------

MARINE_COPILOT_PROMPT = """\
You are the **Marine Guardian AI Engineering Copilot**, a senior marine engineering assistant aboard a merchant vessel. You speak naturally, as one experienced engineer talking to another. You are integrated with live ship telemetry, predictive analytics, maintenance records, and the vessel's technical knowledge base.

## HOW TO ANSWER

CRITICAL: You MUST provide extremely short and quick answers.
- Provide exactly 1 to 2 concise sentences of explanation, diagnosis, or recommendation.
- Always include the relevant sensor values in a short bulleted list.
- Do NOT provide long, detailed, multi-step troubleshooting guides unless explicitly requested.
- Do NOT pad responses with pleasantries or unnecessary context.

## CONVERSATIONAL CONTINUITY

Use the CONVERSATION HISTORY to understand references like "that", "it", "this", "those", or implicit continuations like "Is that dangerous?", "What should I check first?". Resolve these naturally without asking for clarification unless the reference is genuinely ambiguous.

## ENGINEERING RATIONALE (NOT Chain-of-Thought)

When explaining your reasoning, provide a concise, evidence-grounded engineering rationale. Example:

"Engineering rationale: The current vibration is elevated and previous maintenance records show bearing-related events. This makes a bearing-related issue plausible, but the available evidence does not confirm bearing failure."

Do NOT expose hidden internal reasoning steps. Do NOT fabricate causal relationships.

Every conclusion must trace to at least one of: retrieved documentation, current telemetry, AI predictions, active alarms, maintenance history, or previous conversation context.

## SOURCE-AWARE REASONING

When combining multiple evidence sources, distinguish them clearly using these categories (only show categories that have relevant data):

📘 DOCUMENT — Retrieved manuals, SOPs, procedures
📊 SENSOR — Current telemetry readings
🤖 PREDICTION — AI predictive analytics
🚨 ALARM — Active fault conditions
🛠 HISTORY — Maintenance records
💬 CONVERSATION — Previous conversation context

## NUMERICAL & SENSOR GROUNDING [STRICT]

For any torque, pressure, temperature, RPM, vibration, clearance, dimension, maintenance interval, operating limit, or specification:
- You MUST use the exact value from the retrieved evidence.
- NEVER invent, estimate, or guess a value.
- NEVER call a sensor reading "normal", "safe", "acceptable", or "within range" unless the documentation EXPLICITLY establishes the approved operating range.
- NEVER agree with a user's claim about a value being within range unless the documentation confirms the range.
- If you cannot verify: "I couldn't find a verified specification for that value in the available documentation."
- If the user states a value is within range and asks you to confirm, but no range is documented: "The current reading is [X], but I cannot confirm it is within the manufacturer's approved range because the available documentation does not establish that limit."

## ENGINE-SPECIFIC GROUNDING [STRICT]

Do NOT assume a general specification applies to a specific engine (e.g., Engine 1, Engine 2, Engine 3) unless the evidence explicitly establishes that relationship.

Fallback: "The retrieved documentation specifies [X], but the available evidence does not explicitly confirm that this specification applies to [Engine N]."

## UNCERTAINTY & CONFLICTS

Be comfortable saying: "I don't have enough evidence to determine that."

If sources conflict, explain the conflict rather than silently choosing one.

## SAFETY BOUNDARY

You are an engineering decision-support assistant. Your responses do NOT override manufacturer instructions, vessel SMS, classification society requirements, or approved operating procedures. For high-risk actions, clearly distinguish between "Recommended check" and "Required action according to the documented procedure."

## FOLLOW-UP SUGGESTIONS

When appropriate, naturally offer to check related data — e.g., "I can also check the maintenance history for previous occurrences if you'd like." Do not repeatedly ask unnecessary questions.

## EVIDENCE MODE

When the user asks "Show me the source", "What supports your answer?", "Where did you get this?", "Show me the evidence", or similar, respond using this format:

### Evidence

📘 **Source:** [Document Name]
📍 **Location:** Page [X] / Section [Y]
**Evidence:** [Concise summary of the actual retrieved content]
**Why it matters:** [How this evidence supports the answer]

(Repeat for each source used.)

Never fabricate page numbers, sections, quotes, or evidence.

## CITATIONS

At the end of your response, list ONLY the sources you ACTUALLY used to formulate your answer. Do NOT list retrieved documents that were irrelevant. Use this format:

### Sources Used

📘 [Document Name] — Page [X]

For maintenance logs:
🛠 Maintenance Log — [Date] / [Equipment]

For telemetry:
📊 Current Sensor — [Parameter]: [Value]

For predictions:
🤖 AI Prediction — [Key metric]

## WHAT NOT TO DO

- Do NOT respond like a search engine, PDF summarizer, or robotic FAQ system.
- Do NOT say "According to Document 1… According to Document 2…" — synthesize naturally.
- Do NOT list all retrieved documents — only cite what you actually used.
- Do NOT expose internal chain-of-thought.
- Do NOT invent emergency procedures.
- Do NOT fabricate numerical confidence scores (use natural language: high/moderate/low confidence).

---

{context}

---
CONVERSATION HISTORY:
{chat_history}

---
CURRENT QUESTION:
{question}

Respond as a knowledgeable marine engineering copilot, strictly grounded in the evidence above.
"""


# ---------------------------------------------------------------------------
# Retriever
# ---------------------------------------------------------------------------

def get_retriever():
    """Returns the raw vectorstore for custom dual retrieval."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings,
        collection_name=CHROMA_COLLECTION_NAME,
    )
    return vectorstore


# ---------------------------------------------------------------------------
# Equipment keyword extraction (for query-aware filtering)
# ---------------------------------------------------------------------------

def extract_equipment_keywords(query: str) -> list[str]:
    """Extract potential equipment keywords from query for query-aware filtering."""
    query = query.lower()
    keywords = []
    if "bearing" in query: keywords.append("bearing")
    if "overheat" in query or "cooling" in query or "temperature" in query: keywords.append("overheat")
    if "fuel" in query: keywords.append("fuel")
    if "injector" in query: keywords.append("injector")
    if "pump" in query: keywords.append("pump")
    if "engine 1" in query or "main engine 1" in query: keywords.append("engine 1")
    if "engine 2" in query or "main engine 2" in query: keywords.append("engine 2")
    if "engine 3" in query or "main engine 3" in query: keywords.append("engine 3")
    if "vibration" in query: keywords.append("vibration")
    if "torque" in query: keywords.append("torque")
    if "exhaust" in query: keywords.append("exhaust")
    if "turbocharger" in query or "turbo" in query: keywords.append("turbocharger")
    if "lubrication" in query or "lube" in query or "oil" in query: keywords.append("lubrication")
    if "generator" in query: keywords.append("generator")
    if "boiler" in query: keywords.append("boiler")
    if "shaft" in query: keywords.append("shaft")
    return keywords


# ---------------------------------------------------------------------------
# Diverse retrieval with relevance scoring
# ---------------------------------------------------------------------------

def retrieve_diverse_context(vectorstore, question: str) -> list:
    """Retrieve documents using relevance scores and query-aware metadata filtering."""
    keywords = extract_equipment_keywords(question)
    
    # Diverse retrieval by document_type
    results = []
    
    try:
        sops = vectorstore.similarity_search_with_relevance_scores(question, k=5, filter={"document_type": "SOP"})
        results.extend(sops)
    except Exception: pass
    
    try:
        manuals = vectorstore.similarity_search_with_relevance_scores(question, k=5, filter={"document_type": "manual"})
        results.extend(manuals)
    except Exception: pass
    
    try:
        logs = vectorstore.similarity_search_with_relevance_scores(question, k=5, filter={"document_type": "maintenance_log"})
        results.extend(logs)
    except Exception: pass
    
    # Base general search
    general = vectorstore.similarity_search_with_relevance_scores(question, k=10)
    results.extend(general)
    unique_results = {}
    for doc, score in results:
        if score >= SIMILARITY_THRESHOLD:
            # If we have keywords, boost the score of documents that contain the keywords
            # so they get prioritized, or just filter. We'll boost score if it matches keyword.
            equip_hint = doc.metadata.get('equipment_hint', '').lower()
            doc_score = score
            if keywords:
                for kw in keywords:
                    if kw in equip_hint:
                        doc_score += 0.2  # significant relevance boost for matching equipment
                        break
                        
            if doc.page_content not in unique_results or unique_results[doc.page_content][1] < doc_score:
                unique_results[doc.page_content] = (doc, doc_score)
                
    # Sort by relevance (descending)
    sorted_results = sorted(unique_results.values(), key=lambda x: x[1], reverse=True)
    
    # Return top K
    return sorted_results[:RETRIEVAL_TOP_K]


# ---------------------------------------------------------------------------
# Context formatting (improved for LLM clarity)
# ---------------------------------------------------------------------------

def format_retrieved_docs(docs_with_scores) -> str:
    """Format retrieved documents for the LLM context with clear structure."""
    formatted = []
    for i, (doc, score) in enumerate(docs_with_scores, 1):
        source = doc.metadata.get('source_file', 'Unknown')
        doc_type = doc.metadata.get('document_type', 'document')
        page = doc.metadata.get('page', 'N/A')
        equip = doc.metadata.get('equipment_hint', '')

        # Use icons based on document type
        if doc_type in ('SOP', 'manual'):
            icon = "📘"
            type_label = "DOCUMENT"
        elif doc_type == 'maintenance_log':
            icon = "🛠"
            type_label = "MAINTENANCE RECORD"
        else:
            icon = "📄"
            type_label = "DOCUMENT"

        header = f"{icon} EVIDENCE [{i}] ({type_label})"
        meta = f"Source: {source} | Page: {page}"
        if equip:
            meta += f" | Equipment: {equip}"
        
        formatted.append(f"{header}\n{meta}\nContent:\n{doc.page_content}")

    return "\n\n---\n\n".join(formatted) if formatted else "No relevant documents found in the knowledge base."


def build_operational_context(sensor_data: dict, predictions: dict,
                               alarms: list, maintenance: list,
                               equipment_maintenance: list = None) -> str:
    """Build a structured operational context string for the LLM with clear source-type headers."""
    lines = []

    # Sensors
    lines.append("📊 CURRENT TELEMETRY:")
    lines.append(f"  Engine ID: {sensor_data.get('engine_id', 'N/A')}")
    lines.append(f"  Timestamp: {sensor_data.get('timestamp', 'N/A')}")
    lines.append(f"  Engine Temperature: {sensor_data.get('engine_temperature', 'N/A')}°C")
    lines.append(f"  Oil Pressure: {sensor_data.get('oil_pressure', 'N/A')} bar")
    lines.append(f"  Fuel Pressure: {sensor_data.get('fuel_pressure', 'N/A')} bar")
    lines.append(f"  Vibration Level: {sensor_data.get('vibration_level', 'N/A')} mm/s")
    lines.append(f"  RPM: {sensor_data.get('rpm', 'N/A')}")
    lines.append(f"  Engine Load: {sensor_data.get('engine_load', 'N/A')}%")
    lines.append(f"  Coolant Temperature: {sensor_data.get('coolant_temperature', 'N/A')}°C")
    lines.append(f"  Exhaust Temperature: {sensor_data.get('exhaust_temperature', 'N/A')}°C")
    lines.append(f"  Running Period: {sensor_data.get('running_period', 'N/A')} hrs")
    lines.append(f"  Fuel Consumption: {sensor_data.get('fuel_consumption', 'N/A')} L/h")
    lines.append(f"  Maintenance: {sensor_data.get('maintenance', 'N/A')}")
    lines.append(f"  Engine Type: {sensor_data.get('engine_type', 'N/A')}")
    lines.append(f"  Fuel Type: {sensor_data.get('fuel_type', 'N/A')}")
    lines.append(f"  Manufacturer: {sensor_data.get('manufacturer', 'N/A')}")
    
    fault = sensor_data.get('fault_label', 'Normal')
    if fault and fault != 'Normal':
        lines.append(f"  ⚠ Active Fault Label: {fault}")

    # Predictions (New Schema)
    lines.append("\n🤖 AI PREDICTIONS:")
    lines.append(f"  Engine ID: {predictions.get('engine_id', 'N/A')}")
    lines.append(f"  Health Score: {predictions.get('health_score', 'N/A')}/100")
    lines.append(f"  Failure Probability: {predictions.get('failure_probability', 'N/A')}%")
    lines.append(f"  Remaining Useful Life: {predictions.get('remaining_useful_life', 'N/A')} hours")
    lines.append(f"  Maintenance Recommendation: {predictions.get('maintenance_recommendation', 'N/A')}")
    lines.append(f"  Fault Type: {predictions.get('fault_type', 'N/A')}")

    # Alarms
    lines.append("\n🚨 ACTIVE ALARMS:")
    if alarms:
        for a in alarms:
            lines.append(f"  ⚠ {a.get('fault_label', 'Unknown')} at {a.get('timestamp', 'N/A')} "
                        f"(RPM={a.get('rpm', 'N/A')}, Temp={a.get('temperature', 'N/A')}°C, "
                        f"Vibration={a.get('vibration', 'N/A')} mm/s)")
    else:
        lines.append("  No active alarms.")

    # General recent maintenance
    lines.append("\n🛠 RECENT MAINTENANCE HISTORY:")
    if maintenance:
        for m in maintenance:
            lines.append(f"  [{m.get('date', 'N/A')}] {m.get('equipment', 'N/A')}: "
                        f"{m.get('fault', 'N/A')} → {m.get('action_taken', 'N/A')} "
                        f"(Severity: {m.get('severity', 'N/A')})")
    else:
        lines.append("  No recent maintenance records.")

    # Equipment-specific maintenance (supplementary — constraint #2)
    if equipment_maintenance:
        lines.append("\n🛠 EQUIPMENT-SPECIFIC MAINTENANCE HISTORY (supplementary):")
        for m in equipment_maintenance:
            lines.append(f"  [{m.get('date', 'N/A')}] {m.get('equipment', 'N/A')}: "
                        f"{m.get('fault', 'N/A')} → {m.get('action_taken', 'N/A')} "
                        f"(Severity: {m.get('severity', 'N/A')})")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Source-usage tracking (constraint #3)
# ---------------------------------------------------------------------------

def extract_used_source_ids(response_text: str, sources: list[dict]) -> list[dict]:
    """
    Identify which retrieved sources were actually referenced in the LLM response.
    
    Heuristic: A source is considered "used" if the response mentions its filename
    (without extension), equipment hint, or key content terms.
    If the LLM cited no identifiable sources, return all sources as fallback
    (the LLM may have synthesized across all of them).
    """
    if not sources:
        return []
    
    response_lower = response_text.lower()
    used = []
    
    for src in sources:
        source_file = src.get('source_file', '')
        equipment_hint = src.get('equipment_hint', '')
        doc_type = src.get('document_type', '')
        
        # Check if the source name (minus extension) appears in the response
        name_no_ext = source_file.rsplit('.', 1)[0].replace('_', ' ').lower()
        name_parts = [p for p in name_no_ext.split() if len(p) > 3]  # meaningful words
        
        # Check equipment hint
        equip_parts = [p for p in equipment_hint.lower().split() if len(p) > 3]
        
        matched = False
        
        # Match by filename fragments
        if name_parts:
            match_count = sum(1 for p in name_parts if p in response_lower)
            if match_count >= min(2, len(name_parts)):
                matched = True
        
        # Match by equipment hint
        if not matched and equip_parts:
            match_count = sum(1 for p in equip_parts if p in response_lower)
            if match_count >= min(2, len(equip_parts)):
                matched = True
        
        # Match if the response explicitly mentions the source file
        if not matched and source_file.lower().replace('_', ' ').replace('.pdf', '') in response_lower:
            matched = True
            
        # Match maintenance logs if the response mentions maintenance/history
        if not matched and doc_type == 'maintenance_log':
            if any(kw in response_lower for kw in ['maintenance history', 'maintenance record',
                                                      'maintenance log', 'previous maintenance',
                                                      'historically', 'past maintenance',
                                                      '🛠']):
                matched = True
        
        if matched:
            used.append(src)
    
    # Fallback: if nothing matched but the LLM clearly produced a substantive answer,
    # return all sources (the LLM synthesized across them)
    if not used and len(response_text.strip()) > 100:
        return sources
    
    return used


# ---------------------------------------------------------------------------
# RAG Chain
# ---------------------------------------------------------------------------

def get_rag_chain():
    """Build the RAG chain with marine-specific prompt and source citations."""
    vectorstore = get_retriever()
    llm = get_llm()
    prompt = PromptTemplate.from_template(MARINE_COPILOT_PROMPT)

    def invoke_chain(inputs: dict) -> dict:
        """Custom chain that returns both the response and sources."""
        question = inputs["question"]
        retrieval_query = inputs.get("retrieval_query", question)
        live_data = inputs.get("live_data", "No operational data available.")
        chat_history = inputs.get("chat_history", "No previous conversation.")

        # 1. Retrieve diverse documents (use expanded query for retrieval)
        retrieved_docs_with_scores = retrieve_diverse_context(vectorstore, retrieval_query)

        # 2. Format Context for LLM
        doc_context_str = format_retrieved_docs(retrieved_docs_with_scores)
        
        full_context = f"DOCUMENT CONTEXT:\n{doc_context_str}\n\n{live_data}"

        # 3. Build prompt
        formatted_prompt = prompt.format(
            context=full_context,
            chat_history=chat_history,
            question=question,
        )

        # 4. Get LLM response
        response = llm.invoke(formatted_prompt)
        response_text = StrOutputParser().invoke(response)

        # 5. Extract ALL source metadata
        all_sources = []
        for doc, score in retrieved_docs_with_scores:
            all_sources.append({
                "source_file": doc.metadata.get('source_file', 'Unknown'),
                "document_type": doc.metadata.get('document_type', 'document'),
                "page": doc.metadata.get('page', 'N/A'),
                "equipment_hint": doc.metadata.get('equipment_hint', ''),
                "score": float(score)
            })

        # 6. Filter to only sources actually used in the response (constraint #3)
        used_sources = extract_used_source_ids(response_text, all_sources)

        return {
            "response": response_text,
            "sources": used_sources,
            "all_sources": all_sources,  # keep for debugging
        }

    return invoke_chain
