"""Calculate and store collections of k-mer signatures."""

from .base import KmerSignature
from .kmers import KmerSpec
from .meta import SignaturesMeta
from .array import SignatureArray, SignatureList, sigarray_eq
