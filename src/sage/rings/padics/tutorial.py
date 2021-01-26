r"""
Introduction to the `p`-adics
==========================================

This tutorial outlines what you need to know in order to use
`p`-adics in Sage effectively.

Our goal is to create a rich structure of different options that
will reflect the mathematical structures of the `p`-adics.
This is very much a work in progress: some of the classes that we
eventually intend to include have not yet been written, and some of
the functionality for classes in existence has not yet been
implemented. In addition, while we strive for perfect code, bugs
(both subtle and not-so-subtle) continue to evade our clutches. As
a user, you serve an important role. By writing non-trivial code
that uses the `p`-adics, you both give us insight into what
features are actually used and also expose problems in the code for
us to fix.

Our design philosophy has been to create a robust, usable interface
working first, with simple-minded implementations underneath. We
want this interface to stabilize rapidly, so that users' code does
not have to change. Once we get the framework in place, we can go
back and work on the algorithms and implementations underneath. All
of the current `p`-adic code is currently written in pure
Python, which means that it does not have the speed advantage of
compiled code. Thus our `p`-adics can be painfully slow at
times when you're doing real computations. However, finding and
fixing bugs in Python code is *far* easier than finding and fixing
errors in the compiled alternative within Sage (Cython), and Python
code is also faster and easier to write. We thus have significantly
more functionality implemented and working than we would have if we
had chosen to focus initially on speed. And at some point in the
future, we will go back and improve the speed. Any code you have
written on top of our `p`-adics will then get an immediate
performance enhancement.

If you do find bugs, have feature requests or general comments,
please email sage-support@groups.google.com or
roed@math.harvard.edu.

Terminology and types of `p`-adics
==========================================

To write down a general `p`-adic element completely would
require an infinite amount of data. Since computers do not have
infinite storage space, we must instead store finite approximations
to elements. Thus, just as in the case of floating point numbers
for representing reals, we have to store an element to a finite
precision level. The different ways of doing this account for the
different types of `p`-adics.

We can think of `p`-adics in two ways. First, as a
projective limit of finite groups:

.. MATH::

    \ZZ_p = \lim_{\leftarrow n} \ZZ/p^n\ZZ.

Secondly, as Cauchy sequences of rationals (or integers, in the
case of `\ZZ_p`) under the `p`-adic metric.
Since we only need to consider these sequences up to equivalence,
this second way of thinking of the `p`-adics is the same as
considering power series in `p` with integral coefficients
in the range `0` to `p-1`. If we only allow
nonnegative powers of `p` then these power series converge
to elements of `\ZZ_p`, and if we allow bounded
negative powers of `p` then we get `\QQ_p`.

Both of these representations give a natural way of thinking about
finite approximations to a `p`-adic element. In the first
representation, we can just stop at some point in the projective
limit, giving an element of `\ZZ/p^n\ZZ`. As
`\ZZ_p / p^n\ZZ_p \cong \ZZ/p^n\ZZ`, this
is equivalent to specifying our element modulo
`p^n\ZZ_p`.

The *absolute precision* of a finite approximation
`\bar{x} \in \ZZ/p^n\ZZ` to `x \in \ZZ_p`
is the non-negative integer `n`.

In the second representation, we can achieve the same thing by
truncating a series

.. MATH::

      a_0 + a_1 p + a_2 p^2 + \cdots

at `p^n`, yielding

.. MATH::

     a_0 + a_1 p + \cdots + a_{n-1} p^{n-1} + O(p^n).


As above, we call this `n` the absolute precision of our
element.

Given any `x \in \QQ_p` with `x \ne 0`, we
can write `x = p^v u` where `v \in \ZZ` and
`u \in \ZZ_p^{\times}`. We could thus also store an element
of `\QQ_p` (or `\ZZ_p`) by storing
`v` and a finite approximation of `u`. This
motivates the following definition: the *relative precision* of an
approximation to `x` is defined as the absolute precision
of the approximation minus the valuation of `x`. For
example, if
`x = a_k p^k + a_{k+1} p^{k+1} +
\cdots + a_{n-1} p^{n-1} + O(p^n)`
then the absolute precision of `x` is `n`, the
valuation of `x` is `k` and the relative precision
of `x` is `n-k`.

There are three different representations of `\ZZ_p`
in Sage and one representation of `\QQ_p`:

-  the fixed modulus ring

-  the capped absolute precision ring

-  the capped relative precision ring, and

-  the capped relative precision field.

Fixed Modulus Rings
-------------------

The first, and simplest, type of `\ZZ_p` is basically
a wrapper around `\ZZ/p^n\ZZ`, providing a unified
interface with the rest of the `p`-adics. You specify a
precision, and all elements are stored to that absolute precision.
If you perform an operation that would normally lose precision, the
element does not track that it no longer has full precision.

The fixed modulus ring provides the lowest level of convenience,
but it is also the one that has the lowest computational overhead.
Once we have ironed out some bugs, the fixed modulus elements will
be those most optimized for speed.

As with all of the implementations of `\ZZ_p`, one
creates a new ring using the constructor ``Zp``, and passing in
``'fixed-mod'`` for the ``type`` parameter. For example,

::

    sage: R = Zp(5, prec = 10, type = 'fixed-mod', print_mode = 'series')
    sage: R
    5-adic Ring of fixed modulus 5^10

One can create elements as follows::

    sage: a = R(375)
    sage: a
    3*5^3
    sage: b = R(105)
    sage: b
    5 + 4*5^2

Now that we have some elements, we can do arithmetic in the ring.

::

    sage: a + b
    5 + 4*5^2 + 3*5^3
    sage: a * b
    3*5^4 + 2*5^5 + 2*5^6

Floor division (//) divides even though the result isn't really
known to the claimed precision; note that division isn't defined::

    sage: a // 5
    3*5^2

::

    sage: a / 5
    Traceback (most recent call last):
    ...
    ValueError: cannot invert non-unit

Since elements don't actually store their actual precision, one can
only divide by units::

    sage: a / 2
    4*5^3 + 2*5^4 + 2*5^5 + 2*5^6 + 2*5^7 + 2*5^8 + 2*5^9
    sage: a / b
    Traceback (most recent call last):
    ...
    ValueError: cannot invert non-unit

If you want to divide by a non-unit, do it using the ``//``
operator::

    sage: a // b
    3*5^2 + 3*5^3 + 2*5^5 + 5^6 + 4*5^7 + 2*5^8 + 3*5^9

Capped Absolute Rings
---------------------

The second type of implementation of `\ZZ_p` is
similar to the fixed modulus implementation, except that individual
elements track their known precision. The absolute precision of
each element is limited to be less than the precision cap of the
ring, even if mathematically the precision of the element would be
known to greater precision (see Appendix A for the reasons for the
existence of a precision cap).

Once again, use ``Zp`` to create a capped absolute `p`-adic
ring.

::

    sage: R = Zp(5, prec = 10, type = 'capped-abs', print_mode = 'series')
    sage: R
    5-adic Ring with capped absolute precision 10

We can do similar things as in the fixed modulus case::

    sage: a = R(375)
    sage: a
    3*5^3 + O(5^10)
    sage: b = R(105)
    sage: b
    5 + 4*5^2 + O(5^10)
    sage: a + b
    5 + 4*5^2 + 3*5^3 + O(5^10)
    sage: a * b
    3*5^4 + 2*5^5 + 2*5^6 + O(5^10)
    sage: c = a // 5
    sage: c
    3*5^2 + O(5^9)

Note that when we divided by 5, the precision of ``c`` dropped.
This lower precision is now reflected in arithmetic.

::

    sage: c + b
    5 + 2*5^2 + 5^3 + O(5^9)

Division is allowed: the element that results is a capped relative
field element, which is discussed in the next section::

    sage: 1 / (c + b)
    5^-1 + 3 + 2*5 + 5^2 + 4*5^3 + 4*5^4 + 3*5^6 + O(5^7)

Capped Relative Rings and Fields
--------------------------------

Instead of restricting the absolute precision of elements (which
doesn't make much sense when elements have negative valuations),
one can cap the relative precision of elements. This is analogous
to floating point representations of real numbers. As in the reals,
multiplication works very well: the valuations add and the relative
precision of the product is the minimum of the relative precisions
of the inputs. Addition, however, faces similar issues as floating
point addition: relative precision is lost when lower order terms
cancel.

To create a capped relative precision ring, use ``Zp`` as before.
To create capped relative precision fields, use ``Qp``.

::

    sage: R = Zp(5, prec = 10, type = 'capped-rel', print_mode = 'series')
    sage: R
    5-adic Ring with capped relative precision 10
    sage: K = Qp(5, prec = 10, type = 'capped-rel', print_mode = 'series')
    sage: K
    5-adic Field with capped relative precision 10

We can do all of the same operations as in the other two cases, but
precision works a bit differently: the maximum precision of an
element is limited by the precision cap of the ring.

::

    sage: a = R(375)
    sage: a
    3*5^3 + O(5^13)
    sage: b = K(105)
    sage: b
    5 + 4*5^2 + O(5^11)
    sage: a + b
    5 + 4*5^2 + 3*5^3 + O(5^11)
    sage: a * b
    3*5^4 + 2*5^5 + 2*5^6 + O(5^14)
    sage: c = a // 5
    sage: c
    3*5^2 + O(5^12)
    sage: c + 1
    1 + 3*5^2 + O(5^10)

As with the capped absolute precision rings, we can divide,
yielding a capped relative precision field element.

::

    sage: 1 / (c + b)
    5^-1 + 3 + 2*5 + 5^2 + 4*5^3 + 4*5^4 + 3*5^6 + 2*5^7 + 5^8 + O(5^9)

Unramified Extensions
---------------------

One can create unramified extensions of `\ZZ_p` and
`\QQ_p` using the functions ``Zq`` and ``Qq``.

In addition to requiring a prime power as the first argument,
``Zq`` also requires a name for the generator of the residue field.
One can specify this name as follows::

    sage: R.<c> = Zq(125, prec = 20); R
    5-adic Unramified Extension Ring in c defined by x^3 + 3*x + 3

Eisenstein Extensions
---------------------

It is also possible to create Eisenstein extensions of `\ZZ_p`
and `\QQ_p`.  In order to do so, create the ground field first::

    sage: R = Zp(5, 2)

Then define the polynomial yielding the desired extension.::

    sage: S.<x> = ZZ[]
    sage: f = x^5 - 25*x^3 + 15*x - 5

Finally, use the ``ext`` function on the ground field to create the
desired extension.::

    sage: W.<w> = R.ext(f)

You can do arithmetic in this Eisenstein extension::

    sage: (1 + w)^7
    1 + 2*w + w^2 + w^5 + 3*w^6 + 3*w^7 + 3*w^8 + w^9 + O(w^10)

Note that the precision cap increased by a factor of 5, since the
ramification index of this extension over `\ZZ_p` is 5.

Lazy Rings and Fields
---------------------

The model for lazy elements is quite different from any of the
other types of `p`-adics. In addition to storing a finite
approximation, one also stores a method for increasing the
precision.

Lazy p-adic rings are created by the constructor :func:`ZpL`::

    sage: R = ZpL(5, print_mode="digits")
    sage: R
    5-adic Ring with lazy precision

Observe that the precision is not capped on `R`::

    sage: R.precision_cap()
    +Infinity

However, a default precision is settled. This is the precision
at which the element will be printed::

    sage: R.default_prec()
    20

One creates elements as usual::

    sage: a = R(17/42)
    sage: a
    ...00244200244200244201

    sage: R.random_element()  # random
    ...21013213133412431402

Here we notice that 20 digits (that is the default precision) are printed.
However, the computation model is designed in order to guarantee that more
digits of `a` are available on demand.
This feature is reflected by the fact that, when we ask for the precision
of `a`, the software answers `\infty`::

    sage: a.precision_absolute()
    +Infinity

Asking for more digits is achieved by the methods :meth:`at_precision_absolute`
and :meth:`at_precision_relative`::

    sage: a.at_precision_absolute(30)
    ...?244200244200244200244200244201

As a shortcut, one can use the operator ``@``::

    sage: a@30
    ...?244200244200244200244200244201

Of course, standard operations are supported::

    sage: b = R(42/17)
    sage: a + b
    ...03232011214322140002
    sage: a - b
    ...42311334324023403400
    sage: a * b
    ...00000000000000000001
    sage: a / b
    ...12442142113021233401
    sage: sqrt(a)
    ...20042333114021142101

We observe again that only 20 digits are printed but, as before,
more digits are available on demand::

    sage: sqrt(a)@30
    ...?142443342120042333114021142101

Checking equalities between lazy p-adics is a bit subtle can could
sometimes be puzzling at first glance.
Actually, when it is obvious (from the previous computations) that
the two sides of the equality are different, everything works well::

    sage: a == b
    False

On the contrary, when the two numbers we want to compare are indeed
equal, it is not possible to conclude after a finite amount of
computations. In this case, an error is raised::

    sage: a == sqrt(a)^2
    Traceback (most recent call last):
    ...
    PrecisionError: unable to decide equality; try to bound precision

and we are forced to check equality at some given finite precision
as follows::

    sage: a@20 == sqrt(a)^2
    True
    sage: a@100 == sqrt(a)^2
    True

Finally, note that checking equality may fail even when the two
operands are different but when the first different digit is beyond
the default precision::

    sage: b == b + 5^50
    Traceback (most recent call last):
    ...
    PrecisionError: unable to decide equality; try to bound precision

::

A quite interesting feature with lazy p-adics is the possibility to
create (in somes cases) self-referent numbers. Here is an example.
We first declare a new variable as follows::

    sage: x = R.selfref()
    sage: x
    ...?.0

We then use the method :meth:`set` to define `x` by writing down an equation
it satisfies::

    sage: x.set(1 + 5*x^2)

The variable `x` now contains the unique solution of the equation
`x = 1 + 5 x^2`::

    sage: x
    ...04222412141121000211

This works because the `n`-th digit of the right hand size of the
defining equation only involves the `i`-th digits of `x` with `i < n`
(this is due to the factor `5`).

As a comparison, the following does not work::

    sage: y = R.selfref()
    sage: y.set(1 + 3*y^2)
    sage: y
    ...?.0
    sage: y@20
    Traceback (most recent call last):
    ...
    RecursionError: definition looks circular

Self-referent definitions also work with systems of equations::

    sage: u = R.selfref()
    sage: v = R.selfref()
    sage: w = R.selfref()

    sage: u.set(1 + 2*v + 3*w^2 + 5*u*v*w)
    sage: v.set(2 + 4*w + sqrt(1 + 5*u + 10*v + 15*w))
    sage: w.set(3 + 25*(u*v + v*w + u*w))

    sage: u
    ...31203130103131131433
    sage: v
    ...33441043031103114240
    sage: w
    ...30212422041102444403

"""
