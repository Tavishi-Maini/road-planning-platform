def format_cost_lakhs_as_cr(value):
    """
    Convert lakhs to crores.
    Example:
    30380.74 lakhs -> ₹303.81 Cr
    """
    return f"₹{value / 100:,.2f} Cr"