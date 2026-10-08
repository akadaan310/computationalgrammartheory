# Mathematical typography tests

<p class="lede">This page renders the equations the book actually relies on. It is part of the build: if any formula here (or anywhere in the book) fails to parse, the build fails. Nothing falls back silently to raw LaTeX. Each formula is rendered at build time to HTML and to MathML for assistive technology.</p>

## Relational semantics and grammars

$$\sem{a_1 a_2 \cdots a_m} = \sem{a_1} \then \sem{a_2} \then \cdots \then \sem{a_m}, \qquad \sem{\varepsilon} = \mathrm{id}_A, \qquad \sem{\Lang} = \bigcup_{w \in \Lang} \sem{w}$$

$$G = (\Sigma, \Str, \sem{\cdot}, \Lang), \qquad \Lang \subseteq \Sigma^*, \qquad \sem{a} \subseteq A \times A$$

$$P \;\to\; E \mid E\,P \qquad\text{versus}\qquad P \;\to\; E \mid P\,P$$

## Aligned derivations

$$\begin{aligned}
\|T(x) - T(y)\|_1 &= \alpha\,\|M(x - y)\|_1 \\
&\le \alpha\,\|x - y\|_1 .
\end{aligned}$$

$$\begin{aligned}
\|x_{k-1} - \pi\|_1 &\le \|x_{k-1} - x_k\|_1 + \|x_k - \pi\|_1 \\
&\le r_k + \alpha\,\|x_{k-1} - \pi\|_1 \\
\Longrightarrow\quad \|x_k - \pi\|_1 &\le \frac{\alpha}{1-\alpha}\, r_k .
\end{aligned}$$

## Floors, shifts and nested scripts

$$f(x) = \Big\lfloor \frac{x}{2^{k}} \Big\rfloor \cdot 2^{j} + c, \qquad \dom f = [\,lo, hi\,], \qquad hi = \min_i \Big( \Big( \Big\lfloor \frac{n - c_i}{2^{j_i}} \Big\rfloor + 1 \Big) 2^{k_i} - 1 \Big)$$

$$\nu(w) = \operatorname{int}(1w), \qquad \operatorname{LCA}(u,v) = \nu' \gg \big(\msb(\nu'_u \oplus \nu'_v) + 1\big)$$

## Sums, limits, asymptotics, quantifiers

$$T_{\mathrm{total}} = T_{\mathrm{build}} + \sum_{i=1}^{Q} T_{\mathrm{query},i} + \sum_{j=1}^{U} T_{\mathrm{update},j}, \qquad Q^{*} = \frac{B}{q_0 - q_1}$$

$$\lim_{m \to \infty} \frac{1}{m}\Big(m + 4\big(2^{\lceil \log_2 m \rceil} - 1\big)\Big) \text{ does not exist, but } \limsup = 9$$

$$\forall x \in [1, n] :\; \sem{w}(x) \neq \varnothing \iff lo \le x \le hi, \qquad \log_2 \#\{\text{posets on } [n]\} \sim \frac{n^2}{4}$$

$$\Theta(n^2),\; \Oh(n \log n),\; \Omega\big(\tfrac{n}{w}\big),\; o(n^2),\; \omega(n m)$$

## Matrices and vectors

$$M = \begin{pmatrix} 0 & 0 & 1 & \tfrac{1}{4} \\ \tfrac12 & 0 & 0 & \tfrac14 \\ \tfrac12 & 1 & 0 & \tfrac14 \\ 0 & 0 & 0 & \tfrac14 \end{pmatrix}, \qquad \pi = \alpha M \pi + (1 - \alpha)\, v, \qquad \mathbf{1}^{\top} \pi = 1$$

## Sets, functions, blackboard and calligraphic letters

$$\mathcal{F} \subseteq \{\, f : \N \rightharpoonup \N \,\}, \qquad \Z_N, \;\; \R_{\ge 0}, \;\; \mathcal{K}, \;\; \mathfrak{A}, \qquad \Ppoly, \;\; \NP \subseteq \Ppoly \Rightarrow \PH = \Sigma_2^{\mathsf{p}}$$

## A deliberately long equation (overflow behavior)

$$\sem{w}(x) = \Big(\Big(\Big(\Big(\Big(x \gg k_1\Big) \ll j_1\Big) \mid c_1\Big) \gg k_2\Big) \ll j_2\Big) \mid c_2 \quad\text{whenever}\quad 2^{\max(k_1,k_2)} \le x \le \min\big(T_1, T_2, T_3, T_4, T_5, T_6, T_7, T_8\big) \text{ and every intermediate numeral lies in } [1, n]$$

## Inline mathematics

The bound $\|x_k - \pi\|_1 \le 2\alpha^k$, the set $\{\,w \in \{L,R,U\}^* : \sem{w}(x) \ne \varnothing\,\}$, the product $A \times Q$ of size at most $|Q| \cdot n$, and the cost $\lceil (h+1)/w \rceil$ must render inline without disturbing line spacing.
