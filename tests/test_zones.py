import pytest
from simulation.distributed_city import Zone, DistributedCity
from simulation.city import Vehicle

def test_zone_contains():
    zone = Zone('test', xmin=0, xmax=10, ymin=0, ymax=10)
    inside = Vehicle('v1', (5, 5))
    outside = Vehicle('v2', (15, 5))
    assert zone.contains(inside) is True
    assert zone.contains(outside) is False

def test_get_zone_for_vehicle(tmp_path):
    # Creamos un YAML temporal
    zones_yaml = tmp_path / "zones.yaml"
    zones_yaml.write_text("""
zones:
  - name: alpha
    xmin: 0
    xmax: 100
    ymin: 0
    ymax: 100
  - name: beta
    xmin: 100
    xmax: 200
    ymin: 0
    ymax: 100
""")
    city = DistributedCity(str(zones_yaml))
    v_alpha = Vehicle('v1', (50, 50))
    v_beta  = Vehicle('v2', (150, 50))

    assert city.get_zone_for_vehicle(v_alpha).name == 'alpha'
    assert city.get_zone_for_vehicle(v_beta).name  == 'beta'
