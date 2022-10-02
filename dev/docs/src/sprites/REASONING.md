### Reasoning

In older versions of 2dmc we had a master list for every type of drawable "sprite" (particles, chunks, ect)
When we wanted to draw, we would some code similar to the following:

```python
for sprite in a_list_of_sprites:
    sprite.draw()
```

One issue we encountered whilst developing with this system was that we often needed sprites of the same kind to be drawn above / behind each other.
This isn't easily doable with the previous system, which led to a lot of janky code with singlular sprites being assigned to variables and lots of weird if checks and it was basically a massive mess.
We also had the issue where if we wanted to reorder the way sprites were drawn we would have to manually go through and change the position of every related draw call.
Not good.

Thus, we decided to implement a new system.
