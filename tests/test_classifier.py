from types import SimpleNamespace

from waste_sorter.classifier import classify_with_threshold


def test_low_confidence_becomes_unknown():
    fake = SimpleNamespace(predict=lambda image: ("plastic", 0.42))
    assert classify_with_threshold(fake, object(), 0.7) == ("unknown", 0.42)


def test_confident_prediction_is_kept():
    fake = SimpleNamespace(predict=lambda image: ("paper", 0.91))
    assert classify_with_threshold(fake, object(), 0.7) == ("paper", 0.91)
