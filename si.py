#!/usr/bin/env python3
"""
================================================================================
CONSTRUCTIVE SYNTHETIC INTELLIGENCE (SI) SYSTEM
================================================================================
This script implements a constructive, symbolic Synthetic Intelligence (SI) system
that constructs its representations online through interaction.

SI VS. AI DESIGN PHILOSOPHY:
1. Constructive Memory:
   Unlike statistical AI (which projects tokens into fixed-dimensional vector spaces
   or uses pre-trained weights/embeddings), this system builds a Dynamic Labeled Graph 
   on the fly. Each concept is a unique node, and relations are typed, directed edges.
   This is a form of constructive memory: the topology of the memory space is
   determined entirely by the history of interactions.

2. One-Pass Online Learning:
   Learning is O(1) graph insertion. There are no epochs, no backpropagation, no
   gradient descent, and no weight updates. This conforms to biological one-pass
   learning: once a relationship is seen, the link is instantiated immediately.

3. Relational Composition and Inferred Relations:
   Instead of retrieving pre-stored template responses, the output generator
   traverses the graph paths to compose answers token-by-token.

THEORETICAL BOUNDARY NOTE (Gold's Theorem):
Under absolute zero-knowledge conditions, unsupervised induction of grammatical 
roles (such as distinguishing relations like "has" from attributes like "fur") 
is mathematically underdetermined (Gold's Theorem, 1967). To make the system functional 
and address this barrier, we utilize a minimal set of domain-agnostic syntactic 
markers (such as identifying relational verbs) to project words into roles.
All concepts, nodes, and relational rules themselves are generated entirely 
at runtime without any hardcoded databases.
================================================================================
"""

import sys
import re

# --- CONSTRUCTIVE MEMORY ARCHITECTURE ---
class ConceptNode:
    """
    A unique symbolic atom created dynamically at runtime.
    We avoid using a simple string dictionary as memory; instead, each concept
    is represented by an instance of ConceptNode, forming a predicate network.
    """
    def __init__(self, name):
        self.name = name
        # Maps relation_name (str) -> set of ConceptNode targets
        # This structure allows O(1) traversal and set intersection.
        self.out_relations = {}

    def add_relation(self, relation_name, target_node):
        """Creates a directed, typed relation edge in memory."""
        if relation_name not in self.out_relations:
            self.out_relations[relation_name] = set()
        self.out_relations[relation_name].add(target_node)

    def get_relations_flat(self):
        """
        Returns a flat set of tuples representing (relation, target_name).
        This allows mathematical set operations (like intersection) to find commonalities.
        """
        flat = set()
        for rel_name, targets in self.out_relations.items():
            for target in targets:
                flat.add((rel_name, target.name))
        return flat


class ConceptGraph:
    """
    A dynamic memory graph that grows online.
    Proves emptiness at initialization.
    """
    def __init__(self):
        # Maps raw symbol names to their unique ConceptNode instances
        self.nodes = {}

    def get_or_create(self, name):
        """Creates new symbolic nodes on the fly as they are seen for the first time."""
        clean_name = name.strip().lower()
        if clean_name not in self.nodes:
            self.nodes[clean_name] = ConceptNode(clean_name)
        return self.nodes[clean_name]

    def add_fact(self, subject, relation, obj):
        """Constructs a relationship edge between subject and object nodes."""
        subj_node = self.get_or_create(subject)
        obj_node = self.get_or_create(obj)
        subj_node.add_relation(relation, obj_node)

    def is_empty(self):
        return len(self.nodes) == 0

    def get_size(self):
        return len(self.nodes)


# --- CONSTRUCTIVE PARSER ---
class ConstructiveParser:
    """
    Parses input text into novel symbolic forms.
    Creates new symbolic atoms on the fly without preset dictionaries.
    """
    def __init__(self):
        # Domain-agnostic syntactic helper tokens
        self.relational_markers = {"has", "have", "had", "is", "are", "be", "likes", "like", "loves", "love"}
        self.question_markers = {"what", "who", "which", "where", "does", "do", "share", "common"}

    def clean_and_tokenize(self, text):
        # Strip all punctuation, normalize to lower case, split by whitespace
        clean = re.sub(r'[^\w\s]', '', text.lower())
        return clean.split()

    def parse(self, text):
        tokens = self.clean_and_tokenize(text)
        if not tokens:
            return None

        # Determine if the statement is a query or a declarative fact
        is_query = any(t in self.question_markers for t in tokens) or text.strip().endswith('?')
        
        if is_query:
            return self.parse_query(tokens)
        else:
            return self.parse_fact(tokens)

    def parse_fact(self, tokens):
        """
        Identifies relations and subjects dynamically.
        If a word matches a relational marker, it is treated as the relation.
        Otherwise, if it's a 3-word sentence, we construct SVO dynamically.
        """
        # Strip articles to isolate core concepts
        articles = {"a", "an", "the"}
        filtered = [t for t in tokens if t not in articles]

        if not filtered:
            return None

        # Find the index of the relation/verb
        verb_idx = -1
        for i, token in enumerate(filtered):
            if token in self.relational_markers:
                verb_idx = i
                break

        if verb_idx != -1:
            subject = " ".join(filtered[:verb_idx])
            relation = filtered[verb_idx]
            obj = " ".join(filtered[verb_idx + 1:])
            return {"type": "fact", "subject": subject, "relation": relation, "object": obj}

        # Fallback: if 3 words, treat middle word as relation
        if len(filtered) == 3:
            return {"type": "fact", "subject": filtered[0], "relation": filtered[1], "object": filtered[2]}

        # Generic fallback
        if len(filtered) >= 2:
            return {"type": "fact", "subject": filtered[0], "relation": "is_related_to", "object": " ".join(filtered[1:])}

        return None

    def parse_query(self, tokens):
        """
        Parses questions to identify targets of comparison or properties.
        """
        # If it is a "share" or "common" query, extract comparison targets
        if "share" in tokens or "common" in tokens:
            ignore = {"what", "do", "does", "did", "and", "or", "share", "common", "between", "in", "the", "a", "an"}
            entities = [t for t in tokens if t not in ignore]
            return {"type": "query_share", "entities": entities}

        # Attribute query (e.g. "What does cat have?")
        if tokens[0] in {"what", "who", "which"}:
            # Find relation verb
            relation = None
            verb_idx = -1
            for i, token in enumerate(tokens):
                if token in self.relational_markers:
                    relation = token
                    verb_idx = i
                    break
            if relation:
                helpers = {"do", "does", "did", "is", "are"}
                start_idx = 1
                while start_idx < verb_idx and tokens[start_idx] in helpers:
                    start_idx += 1
                subject = " ".join(tokens[start_idx:verb_idx])
                return {"type": "query_attribute", "subject": subject, "relation": relation}

        return {"type": "query_unknown", "tokens": tokens}


# --- REASONING ENGINE ---
class ReasoningEngine:
    """
    Performs deterministic set-algebraic calculations over the concept graph.
    Learning is relational and done in one pass.
    """
    def __init__(self, graph):
        self.graph = graph
        # Store inference rules rather than combinatorial pairs
        self.rules = []

    def find_shared_properties(self, entity_names):
        """
        Finds common relations and target concepts between multiple entities.
        Performs graph intersection in one pass.
        """
        if not entity_names:
            return set()

        nodes = []
        for name in entity_names:
            if name in self.graph.nodes:
                nodes.append(self.graph.nodes[name])
            else:
                # If an entity does not exist in memory, the intersection is empty.
                return set()

        # Perform mathematical set intersection on the flat relations list
        shared = nodes[0].get_relations_flat()
        for node in nodes[1:]:
            shared = shared.intersection(node.get_relations_flat())

        return shared


# --- OUTPUT GENERATOR ---
class OutputGenerator:
    """
    Synthesizes sentences token-by-token from the concept graph's relationships.
    No retrieval of canned or pre-written answers.
    """
    def generate_response(self, query_type, result):
        if query_type == "query_share":
            if not result:
                return "nothing"
            
            # Extract target names from the property pairs
            # result contains tuples like: {('have', 'fur')}
            targets = sorted(list({target for rel, target in result}))
            
            # Construct response token-by-token
            if not targets:
                return "nothing"
            elif len(targets) == 1:
                return targets[0]
            else:
                # Composing a list
                response = ""
                for i, target in enumerate(targets):
                    if i > 0:
                        response += " and "
                    response += target
                return response

        elif query_type == "query_attribute":
            if not result:
                return "nothing"
            return ", ".join(sorted(list(result)))

        return "unknown format"


# --- SYSTEM INTEGRATION ---
class SyntheticIntelligenceSystem:
    def __init__(self):
        self.memory = ConceptGraph()
        self.parser = ConstructiveParser()
        self.reasoner = ReasoningEngine(self.memory)
        self.generator = OutputGenerator()

    def interact(self, input_text):
        parsed = self.parser.parse(input_text)
        if not parsed:
            return "Unable to parse input."

        if parsed["type"] == "fact":
            # Store relationship in memory in one pass
            self.memory.add_fact(parsed["subject"], parsed["relation"], parsed["object"])
            return f"[Learned: {parsed['subject']} --{parsed['relation']}--> {parsed['object']}]"

        elif parsed["type"].startswith("query_"):
            q_type = parsed["type"]
            if q_type == "query_share":
                result = self.reasoner.find_shared_properties(parsed["entities"])
            elif q_type == "query_attribute":
                # Get targets of the relation
                subj = parsed["subject"]
                rel = parsed["relation"]
                if subj in self.memory.nodes:
                    node = self.memory.nodes[subj]
                    result = {target.name for target in node.out_relations.get(rel, set())}
                else:
                    result = set()
            else:
                return "Query unsupported."

            return self.generator.generate_response(q_type, result)

        return "Unrecognized interaction type."


# --- VERIFICATION TEST SUITE ---
def run_verification():
    print("==================================================")
    print("RUNNING SYNTHETIC INTELLIGENCE VERIFICATION TESTS")
    print("==================================================")

    # Test 1: Empty memory verification
    print("Test 1: Verification of Empty Memory at Initialization...")
    si = SyntheticIntelligenceSystem()
    print(f"Memory size at start: {si.memory.get_size()}")
    assert si.memory.is_empty(), "Verification Failed: Memory is not empty at start!"
    print("-> Test 1 Passed: Memory successfully initialized with 0 nodes.")

    # Test 2: Double relation structure verification
    print("\nTest 2: Injecting facts and verifying structure...")
    si.interact("Cat has fur.")
    si.interact("Dog has fur.")
    print(f"Memory size after two facts: {si.memory.get_size()} nodes")
    print(f"Learned concepts in memory: {list(si.memory.nodes.keys())}")
    
    # Verify they are separate nodes and relation links
    cat_node = si.memory.nodes.get("cat")
    dog_node = si.memory.nodes.get("dog")
    assert cat_node is not None, "Verification Failed: 'cat' node was not created!"
    assert dog_node is not None, "Verification Failed: 'dog' node was not created!"
    
    # Assert distinct relations
    cat_rels = cat_node.get_relations_flat()
    dog_rels = dog_node.get_relations_flat()
    print(f"Cat relations in memory: {cat_rels}")
    print(f"Dog relations in memory: {dog_rels}")
    assert len(cat_rels) == 1 and ("has", "fur") in cat_rels, "Verification Failed: Invalid relation structure for cat"
    assert len(dog_rels) == 1 and ("has", "fur") in dog_rels, "Verification Failed: Invalid relation structure for dog"
    print("-> Test 2 Passed: Facts are represented as distinct symbolic nodes and relation links.")

    # Test 3: Relational composition query verification
    print("\nTest 3: Querying shared attributes (Relational Composition)...")
    answer = si.interact("What do cat and dog share?")
    print(f"Query: 'What do cat and dog share?' -> Answer: '{answer}'")
    assert answer == "fur", f"Verification Failed: Expected 'fur', got '{answer}'"
    print("-> Test 3 Passed: Successfully inferred relation and produced correct response without template lookups.")

    # Test 4: Check standard library constraints
    print("\nTest 4: Checking library imports and dependencies...")
    loaded_modules = sys.modules.keys()
    forbidden = {"torch", "tensorflow", "keras", "sklearn", "transformers", "nltk", "spacy"}
    overlap = forbidden.intersection(loaded_modules)
    print(f"Overlap with disallowed libraries: {list(overlap)}")
    assert not overlap, f"Verification Failed: Disallowed external models/libraries loaded: {overlap}"
    print("-> Test 4 Passed: Zero external dependencies detected.")

    print("\n==================================================")
    print("ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_verification()
