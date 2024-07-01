Common error resolution: How do I fix my smart meter reporting invalid dates?
=============================================================================

There are some rare cases of smart meters sending telegrams with a timestamp in the past or future.
This varies from several days to even months.

First, you will need to report this to the supplier responsible for (placing) your smart meter.
They might be able to fix it remotely or on site. Or even replace you meter completely (up to them to decide).

Until then, you can enable the "Override telegram timestamp" option in the datalogger configuration.

.. caution::

    **Be advised**: Do **not** enable this option to fix any **small timestamp offset** your smart meter has (let's say, up to a few minutes).
    As it's only meant as a last resort for the situation described above and may cause side effects.
