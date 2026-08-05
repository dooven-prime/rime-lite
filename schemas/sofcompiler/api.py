"""Stable Python facade for the Paper X compiler contract implementation."""

from .validate_examples import (
    compile_output_v1,
    compile_v1,
    ir_reference_errors,
    manifest_errors,
    profile_errors,
)

__all__ = [
    "compile_output_v1",
    "compile_v1",
    "ir_reference_errors",
    "manifest_errors",
    "profile_errors",
]
