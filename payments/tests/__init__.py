from unittest.mock import MagicMock


def mock_stripe(p, success=True):
    if success:
        p.stripe.Charge.create = MagicMock(return_value=True)
    else:
        p.stripe.Charge.create = MagicMock(side_effect=ValueError)
