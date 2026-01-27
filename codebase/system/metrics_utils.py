"""
Safe Metrics Registration Utility
Prevents duplicate metric registration across architectures
"""

from prometheus_client import REGISTRY, Counter, Histogram, Gauge

def get_or_create_metric(metric_type, name, *args, **kwargs):
    """
    Get existing metric or create new one if it doesn't exist.
    Prevents ValueError: Duplicated timeseries in CollectorRegistry
    """
    # Check if metric already exists
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    
    # Create new metric
    return metric_type(name, *args, **kwargs)

def safe_counter(name, *args, **kwargs):
    """Safely register a Counter metric"""
    return get_or_create_metric(Counter, name, *args, **kwargs)

def safe_histogram(name, *args, **kwargs):
    """Safely register a Histogram metric"""
    return get_or_create_metric(Histogram, name, *args, **kwargs)

def safe_gauge(name, *args, **kwargs):
    """Safely register a Gauge metric"""
    return get_or_create_metric(Gauge, name, *args, **kwargs)

def create_namespaced_metric(metric_type, base_name, namespace, *args, **kwargs):
    """
    Create a namespaced metric to avoid conflicts.
    Example: "arifos_verdicts_total" becomes "arifos_v2_verdicts_total"
    """
    namespaced_name = f"{namespace}_{base_name}"
    return metric_type(namespaced_name, *args, **kwargs)
