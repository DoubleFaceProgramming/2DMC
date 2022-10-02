# Layers Enum

The layers enum is what defines the order and number of onscreen layers.
It is defined like so:

```python
class LayersEnum(enum.Enum):
    ONE = enum.auto()
    TWO = enum.auto()
    ...
    SEVEN_BILLION_FOUR_HUNDRED_AND_TWENTY_FIVE_MILLION_ONE_HUNDRED_AND_THIRTY_TWO_THOUSAND_FIVE_HUNDRED_AND_ONE = enum.auto()
```

The beauty of this is that adding a new layer is as simple as choosing a name and adding it in!

It also makes it really easy to re-arrange the ordering of layers (tip: use Alt ↑ / Alt ↓ if you are using VSCode!)
