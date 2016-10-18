from unittest.mock import MagicMock
from stripe.error import CardError


def patch_stripe(p, success=True):
    p.stripe = mock_stripe(success)


def mock_stripe(success=True):
    stripe = MagicMock()

    if success:
        stripe.Charge.create = MagicMock(return_value=True)
    else:
        stripe.Charge.create = MagicMock(side_effect=CardError(message='testing', param='123', code='100500'))

    return stripe
