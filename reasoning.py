from retrieval import retrieve_evidence
from nli_verifier import nli_classify

def aggregate_states(evidence, char):
    states = {
        "dead": {"count": 0, "explicit": 0, "chunks": []},
        "paralyzed": {"count": 0, "explicit": 0, "chunks": []}
    }

    for c in evidence:
        meta = c.get("character_state_metadata", {}).get(char, {})

        if meta.get("life_state") == "dead":
            states["dead"]["count"] += 1
            states["dead"]["chunks"].append(c.get("text", "")[:100])
            if char in c.get("characters_explicit", []):
                states["dead"]["explicit"] += 1

        if meta.get("physical_state") == "paralyzed":
            states["paralyzed"]["count"] += 1
            states["paralyzed"]["chunks"].append(c.get("text", "")[:100])
            if char in c.get("characters_explicit", []):
                states["paralyzed"]["explicit"] += 1

    return states

def violates_state(claim_text, states):
    t = claim_text.lower()
    violations = []

    dead_confidence = (
        states["dead"]["count"] >= 2 and
        states["dead"]["explicit"] >= 1
    )

    if dead_confidence:
        for action in ["escaped", "met", "travel", "visited", "trained", "fought", "joined"]:
            if action in t:
                violations.append(f"dead character cannot {action}")
                return True, violations

    paralyzed_confidence = (
        states["paralyzed"]["count"] >= 2 and
        states["paralyzed"]["explicit"] >= 1
    )

    if paralyzed_confidence:
        for action in ["walked", "ran", "trained", "fought"]:
            if action in t:
                violations.append(f"paralyzed character cannot {action}")
                return True, violations

    return False, violations

def is_interpretive_claim(text):
    cues = [
        "belief", "hope", "ideal", "felt", "absorbed",
        "shaped", "deepened", "sustained", "enthusiasm",
        "distrust", "ethic", "worldview", "spirit",
        "outlook", "conviction"
    ]
    found = [c for c in cues if c in text.lower()]
    return len(found) > 0, found

def is_concrete_event(text):
    cues = [
        " in 17", " in 18", " in 19",
        " at ", " during ", " after ",
        " burned", " signed", " married",
        " executed", " arranged", " drowned"
    ]
    found = [c.strip() for c in cues if c in text.lower()]
    return len(found) > 0, found

def is_specific_factual_claim(text):
    t = text.lower()
    
    profession_patterns = [
        " was a ", " was an ", " worked as ", " served as ",
        " became a ", " became an "
    ]
    
    location_patterns = [
        " lived in ", " lived at ", " resided in ",
        " traveled to ", " went to ", " visited ",
        " born in ", " died in "
    ]
    
    relationship_patterns = [
        " married ", " wife of ", " husband of ",
        " son of ", " daughter of ", " father of ", " mother of ",
        " brother of ", " sister of "
    ]
    
    specific_action_patterns = [
        " built ", " created ", " founded ",
        " killed ", " murdered ", " assassinated ",
        " owned ", " purchased ", " sold "
    ]
    
    all_patterns = (profession_patterns + location_patterns + 
                   relationship_patterns + specific_action_patterns)
    
    has_specific_pattern = any(pattern in t for pattern in all_patterns)
    
    vague_indicators = [
        "might", "maybe", "possibly", "could have", "perhaps",
        "likely", "probably", "seemed", "appeared"
    ]
    has_vague = any(indicator in t for indicator in vague_indicators)
    
    general_descriptors = [
        "good", "bad", "kind", "cruel", "happy", "sad",
        "brave", "cowardly", "honest", "dishonest"
    ]
    only_general = any(desc in t for desc in general_descriptors) and not has_specific_pattern
    
    if has_vague or only_general:
        return False
    
    return has_specific_pattern

def nli_polarity(nli_results):
    support = contradict = neutral = 0
    contradict_scores = []
    support_scores = []
    
    for r in nli_results:
        if r["scores"]["contradiction"] >= 0.85:
            contradict += 1
            contradict_scores.append(r["scores"]["contradiction"])
        elif r["scores"]["entailment"] >= 0.85:
            support += 1
            support_scores.append(r["scores"]["entailment"])
        else:
            neutral += 1
            
    return support, contradict, neutral, support_scores, contradict_scores

def build_pathway_table(pathway):
    return {
        "state_conflict": "STATE_CONFLICT" in pathway,
        "nli_contradiction": "NLI_CONTRADICTION_FOUND" in pathway,
        "nli_support": "NLI_SUPPORT_FOUND" in pathway,
        "interpretive_override": "CONTRADICTION_IGNORED_INTERPRETIVE" in pathway,
        "concrete_event_rejected": "CONCRETE_EVENT_UNSUPPORTED" in pathway,
        "fallback": "NO_DECISIVE_EVIDENCE_ASSUME_CONSISTENT" in pathway
    }

def generate_rationale(pathway, states, support_count, contradict_count, evidence_count, 
                       claim_text, state_violations, interpretive_cues, concrete_cues,
                       support_scores, contradict_scores):
    
    if "NO_EVIDENCE_REJECT_SPECIFIC" in pathway:
        return "Specific factual claim lacks any supporting evidence in the text"
    
    if "NO_EVIDENCE_ASSUME_CONSISTENT" in pathway:
        return "No textual evidence found mentioning character in relevant context"
    
    if "STATE_CONFLICT" in pathway:
        if states["dead"]["count"] >= 2:
            return f"Character state contradicts claim: textual evidence shows character is dead ({states['dead']['count']} references), but claim describes active behavior"
        if states["paralyzed"]["count"] >= 2:
            return f"Physical state contradicts claim: character confirmed paralyzed in {states['paralyzed']['count']} passages, incompatible with claimed actions"
        if state_violations:
            return f"Character state makes claim impossible: {state_violations[0]}"
        return "Character state fundamentally contradicts claimed events"
    
    if "NLI_CONTRADICTION_FOUND" in pathway:
        avg_conf = sum(contradict_scores) / len(contradict_scores) if contradict_scores else 0
        if contradict_count >= 3:
            return f"Multiple contradictions found: {contradict_count} passages directly contradict claim with high confidence (avg {avg_conf:.2f})"
        elif contradict_count == 2:
            return f"Dual contradictory evidence: two separate passages refute the claim"
        else:
            return f"Direct textual contradiction: retrieved passage explicitly contradicts claim"
    
    if "CONTRADICTION_IGNORED_INTERPRETIVE" in pathway:
        cue_str = ", ".join(interpretive_cues[:2]) if interpretive_cues else "subjective terms"
        return f"Claim involves interpretive content ({cue_str}): textual contradictions ignored for subjective interpretation"
    
    if "NLI_SUPPORT_FOUND" in pathway:
        avg_conf = sum(support_scores) / len(support_scores) if support_scores else 0
        if support_count >= 3:
            return f"Strong textual support: {support_count} passages corroborate claim with high confidence (avg {avg_conf:.2f})"
        elif support_count == 2:
            return f"Corroborating evidence: multiple passages align with and support the claim"
        else:
            return f"Textual evidence supports claim: retrieved passage entails the statement"
    
    if "CONCRETE_EVENT_UNSUPPORTED" in pathway:
        cue_context = concrete_cues[0] if concrete_cues else "specific event/date"
        return f"Concrete claim lacks verification: specific event ({cue_context}) mentioned but no supporting textual evidence found across {evidence_count} relevant passages"
    
    if "NO_DECISIVE_EVIDENCE_ASSUME_CONSISTENT" in pathway:
        return f"Insufficient evidence for determination: {evidence_count} passages retrieved but none provide decisive support or contradiction"
    
    return "Unable to determine consistency from available evidence"

def check_consistency(target_character, claim_text, co_occurrence_index, book_name):
    pathway = ["START"]

    evidence = retrieve_evidence(
        target_character,
        claim_text,
        co_occurrence_index,
        book_name
    )
    pathway.append(f"RETRIEVAL_EXIT chunks={len(evidence)}")

    if not evidence:
        is_specific = is_specific_factual_claim(claim_text)
        
        if is_specific:
            pathway.append("NO_EVIDENCE_REJECT_SPECIFIC")
            rationale = generate_rationale(pathway, {}, 0, 0, 0, claim_text, [], [], [], [], [])
            return False, pathway, build_pathway_table(pathway), rationale
        else:
            pathway.append("NO_EVIDENCE_ASSUME_CONSISTENT")
            rationale = generate_rationale(pathway, {}, 0, 0, 0, claim_text, [], [], [], [], [])
            return True, pathway, build_pathway_table(pathway), rationale

    states = aggregate_states(evidence, target_character)
    state_violation, violations = violates_state(claim_text, states)

    nli_results = [nli_classify(claim_text, c["text"]) for c in evidence]
    support, contradict, neutral, support_scores, contradict_scores = nli_polarity(nli_results)
    
    is_interp, interp_cues = is_interpretive_claim(claim_text)
    is_concrete, concrete_cues = is_concrete_event(claim_text)

    if state_violation and contradict > 0:
        pathway.append("STATE_CONFLICT")
        rationale = generate_rationale(pathway, states, support, contradict, len(evidence), 
                                      claim_text, violations, interp_cues, concrete_cues,
                                      support_scores, contradict_scores)
        return False, pathway, build_pathway_table(pathway), rationale

    if contradict > 0:
        if is_interp:
            pathway.append("CONTRADICTION_IGNORED_INTERPRETIVE")
            rationale = generate_rationale(pathway, states, support, contradict, len(evidence),
                                          claim_text, violations, interp_cues, concrete_cues,
                                          support_scores, contradict_scores)
            return True, pathway, build_pathway_table(pathway), rationale
        else:
            pathway.append("NLI_CONTRADICTION_FOUND")
            rationale = generate_rationale(pathway, states, support, contradict, len(evidence),
                                          claim_text, violations, interp_cues, concrete_cues,
                                          support_scores, contradict_scores)
            return False, pathway, build_pathway_table(pathway), rationale

    if support > 0:
        pathway.append("NLI_SUPPORT_FOUND")
        rationale = generate_rationale(pathway, states, support, contradict, len(evidence),
                                      claim_text, violations, interp_cues, concrete_cues,
                                      support_scores, contradict_scores)
        return True, pathway, build_pathway_table(pathway), rationale

    if is_concrete:
        pathway.append("CONCRETE_EVENT_UNSUPPORTED")
        rationale = generate_rationale(pathway, states, support, contradict, len(evidence),
                                      claim_text, violations, interp_cues, concrete_cues,
                                      support_scores, contradict_scores)
        return False, pathway, build_pathway_table(pathway), rationale

    pathway.append("NO_DECISIVE_EVIDENCE_ASSUME_CONSISTENT")
    rationale = generate_rationale(pathway, states, support, contradict, len(evidence),
                                  claim_text, violations, interp_cues, concrete_cues,
                                  support_scores, contradict_scores)
    return True, pathway, build_pathway_table(pathway), rationale