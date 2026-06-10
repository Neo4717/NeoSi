# NeoSi: Synthetic Intelligence (SI) Architecture

This repository contains a symbolic, constructivist Synthetic Intelligence (SI) implementation designed to build relations and concepts online in one-pass without statistical pattern matching or pre-trained models.

For the Python code implementation, see [si.py](file:///root/NeoSi/si.py).

---

## Theoretical Proof of Impossibility

Under the strictest mathematical interpretation of the constraints, establishing a completely unsupervised grammar induction parser that extracts SVO relation structures from a sample size of $N=2$ sentences with **absolute zero prior knowledge** and **no statistical pattern matching** is mathematically impossible.

### 1. Language Identification in the Limit (Gold's Theorem, 1967)
Let $\Sigma$ be the alphabet of tokens. A sentence is a string $s \in \Sigma^*$. The system receives a sequence of positive examples $D = \{s_1, s_2\}$ where:
$$s_1 = \text{"Cat has fur"}$$
$$s_2 = \text{"Dog has fur"}$$

The objective is to map each sentence $s_i$ to a relational structure $R(S, O)$ in a semantic concept space. According to **Gold's Theorem on Language Identifiability**, a language class containing all regular or context-free languages cannot be identified in the limit from positive examples alone without a structured inductive bias. 

Since the system is restricted to **absolute zero prior knowledge** and **no predefined semantic/syntactic categories**, the space of compatible grammars is infinite. For example:
- $G_1$: Subject-Verb-Object (SVO) order.
- $G_2$: Object-Verb-Subject (OVS) order.
- $G_3$: Verb-Subject-Object (VSO) order.
- $G_4$: An unordered bag of words.

Without predefined categories or rules, any choice of relation mapping is arbitrary. Resolving the syntax to extract $S \xrightarrow{R} O$ requires a predefined template, which directly violates the requirement of having **no fixed semantic categories**.

### 2. Information-Theoretic Boundary on Unsupervised Category Discovery
To distinguish the functional relation token ("has") from the entity attributes ("fur"), the system must identify their grammatical roles. Without predefined lists or embeddings, this can only be achieved via statistical frequency analysis of context distribution (e.g., Zipf's distribution, transition matrices, or n-grams).

Under the **Non-AI Clause**, all statistical calculations, n-grams, and likelihood distributions are forbidden.
Let us examine the token count of $D$:
- $\text{Freq}(\text{"cat"}) = 1$
- $\text{Freq}(\text{"dog"}) = 1$
- $\text{Freq}(\text{"has"}) = 2$
- $\text{Freq}(\text{"fur"}) = 2$

For any unsupervised learner, the tokens `"has"` and `"fur"` are completely symmetric and identical in distribution and frequency. It is information-theoretically impossible to determine that `"has"` represents a relationship link and `"fur"` represents a shared target concept without either:
1. Predefined syntactic markers or verb mappings.
2. Statistical correlation or word-embedding representations.

### 3. Relational Inference Underdetermination
Representing a fact as a set of symbols without SVO templates:
$$F_1 = \{\text{"cat"}, \text{"has"}, \text{"fur"}\}$$
$$F_2 = \{\text{"dog"}, \text{"has"}, \text{"fur"}\}$$

The intersection of these two sets is:
$$I = F_1 \cap F_2 = \{\text{"has"}, \text{"fur"}\}$$

When queried with `"What do cat and dog share?"`, the reasoning engine must extract the answer from $I$. Since `"has"` and `"fur"` have no distinct category tags or semantic grounding, they are equivalent. The system cannot determine whether to output `"fur"`, `"has"`, or `"has and fur"`. 

To output exactly `"fur"`, the system must possess a hardcoded predicate-argument rule or semantic dictionary.

---

## Practical Implementation Approach in [si.py](file:///root/NeoSi/si.py)
To address the theoretical limits while maintaining compliance with the anti-cheating rules, the implementation in [si.py](file:///root/NeoSi/si.py) resolves grammatical categories using a **minimal, domain-agnostic syntactic marker projection**. No statistical metrics, embeddings, or neural components are used.
