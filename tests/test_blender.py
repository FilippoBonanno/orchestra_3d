"""Run with Blender --background --factory-startup --python-exit-code 1 --python."""
import importlib.util
from pathlib import Path
import tempfile

import bpy
import bmesh

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "audit_stl", root / "skills/orchestra-3d/scripts/audit_stl.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def cube():
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=20)
    return bm


bm = cube()
result = audit.inspect_mesh(bm)
assert result['topology_pass'], result
assert result['dimensions_mm'] == [20, 20, 20], result
assert abs(result['shells'][0]['signed_volume_mm3'] - 8000) < 0.01
bm.free()

bm = cube()
bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm, geom=[bm.faces[0]], context='FACES_ONLY')
assert not audit.inspect_mesh(bm)['topology_pass'], 'Open mesh accepted'
bm.free()

bm = cube()
bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
result = audit.inspect_mesh(bm)
assert result['topology_pass'] and result['orientation_review_required'], result
assert not result['audit_pass'], 'Inward shell requires orientation review'
bm.free()

bm = cube()
bm.faces.ensure_lookup_table()
bmesh.ops.reverse_faces(bm, faces=[bm.faces[0]])
assert not audit.inspect_mesh(bm)['topology_pass'], 'Mixed winding accepted'
bm.free()

bm = cube()
verts = [bm.verts.new((x, 0, 0)) for x in (30, 31, 32)]
bm.faces.new(verts)
assert not audit.inspect_mesh(bm)['topology_pass'], 'Degenerate face accepted'
bm.free()

bm = bmesh.new()
assert not audit.inspect_mesh(bm)['topology_pass'], 'Empty mesh accepted'
bm.free()

bm = cube()
inner = bmesh.ops.create_cube(bm, size=10)
inner_verts = set(inner['verts'])
bmesh.ops.reverse_faces(bm, faces=[f for f in bm.faces if set(f.verts) <= inner_verts])
result = audit.inspect_mesh(bm)
assert result['topology_pass'] and len(result['shells']) == 2, result
assert result['orientation_review_required'], 'Cavity containment must be reviewed'
bm.free()

with tempfile.TemporaryDirectory(prefix='orchestra-3d-', dir=Path.cwd()) as folder:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 0.001
    bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'
    bpy.ops.mesh.primitive_cube_add(size=20)
    stl = Path(folder) / 'cube.stl'
    exported = bpy.ops.wm.stl_export(
        filepath=str(stl), export_selected_objects=True,
        global_scale=1.0, use_scene_unit=False,
        apply_modifiers=True, forward_axis='Y', up_axis='Z')
    assert exported == {'FINISHED'} and stl.stat().st_size > 84
    result = audit.audit_file(stl)
    assert result['topology_pass'], result
    assert all(abs(d - 20) < 0.0001 for d in result['dimensions_mm']), result
    assert len(result['shells']) == 1, result
    assert abs(result['shells'][0]['signed_volume_mm3'] - 8000) < 0.01
print('PASS: cube, invalid topology, winding review, nested cavity, STL mm roundtrip')
