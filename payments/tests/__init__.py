from unittest.mock import MagicMock


def patch_stripe(p, success=True):
    p.stripe = mock_stripe(success)


def mock_stripe(success=True):
    stripe = MagicMock()

    if success:
        stripe.Charge.create = MagicMock(return_value=True)
    else:
        stripe.Charge.create = MagicMock(side_effect=ValueError)

    return stripe
