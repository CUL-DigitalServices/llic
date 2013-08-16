#!/bin/bash
echo "llic:"
python -m timeit -s "import bench" "bench.llic_gen.generate_icalendar(1000)"

echo "icalendar:"
python -m timeit -s "import bench" "bench.ical_gen.generate_icalendar(1000)"

echo "stupid:"
python -m timeit -s "import bench" "bench.stupid_gen.generate_icalendar(1000)"
