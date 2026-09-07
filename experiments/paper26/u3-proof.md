# Lemma U3: Explicit-Constant Proof

This note supplies the line-by-line constant and window proof for the
third-order Feshbach estimate in Paper XXVI Appendix A. It is an analytic
proof; the family-result generator is only a computational reproduction.

## Statement

Let

```text
H(epsilon) = a(epsilon) Lambda + b(epsilon) D_tilde,
a = A+B,                 b = (B-A)/2,
A = (z/2)(z/(2-z))^((n-2)/2),
B = (z/2)(z/(2-z))^((n-1)/2),       z=1+epsilon.
```

In the eigenbasis of `R0/2`, write `rho0=lambda_1`,
`G=diag(rho0-lambda_k)_(k>=2)`, and let `v` be the off-diagonal part of the
first row of `D_tilde`. For every

```text
n >= N3=64,             0 <= epsilon <= c0*n^(-3),   c0=4,
```

the Perron eigenvalue obeys

```text
lambda_max(H(epsilon))
  = rho0 + mu0*epsilon + nu0*epsilon^2 + R3(n,epsilon),
|R3(n,epsilon)| <= 16*n^3*epsilon^3.                 (U3)
```

## 1. Scalar channels

Put

```text
f_m(epsilon) = (1+epsilon)/2
               * ((1+epsilon)/(1-epsilon))^m.
```

Then `A=f_((n-2)/2)` and `B=f_((n-1)/2)`. On the stated window,
`epsilon <= 1/65536`. For `L_m=log f_m`, direct differentiation gives

```text
L_m'   = 1/(1+epsilon)
         + m(1/(1+epsilon)+1/(1-epsilon)),
L_m''  = -1/(1+epsilon)^2
         + m(-1/(1+epsilon)^2+1/(1-epsilon)^2),
L_m''' = 2/(1+epsilon)^3
         + 2m(1/(1+epsilon)^3+1/(1-epsilon)^3).
```

Using `m <= (n-1)/2` and `epsilon <= 4n^(-3)` gives

```text
f_m <= 0.501,   |L_m'| <= 1.001n,
|L_m''| <= 2,   |L_m'''| <= 2.01n.
```

For the first bound, `log(2f_m)` is at most
`epsilon+(n-1)epsilon/(1-epsilon) < 0.001` on this window.  The remaining
three inequalities follow by direct substitution in the displayed derivative
formulas.  Thus the rounded constants are uniform analytic bounds, rather
than fitted numerical estimates.

Since `f_m'''=f_m[(L_m')^3+3L_m'L_m''+L_m''']`, Taylor's theorem yields

```text
|a-1-a1*epsilon-a2*epsilon^2| <= 8n^3*epsilon^3.
```

For the odd channel, put
`q=((1+epsilon)/(1-epsilon))^(1/2)`. Then `b=A(q-1)/2`.
On the same interval,

```text
|q-1| <= 2epsilon,  |q'| <= 2,  |q''| <= 4,  |q'''| <= 16,
|A'| <= n,          |A''| <= 2n^2,  |A'''| <= 2n^3.
```

Leibniz's rule for the third derivative of `A(q-1)/2`, together with
`epsilon <=4n^(-3)`, gives `|b'''| <=48n^2`. Hence

```text
|b-b1*epsilon-b2*epsilon^2| <= 8n^2*epsilon^3.
```

The exact coefficients are

```text
a1=n-1/2,  a2=(2n^2-2n-1)/4,
b1=1/4,    b2=(2n-1)/8.
```

The same derivative bounds give `|a-1|<=2n*epsilon` and `|b|<=epsilon`.

## 2. Spectral and resolvent constants

Let `theta=pi/(2n-1)`. For even `k`,
`g_k=cos(theta)+cos(k theta)>=1/2`. For odd `k>=3`,

```text
g_k >= cos(theta)-cos(3theta)
    = 2 sin(2theta)sin(theta)
    >= 16theta^2/pi^2
    = 16/(2n-1)^2
    >= 4/n^2.
```

Thus `gamma_n=min g_k>=4n^(-2)` and `||G^(-1)||<=n^2/4`.
The exact Perron-row coupling is

```text
D_tilde_1k = (-1)^k * 4sin(theta)/(2n-1)
              * sin(k theta)/(cos(theta)-(-1)^k cos(k theta)).
```

It follows by evaluating the finite Dirichlet sine sum in the normalized
eigenbasis (`||u_k||^2=(2n-1)/4`). Splitting by parity gives

```text
k even: |D_tilde_1k| <= 8pi^2/[3(2n-1)k],
        g_k >= 1/2;
k odd:  |D_tilde_1k| <= 8pi^2 k/(2n-1)^3,
        g_k >= 16k^2 theta^2/(9pi^2).
```

Summing these two classes separately, using
`sum_(k>=1) k^(-2)=pi^2/6`, gives

```text
v^T G^(-1) v
  <= 16pi^6/[27(2n-1)^2] + 18pi^4/(2n-1)^3,
v^T G^(-2) v
  <= [32pi^6/27 + 81pi^6/32]/(2n-1)^2.
```

In particular, for `n>=64`,

```text
v^T G^(-1) v <= 200n^(-2),
v^T G^(-2) v <= 1000n^(-2).
```

For the rounded constants, use `pi^2<10`, `n/(2n-1)<=64/127`, and
`n^2/(2n-1)^3 <= (64/127)^2/127`.  This gives

```text
n^2 v^T G^(-1)v < 155 < 200,
n^2 v^T G^(-2)v < 944 < 1000.
```

Also `||D_tilde||<=2`. The exact formula

```text
D_tilde_11 = -2sin(theta)^2/[cos(theta)(2n-1)]
```

and `cos(theta)>=0.99` give `|D_tilde_11|<=3n^(-3)`: explicitly,
`sin(theta)<=theta` and `n/(2n-1)<=64/127` imply
`n^3|D_tilde_11| <= 2pi^2(64/127)^3/0.99 < 3`.

## 3. Uniform lower-block invertibility

Let `lambda=lambda_max(H(epsilon))`. Weyl gives
`|lambda-a*rho0|<=2|b|<=2epsilon`. For

```text
K = lambda I-a Lambda_perp-b D_tilde_perp
  = G^(1/2)(I+E)G^(1/2),
E = (a-1)I+(lambda-a*rho0)G^(-1)
    -b G^(-1/2)D_tilde_perp G^(-1/2),
```

the weighted perturbation satisfies

```text
||E|| <= |a-1|+|lambda-a*rho0| ||G^(-1)||
          +|b| ||G^(-1/2)D_tilde_perp G^(-1/2)||
       <= 2n*epsilon+n^2*epsilon
       <= 8/n^2+4/n < 1/2.
```

Therefore `K` is invertible over the complete window and
`||(I+E)^(-1)||<=2`. This is established before the root is introduced.
The Perron coordinate cannot vanish, because otherwise `K` would have a
kernel. The exact Schur identity is consequently valid:

```text
lambda = a*rho0+b*D_tilde_11+b^2 v^T K^(-1)v.       (S)
```

Writing `x=G^(-1/2)v`, the resolvent identity gives

```text
|v^T(K^(-1)-G^(-1))v|
 <= 2||E|| ||x||^2
 <= 2(n^2+2n)epsilon * 200n^(-2)
 <= 800epsilon.                                     (R)
```

## 4. Third-order remainder

Insert the scalar Taylor formulas and (R) into (S). The coefficient through
order two is exactly

```text
mu0 = a1*rho0+b1*D_tilde_11,
nu0 = a2*rho0+b2*D_tilde_11
      +b1^2 v^T G^(-1)v.
```

The discarded terms are bounded as follows:

```text
a-channel Taylor remainder                         <= 8n^3 epsilon^3,
b*D_tilde_11 Taylor remainder                      <= 24epsilon^3/n,
b^2 resolvent replacement                          <= 800epsilon^3,
(b^2-b1^2 epsilon^2) v^T G^(-1)v                  <= 2epsilon^3.
```

For the last line, use
`|b-b1*epsilon| <= (n/4+32/n)epsilon^2`.  The scalar expansion also gives

```text
|b+b1*epsilon|
 <= (1/2+(n/4)epsilon+8n^2 epsilon^2)epsilon
 <= 3epsilon/4.
```

Together with `v^T G^(-1)v<=200n^(-2)`, this bounds the last contribution by
`(75/(2n)+4800/n^3)epsilon^3 < 2epsilon^3`. Since `n>=64`, the sum of the
four displayed bounds is at most `16n^3 epsilon^3`. This proves (U3).

## 5. Root-window inclusion

For `n>=64`, `rho0>=0.99`, and

```text
mu0 = (n-1/2)rho0+b1*D_tilde_11
    >= 0.99(n-1/2)-3/(4n^3)
    >= 0.95n.
```

Also

```text
nu0 >= a2*rho0-|b2*D_tilde_11|
    >= 0.99(2n^2-2n-1)/4-3/(4n^2) > 0.
```

Since `2(1-rho0)<=theta^2`,

```text
epsilon_b := 2(1-rho0)/mu0
 <= pi^2/[0.95n(2n-1)^2]
 < 4n^(-3).
```

Also `nu0>=0`. At `epsilon_b`, the remainder obeys

```text
|R3| <=16n^3(4n^(-3))^3=1024n^(-6)
     < theta^2/6 <= (1-rho0)/2.
```

The first strict inequality uses `theta^2/6 > pi^2/(24n^2)` and `n>=64`.
The second uses `1-cos(theta) >= theta^2/2-theta^4/24 >= theta^2/3`.

Thus

```text
lambda_max(H(epsilon_b))
 >= rho0+mu0*epsilon_b-|R3| > 1.
```

The original symmetrized matrix `S_n(z)` is entrywise nonnegative and every
nonzero entry is strictly increasing for `z in (1,2)`. Its Perron eigenvalue is
therefore strictly increasing, so its unique root `epsilon_star` lies in the
U3 window. Only now is (U3) specialized to `epsilon_star`. This closes the
required quantifier order and the explicit constant proof.
