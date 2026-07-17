"""DEPRECATED — arifosmcp has been renamed to arifos.

This package exists only to redirect users to the canonical package.
Please run: pip install arifos
"""
import warnings
warnings.warn(
    "arifosmcp is deprecated. Use 'pip install arifos' instead. "
    "This package will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)
