---
title: Notation and Conventions
status: definition
noexercises: true
description: The symbols, cost conventions and evidence labels used throughout the book.
---

## Sets, relations, words {#sec:notation-sets}

| Notation | Meaning |
|---|---|
| $[n]$ | $\{1, \dots, n\}$ (or $\{0, \dots, n-1\}$ where stated) |
| $\Sigma$, $\Sigma^*$, $\varepsilon$ | an alphabet of moves; all finite words over it; the empty word |
| $\lvert w \rvert$ | length of a word $w$ |
| $\pi_\Gamma(w)$ | projection of $w$ onto the letters in $\Gamma$ |
| $R \then S$ | relational composition: first $R$, then $S$ |
| $\Rel(A)$ | the relations on $A$ |
| $\sem{a}$, $\sem{w}$, $\sem{\Lang}$ | meaning of a move, a word, a language (Definition \ref{def:relsem}) |
| $\sem{w}(x) = \varnothing$ | $w$ is undefined at $x$ |
| $\dom f$ | domain of a partial map |
| $\Lang$ | an admissibility language |
| $D = (Q, \Sigma, \delta, q_0, F)$ | a deterministic automaton with partial $\delta$; $\lvert Q \rvert$ its number of states |
| $\Str = (A; R_1, \dots)$ | a computational structure |
| $G = (\Sigma, \Str, \sem{\cdot}, \Lang)$ | an operational grammar (Definition \ref{def:opgrammar}) |

## Numbers, bits, asymptotics {#sec:notation-numbers}

| Notation | Meaning |
|---|---|
| $w$ (in cost statements) | the machine word size in bits; context distinguishes it from a word $w \in \Sigma^*$ |
| $\lfloor x \rfloor$, $\lceil x \rceil$ | floor, ceiling |
| $x \gg k$, $x \ll k$ | shift right / left by $k$ bits |
| $x \oplus y$ | bitwise exclusive or |
| $\msb(x)$ | index of the most significant set bit ($\msb(0) = -1$) |
| $\lowbit(i)$ | $i \mathbin{\&} (-i)$, the lowest set bit |
| $\nu(w) = \operatorname{int}(1w)$ | the heap numeration of a binary address |
| $\Oh, \Omega, \Theta, o, \omega$ | asymptotic notation; the growing parameters are always named |
| $\|x\|_1$ | $L_1$ norm $\sum_i \lvert x_i \rvert$ |

## Cost conventions {#sec:notation-cost}

Costs are counted elementary steps in categories `read`, `write`, `compare`, `arith`, `pointer`, `hash`, `probe`, `alloc`, `edge`, `rule`. An arithmetic operation on a $b$-bit integer costs $\lceil b / 64 \rceil$ steps. The **unit** cost model weighs every category by one; other models are stated where used. A **cost profile** is $(T_{\mathrm{build}}, S, T_{\mathrm{query}}, T_{\mathrm{update}}, \lvert\mathrm{out}\rvert)$.

## Evidence labels {#sec:notation-evidence}

Proved here · Established · Adapted · Empirical · Conjecture · Rejected · Definition · Proposed — see §\ref{sec:evidence}. Ledger identifiers: `CGT-DEF` definition, `CGT-THM`/`PROP`/`COR` results, `CGT-CONJ` conjectures, `CGT-OBS` observations, `CGT-EXP` experiments, `CGT-NEG`/`REJ` negative results, `CGT-OPEN` open problems, `CGT-D` decisions, `CGT-H` hypotheses.
