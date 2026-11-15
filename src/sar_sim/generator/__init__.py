"""Generator package: scenario generation for SAR mission planning."""

from sar_sim.generator.orbit import (
    kepler_to_eci,
    propagate_orbit,
    solve_kepler,
    MU_EARTH,
)
from sar_sim.generator.target import (
    lat_lon_to_ecef,
    make_targets,
    EARTH_EQUATORIAL_RADIUS,
)
from sar_sim.generator.visibility import (
    find_visibility_windows,
    visibility_matrix,
    satellite_to_target_vector,
    _check_geometric_constraints,
)
from sar_sim.generator.scenario import (
    sun_synchronous_orbit,
    random_satellites,
    generate_scenario,
)
